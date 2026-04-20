#!/usr/bin/env python3
"""좀비파크 카드뉴스 일일 발행 파이프라인.

매일 18:00 KST GitHub Actions에서 실행.
파이프라인: 선택 → 텍스트 다듬기 → 이미지 생성 → 합성 → 업로드 → 발행 → 알림 → 로그

재시도 모드:
  RETRY_MODE=true 환경변수가 설정되면, failure_log.json을 분석하여
  이전 실패 원인에 맞는 우회 전략을 자동 적용한다.
"""

import sys
import os
import time
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
from src.logger import log_daily_publish, log_error, log_to_discord
from src.retry_strategy import log_failure, get_retry_strategy, mark_resolved

KST = timezone(timedelta(hours=9))


def _classify_error(error: Exception) -> str:
    """에러를 분류하여 error_type 문자열 반환."""
    msg = str(error).lower()
    if "503" in msg or "unavailable" in msg:
        return "api_503"
    if "429" in msg or "rate" in msg:
        return "api_rate_limit"
    if "timeout" in msg:
        return "api_timeout"
    if "json" in msg or "parse" in msg:
        return "parse_error"
    if "upload" in msg or "cloudinary" in msg:
        return "upload_fail"
    if "instagram" in msg or "graph api" in msg:
        return "instagram_api"
    return "unknown"


def _fallback_text_direct(content: dict) -> dict:
    """Gemini 완전 우회 — 원본 콘텐츠로 직접 폴백 텍스트 생성."""
    from src.image_generator import get_style_for_type
    content_type = content.get('type', '')
    type_style = get_style_for_type(content_type)

    slides = []
    for slide in content.get("slides", []):
        slides.append({
            "slide": slide.get("slide", 1),
            "text": slide.get("text", ""),
            "image_prompt": (
                f"{type_style}, "
                f"Instagram square 1:1, high contrast, "
                f"neon green and dark purple color scheme"
            )
        })

    return {
        "slides": slides,
        "caption": content.get("caption", f"{content.get('title', '좀비파크')}\n\n#좀비파크"),
        "hashtags": content.get("hashtags", [
            "#좀비파크", "#ZombiePark", "#영흥도", "#서바이벌",
            "#생존", "#좀비아포칼립스", "#생존체험"
        ])
    }


def run_daily_pipeline():
    """일일 카드뉴스 발행 전체 파이프라인."""
    dry_run = os.environ.get('DRY_RUN', 'false').lower() == 'true'
    is_retry = os.environ.get('RETRY_MODE', 'false').lower() == 'true'
    now = datetime.now(KST)

    # ─── 재시도 전략 확인 ───
    strategy = None
    if is_retry:
        strategy = get_retry_strategy()
        if not strategy["should_retry"]:
            print(f"\n🚫 재시도 중단: {strategy['reason']}")
            return False

    print(f"\n{'='*60}")
    print(f"  🧟 좀비파크 카드뉴스 일일 파이프라인")
    print(f"  📅 {now.strftime('%Y-%m-%d %H:%M KST')}")
    if dry_run:
        print(f"  🧪 드라이런 모드 — 실제 발행하지 않음")
    if is_retry and strategy:
        print(f"  🔄 재시도 모드 (시도 #{strategy['attempt']})")
        print(f"  📋 전략: {strategy['reason']}")
    print(f"{'='*60}\n")

    output_dir = "/tmp/zombiepark_cards"
    attempt = strategy["attempt"] if strategy else 1
    content_id = ""

    try:
        # ─── Step 1: 오늘의 콘텐츠 선택 ───
        print("📌 Step 1: 콘텐츠 선택")
        content = select_content()
        if not content:
            print("   ⚠️ 오늘 발행할 콘텐츠가 없습니다.")
            log_failure("selector", "no_content", "오늘 발행할 콘텐츠 없음", attempt=attempt)
            log_error("selector", "오늘 발행할 콘텐츠 없음")
            return False

        content_id = content.get("id", "unknown")
        title = content.get("title", "제목 없음")
        content_type = content.get("type", "")
        print(f"   ✅ 선택됨: [{content_id}] {title} ({content_type})")

        # ─── Step 2: AI 텍스트 다듬기 ───
        print("\n✏️ Step 2: AI 텍스트 생성")
        skip_gemini_text = strategy and strategy.get("skip_gemini_text")

        if skip_gemini_text:
            print("   ⏭️ 재시도 전략: Gemini 텍스트 생성 건너뜀 → 폴백 텍스트 직접 사용")
            enriched = _fallback_text_direct(content)
        else:
            try:
                enriched = generate_text(content)
            except Exception as e:
                error_type = _classify_error(e)
                log_failure("text_generator", error_type, str(e),
                           content_id=content_id, attempt=attempt)
                print(f"   ⚠️ 텍스트 생성 실패: {e}. 폴백 텍스트 사용.")
                enriched = _fallback_text_direct(content)

        slides = enriched.get("slides", [])
        caption = enriched.get("caption", "")
        hashtags = enriched.get("hashtags", [])

        if hashtags:
            caption += "\n\n" + " ".join(hashtags)

        print(f"   ✅ {len(slides)}장 슬라이드 + 캡션 준비 완료")

        # ─── Step 3: 마케터 에이전트 캡션 강화 ───
        print("\n💡 Step 3: 마케터 에이전트")
        skip_gemini_agent = strategy and strategy.get("skip_gemini_agent")

        if skip_gemini_agent:
            print("   ⏭️ 재시도 전략: 마케터 에이전트 건너뜀 → 원본 캡션 유지")
        else:
            try:
                slides_text = [s.get("text", "") for s in slides]
                content_with_caption = {**content, "caption": caption}
                enhanced = marketer_enhance(content_with_caption, slides_text)
                caption = enhanced.get("caption", caption)
            except Exception as e:
                log_failure("agent_enhancer", _classify_error(e), str(e),
                           content_id=content_id, attempt=attempt)
                print(f"   ⚠️ 마케터 에이전트 실패: {e}. 원본 캡션 유지.")

        print(f"   ✅ 캡션 강화 완료")

        # ─── Step 4: AI 이미지 생성 ───
        print("\n🎨 Step 4: AI 이미지 생성")
        try:
            raw_images = generate_images(slides, output_dir,
                                         content_type=content.get('type', ''))
        except Exception as e:
            log_failure("image_generator", _classify_error(e), str(e),
                       content_id=content_id, attempt=attempt)
            raise

        print(f"   ✅ {len(raw_images)}장 배경 이미지 생성")

        # ─── Step 5: 텍스트 오버레이 합성 ───
        print("\n🖼️ Step 5: 카드 합성")
        try:
            final_images = compose_all_cards(slides, raw_images, output_dir)
        except Exception as e:
            log_failure("composer", _classify_error(e), str(e),
                       content_id=content_id, attempt=attempt)
            raise

        if not final_images:
            log_failure("composer", "no_output", "카드 합성 결과 0장",
                       content_id=content_id, attempt=attempt)
            print("   ❌ 합성된 카드가 0장. 발행 중단.")
            log_error("composer", "카드 합성 결과 0장")
            return False
        print(f"   ✅ {len(final_images)}장 최종 카드 완성")

        # ─── Step 6: Telegram 미리보기 ───
        print("\n📱 Step 6: Telegram 미리보기")
        send_preview(content, final_images, caption)

        # ─── Step 7 ~ 9: 업로드 + 발행 + 결과 ───
        if dry_run:
            print("\n☁️ Step 7: Cloudinary 업로드 (드라이런 — 건너뜀)")
            print("\n📸 Step 8: Instagram 발행 (드라이런 — 건너뜀)")
            result = {"success": True, "post_id": "dry_run", "dry_run": True}
            print("\n📊 Step 9: 결과 처리")
            print(f"   ✅ 드라이런 완료! 실제 발행 없이 파이프라인 검증 성공.")
        else:
            # 재시도 전략: Instagram API 대기
            extra_wait = strategy.get("extra_wait_seconds", 0) if strategy else 0
            if extra_wait > 0:
                print(f"\n⏳ 재시도 전략: {extra_wait}초 대기 중...")
                time.sleep(extra_wait)

            print("\n☁️ Step 7: Cloudinary 업로드")
            try:
                uploaded = upload_images(final_images, content_id)
                image_urls = [u["url"] for u in uploaded if "error" not in u]
            except Exception as e:
                log_failure("uploader", _classify_error(e), str(e),
                           content_id=content_id, attempt=attempt)
                raise

            if not image_urls:
                log_failure("uploader", "upload_fail", "모든 이미지 업로드 실패",
                           content_id=content_id, attempt=attempt)
                print("   ⚠️ 업로드된 이미지 없음. 발행 중단.")
                log_error("uploader", "모든 이미지 업로드 실패")
                return False

            print(f"   ✅ {len(image_urls)}장 업로드 완료")

            # ─── Step 8: Instagram 발행 ───
            print("\n📸 Step 8: Instagram 발행")
            try:
                if len(image_urls) >= 2:
                    result = publish_carousel(image_urls, caption)
                else:
                    result = publish_single_image(image_urls[0], caption)
            except Exception as e:
                log_failure("publisher", _classify_error(e), str(e),
                           content_id=content_id, attempt=attempt)
                raise

            # ─── Step 9: 발행 결과 처리 ───
            print("\n📊 Step 9: 결과 처리")
            if result.get("success"):
                post_id = result.get("post_id", "")
                mark_as_published(content_id, post_id)
                print(f"   ✅ 발행 성공! Post ID: {post_id}")
            else:
                log_failure("publisher", "publish_fail",
                           result.get("error", "알 수 없는 발행 오류"),
                           content_id=content_id, attempt=attempt)
                print(f"   ❌ 발행 실패: {result.get('error', '')}")

        # Telegram 결과 알림
        send_publish_result(content_id, result)

        # Discord + performance_log 기록
        log_daily_publish(content_id, title, content_type, result)

        # 성공 시 오늘의 실패 기록을 해결됨으로 표시
        if result.get("success"):
            mark_resolved()

        success = result.get("success", False)

        print(f"\n{'='*60}")
        if success:
            if is_retry:
                print(f"  ✅ 재시도 성공! (시도 #{attempt})")
            else:
                print(f"  ✅ 파이프라인 완료!")
        else:
            print(f"  ❌ 파이프라인 실패")
        print(f"{'='*60}\n")

        return success

    except Exception as e:
        error_type = _classify_error(e)
        error_msg = str(e)
        print(f"\n❌ 파이프라인 에러: {error_msg}")

        # 실패 로그 기록
        log_failure("pipeline", error_type, error_msg,
                   content_id=content_id, attempt=attempt)
        log_error("pipeline", f"[시도 #{attempt}] {error_msg}")

        # 재시도 모드에서 Discord 알림
        if is_retry:
            log_to_discord(
                title=f"🔄 재시도 #{attempt} 실패",
                description=f"에러: {error_msg[:300]}",
                color=0xFF4500,
            )

        return False


if __name__ == "__main__":
    success = run_daily_pipeline()
    sys.exit(0 if success else 1)
