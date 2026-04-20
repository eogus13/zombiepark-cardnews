"""Step 7: Telegram 리뷰 — 발행 전 미리보기 + 승인/거부 시스템"""

import os
import json
import asyncio
import requests
from pathlib import Path


def send_preview(content: dict, image_paths: list,
                 caption: str) -> dict:
    """Telegram으로 카드뉴스 미리보기 전송.

    자동 발행 모드에서는 미리보기만 전송하고 바로 발행.
    수동 승인 모드에서는 승인 대기 (별도 봇 필요).

    Args:
        content: 콘텐츠 dict (id, title, type 등)
        image_paths: 로컬 이미지 경로 리스트
        caption: 인스타그램 캡션

    Returns:
        {"sent": True/False, "message_ids": [...]}
    """
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')

    if not bot_token or not chat_id:
        print("   ⚠️ Telegram 설정 없음. 미리보기 건너뜀.")
        return {"sent": False, "error": "Telegram 미설정"}

    try:
        message_ids = []

        # 1) 텍스트 요약 전송
        summary = _build_summary(content, caption)
        msg_id = _send_message(bot_token, chat_id, summary)
        if msg_id:
            message_ids.append(msg_id)

        # 2) 카드 이미지 전송 (최대 10장 = Telegram media group 제한)
        if image_paths:
            photo_ids = _send_photos(bot_token, chat_id, image_paths[:10])
            message_ids.extend(photo_ids)

        # 3) 캡션 미리보기
        caption_preview = f"📝 *캡션 미리보기*\n\n{caption[:500]}"
        if len(caption) > 500:
            caption_preview += "\n...(이하 생략)"
        msg_id = _send_message(bot_token, chat_id, caption_preview)
        if msg_id:
            message_ids.append(msg_id)

        print(f"   📱 Telegram 미리보기 전송 완료 ({len(message_ids)}개 메시지)")
        return {"sent": True, "message_ids": message_ids}

    except Exception as e:
        print(f"   ⚠️ Telegram 전송 실패: {e}")
        return {"sent": False, "error": str(e)}


def send_publish_result(content_id: str, result: dict) -> bool:
    """발행 결과를 Telegram으로 알림.

    Args:
        content_id: 콘텐츠 ID
        result: publisher.py의 반환값

    Returns:
        전송 성공 여부
    """
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')

    if not bot_token or not chat_id:
        return False

    if result.get("success"):
        text = (
            f"✅ *발행 완료!*\n\n"
            f"ID: `{content_id}`\n"
            f"슬라이드: {result.get('slides_count', 0)}장\n"
            f"Post ID: `{result.get('post_id', 'N/A')}`\n"
        )
        permalink = result.get("permalink", "")
        if permalink:
            text += f"\n🔗 [인스타그램에서 보기]({permalink})"
    else:
        text = (
            f"❌ *발행 실패*\n\n"
            f"ID: `{content_id}`\n"
            f"에러: {result.get('error', '알 수 없는 오류')}"
        )

    msg_id = _send_message(bot_token, chat_id, text)
    return msg_id is not None


def send_weekly_report(contents: list) -> bool:
    """주간 콘텐츠 생성 결과 리포트.

    Args:
        contents: 이번 주 생성된 콘텐츠 리스트

    Returns:
        전송 성공 여부
    """
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')

    if not bot_token or not chat_id:
        return False

    lines = ["📋 *주간 카드뉴스 생성 완료*\n"]
    for c in contents:
        date = c.get("scheduled_date", "?")
        title = c.get("title", "제목 없음")
        ctype = c.get("type", "")
        lines.append(f"• {date} ({ctype}): {title}")

    lines.append(f"\n총 {len(contents)}개 콘텐츠 준비됨 ✅")

    text = "\n".join(lines)
    msg_id = _send_message(bot_token, chat_id, text)
    return msg_id is not None


# ─── 내부 함수들 ───────────────────────────────────────


def _build_summary(content: dict, caption: str) -> str:
    """카드뉴스 요약 텍스트 생성."""
    content_id = content.get("id", "N/A")
    title = content.get("title", "제목 없음")
    ctype = content.get("type", "일반")
    slides = content.get("slides", [])
    scheduled = content.get("scheduled_date", "오늘")

    text = (
        f"🎬 *좀비파크 카드뉴스 미리보기*\n\n"
        f"📌 ID: `{content_id}`\n"
        f"📋 제목: {title}\n"
        f"🏷 유형: {ctype}\n"
        f"📅 발행예정: {scheduled}\n"
        f"🖼 슬라이드: {len(slides)}장\n"
        f"\n─── 슬라이드 텍스트 ───\n"
    )

    for s in slides[:5]:
        slide_num = s.get("slide", "?")
        slide_text = s.get("text", "")[:100]
        text += f"\n*[{slide_num}]* {slide_text}"

    if len(slides) > 5:
        text += f"\n... 외 {len(slides)-5}장"

    return text


def _send_message(bot_token: str, chat_id: str, text: str) -> str | None:
    """Telegram 메시지 전송."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    try:
        resp = requests.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }, timeout=15)

        data = resp.json()
        if data.get("ok"):
            return str(data["result"]["message_id"])
        else:
            print(f"   ⚠️ Telegram 메시지 에러: {data.get('description', '')}")
            return None

    except Exception as e:
        print(f"   ⚠️ Telegram 전송 실패: {e}")
        return None


def _send_photos(bot_token: str, chat_id: str,
                 image_paths: list) -> list:
    """Telegram으로 이미지 그룹 전송."""
    message_ids = []

    if len(image_paths) == 1:
        # 단일 이미지
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        try:
            with open(image_paths[0], 'rb') as photo:
                resp = requests.post(url, data={
                    "chat_id": chat_id,
                }, files={"photo": photo}, timeout=30)

            data = resp.json()
            if data.get("ok"):
                message_ids.append(str(data["result"]["message_id"]))
        except Exception as e:
            print(f"   ⚠️ 사진 전송 실패: {e}")

    else:
        # 미디어 그룹 (2장 이상)
        url = f"https://api.telegram.org/bot{bot_token}/sendMediaGroup"
        media = []
        files = {}

        for i, path in enumerate(image_paths):
            attach_name = f"photo_{i}"
            media.append({
                "type": "photo",
                "media": f"attach://{attach_name}",
            })
            files[attach_name] = open(path, 'rb')

        try:
            resp = requests.post(url, data={
                "chat_id": chat_id,
                "media": json.dumps(media),
            }, files=files, timeout=60)

            data = resp.json()
            if data.get("ok"):
                for msg in data["result"]:
                    message_ids.append(str(msg["message_id"]))
        except Exception as e:
            print(f"   ⚠️ 미디어 그룹 전송 실패: {e}")
        finally:
            for f in files.values():
                f.close()

    return message_ids
