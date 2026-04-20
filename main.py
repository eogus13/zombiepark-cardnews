#!/usr/bin/env python3
"""좀비파크 카드뉴스 일일 발행 파이프라인.

매일 18:00 KST GitHub Actions에서 실행.
파이프라인: 선택 → 텍스트 다듬기 → 이미지 생성 → 합성 → 업로드 → 발행 → 알림 → 로그
"""

import sys
import os
from datetime import datetime, timezone, timedelta

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.selector import select_content, mark_as_published
from src.text_generator import generate_text
from src.image_generator import generate_images
from src.image_composer import compose_all_cards
from src.uploader import upload_images
from src.publisher import publish_carousel, publish_single_image
from src.reviewer import send_preview, send_publish_result
from src.agent_enhancer import marketer_enhance
from src.logger import log_daily_publish, log_error

KST = timezone(timedelta(hours=9))


def run_daily_pipeline():
    """일일 카드뉴스 발행 전체 파이프라인."""
    now = datetime.now(KST)
    print(f"\n{'='*60}")
    print(f"  🧟 좀비파크 카드뉴스 일일 파이프라인")
    print(f"  📅 {now.strftime('%Y-%m-%d %H:%M KST')}")
    print(f"{'='*60}\n")

    output_dir = "/tmp/zombiepark_cards"

    try:
        # ─── Step 1: 오늘의 콘텐츠 선택 ───
        print("📌 Step 1: 콘텐츠 선택")
        content = select_content()
        if not content:
            print("   ⚠️ 오늘 발행할 콘텐츠가 없습니다.")
            log_error("selector", "오늘 발행할 콘텐츠 없음")
            return False

        content_id = content.get("id", "unknown")
        title = content.get("title", "제목 없음")
        content_type = content.get("type", "")
        print(f"   ✅ 선택됨: [{content_id}] {title} ({content_type})")

        # ─── Step 2: AI 텍스트 다듬기 ───
        print("\n✏️ Step 2: AI 텍스트 생성")
        enriched = generate_text(content)
        slides = enriched.get("slides", [])
        caption = enriched.get("caption", "")
        hashtags = enriched.get("hashtags", [])

        # 해시태그를 캡션에 추가
        if hashtags:
            caption += "\n\n" + " ".join(hashtags)

        print(f"   ✅ {len(slides)}장 슬라이드 + 캡션 준비 완료")

        # ─── Step 3: 마케터 에이전트 캡션 강화 ───
        print("\n💡 Step 3: 마케터 에이전트")
        slides_text = [s.get("text", "") for s in slides]
        content_with_caption = {**content, "caption": caption}
        enhanced = marketer_enhance(content_with_caption, slides_text)
        caption = enhanced.get("caption", caption)
        print(f"   ✅ 캡션 강화 완료")

        # ─── Step 4: AI 이미지 생성 ───
        print("\n🎨 Step 4: AI 이미지 생성")
        raw_images = generate_images(slides, output_dir)
        print(f"   ✅ {len(raw_images)}장 배경 이미지 생성")

        # ─── Step 5: 텍스트 오버레이 합성 ───
        print("\n🖼️ Step 5: 카드 합성")
        final_images = compose_all_cards(slides, raw_images, output_dir)
        print(f"   ✅ {len(final_images)}장 최종 카드 완성")

        # ─── Step 6: Telegram 미리보기 ───
        print("\n📱 Step 6: Telegram 미리보기")
        send_preview(content, final_images, caption)

        # ─── Step 7: Cloudinary 업로드 ───
        print("\n☁️ Step 7: Cloudinary 업로드")
        uploaded = upload_images(final_images, content_id)
        image_urls = [u["url"] for u in uploaded if "error" not in u]

        if not image_urls:
            print("   ⚠️ 업로드된 이미지 없음. 발행 중단.")
            log_error("uploader", "모든 이미지 업로드 실패")
            return False

        print(f"   ✅ {len(image_urls)}장 업로드 완료")

        # ─── Step 8: Instagram 발행 ───
        print("\n📸 Step 8: Instagram 발행")
        if len(image_urls) >= 2:
            result = publish_carousel(image_urls, caption)
        else:
            result = publish_single_image(image_urls[0], caption)

        # ─── Step 9: 발행 결과 처리 ───
        print("\n📊 Step 9: 결과 처리")
        if result.get("success"):
            post_id = result.get("post_id", "")
            mark_as_published(content_id, post_id)
            print(f"   ✅ 발행 성공! Post ID: {post_id}")
        else:
            print(f"   ❌ 발행 실패: {result.get('error', '')}")

        # Telegram 결과 알림
        send_publish_result(content_id, result)

        # Discord + performance_log 기록
        log_daily_publish(content_id, title, content_type, result)

        print(f"\n{'='*60}")
        print(f"  {'✅ 파이프라인 완료!' if result.get('success') else '❌ 파이프라인 실패'}")
        print(f"{'='*60}\n")

        return result.get("success", False)

    except Exception as e:
        error_msg = f"파이프라인 예외: {str(e)}"
        print(f"\n❌ {error_msg}")
        log_error("pipeline", error_msg)
        return False


if __name__ == "__main__":
    success = run_daily_pipeline()
    sys.exit(0 if success else 1)
