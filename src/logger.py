"""Step 8: 로깅 시스템 — Discord 웹훅 알림 + 로컬 발행 기록"""

import os
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import requests

from src.utils import load_json, save_json

KST = timezone(timedelta(hours=9))
PERFORMANCE_LOG_PATH = "data/performance_log.json"


def log_to_discord(title: str, description: str,
                   color: int = 0x39FF14,
                   fields: list = None) -> bool:
    """Discord 웹훅으로 임베드 메시지 전송.

    Args:
        title: 임베드 제목
        description: 본문
        color: 임베드 색상 (기본: 네온 그린)
        fields: [{"name": "필드명", "value": "값", "inline": True}]

    Returns:
        전송 성공 여부
    """
    webhook_url = os.environ.get('DISCORD_WEBHOOK_URL', '')
    if not webhook_url:
        print("   ⚠️ Discord 웹훅 미설정. 로깅 건너뜀.")
        return False

    embed = {
        "title": title,
        "description": description,
        "color": color,
        "timestamp": datetime.now(KST).isoformat(),
        "footer": {"text": "🧟 좀비파크 카드뉴스 자동화"},
    }

    if fields:
        embed["fields"] = fields

    payload = {
        "username": "좀비파크 봇",
        "embeds": [embed],
    }

    try:
        resp = requests.post(webhook_url, json=payload, timeout=15)
        if resp.status_code in (200, 204):
            print(f"   📨 Discord 로그 전송: {title}")
            return True
        else:
            print(f"   ⚠️ Discord 전송 실패: HTTP {resp.status_code}")
            return False
    except Exception as e:
        print(f"   ⚠️ Discord 전송 에러: {e}")
        return False


def log_daily_publish(content_id: str, title: str,
                      content_type: str, result: dict) -> None:
    """일일 발행 결과를 Discord + performance_log.json에 기록.

    Args:
        content_id: 콘텐츠 ID
        title: 콘텐츠 제목
        content_type: 콘텐츠 유형
        result: publisher의 반환값
    """
    now = datetime.now(KST)
    success = result.get("success", False)

    # 1) performance_log에 기록
    perf = load_json(PERFORMANCE_LOG_PATH)
    if "posts" not in perf:
        perf["posts"] = []

    entry = {
        "content_id": content_id,
        "title": title,
        "type": content_type,
        "published_at": now.strftime("%Y-%m-%d %H:%M"),
        "post_id": result.get("post_id", ""),
        "permalink": result.get("permalink", ""),
        "success": success,
        # 인사이트는 나중에 collect_insights가 채움
        "insights": None,
        "energy_score": None,
    }

    if not success:
        entry["error"] = result.get("error", "")

    perf["posts"].append(entry)
    save_json(PERFORMANCE_LOG_PATH, perf)
    print(f"   📊 performance_log 기록 완료: {content_id}")

    # 2) Discord 알림
    if success:
        log_to_discord(
            title=f"✅ 발행 완료: {title}",
            description=f"ID: {content_id}\n유형: {content_type}",
            color=0x39FF14,  # 네온 그린
            fields=[
                {"name": "Post ID", "value": result.get("post_id", "N/A"), "inline": True},
                {"name": "슬라이드", "value": f"{result.get('slides_count', 0)}장", "inline": True},
                {"name": "시간", "value": now.strftime("%H:%M KST"), "inline": True},
            ]
        )
    else:
        log_to_discord(
            title=f"❌ 발행 실패: {title}",
            description=f"ID: {content_id}\n에러: {result.get('error', '')}",
            color=0xFF0000,  # 빨강
        )


def log_weekly_generation(contents: list) -> None:
    """주간 콘텐츠 생성 결과 Discord 로깅.

    Args:
        contents: 이번 주 생성된 콘텐츠 리스트
    """
    lines = []
    for c in contents:
        date = c.get("scheduled_date", "?")
        title = c.get("title", "제목 없음")
        ctype = c.get("type", "")
        lines.append(f"• {date} ({ctype}): {title}")

    description = "\n".join(lines) if lines else "생성된 콘텐츠 없음"

    log_to_discord(
        title=f"📋 주간 카드뉴스 {len(contents)}개 생성",
        description=description,
        color=0x7B68EE,  # 미디엄 슬레이트 블루
        fields=[
            {"name": "총 개수", "value": str(len(contents)), "inline": True},
        ]
    )


def log_insights_collected(post_count: int, avg_energy: float) -> None:
    """인사이트 수집 결과 Discord 로깅."""
    log_to_discord(
        title="📈 인사이트 수집 완료",
        description=f"{post_count}개 포스트 인사이트 업데이트",
        color=0x00BFFF,  # 딥 스카이 블루
        fields=[
            {"name": "평균 에너지 점수", "value": f"{avg_energy:.1f}", "inline": True},
            {"name": "수집 포스트", "value": str(post_count), "inline": True},
        ]
    )


def log_error(stage: str, error_msg: str) -> None:
    """에러 발생 시 Discord 알림."""
    log_to_discord(
        title=f"⚠️ 오류 발생: {stage}",
        description=error_msg[:500],
        color=0xFF4500,  # 오렌지 레드
    )


def get_publish_stats(days: int = 7) -> dict:
    """최근 N일간 발행 통계.

    Returns:
        {"total": 5, "success": 4, "failed": 1,
         "avg_energy": 23.5, "best_type": "quiz"}
    """
    perf = load_json(PERFORMANCE_LOG_PATH)
    posts = perf.get("posts", [])

    cutoff = (datetime.now(KST) - timedelta(days=days)).strftime("%Y-%m-%d")

    recent = [p for p in posts if p.get("published_at", "") >= cutoff]

    if not recent:
        return {"total": 0, "success": 0, "failed": 0,
                "avg_energy": 0, "best_type": ""}

    success_count = sum(1 for p in recent if p.get("success"))
    failed_count = len(recent) - success_count

    # 에너지 점수 통계
    energies = [p["energy_score"] for p in recent
                if p.get("energy_score") is not None]
    avg_energy = sum(energies) / len(energies) if energies else 0

    # 유형별 에너지
    type_energy = {}
    for p in recent:
        if p.get("energy_score") is not None:
            t = p.get("type", "unknown")
            if t not in type_energy:
                type_energy[t] = []
            type_energy[t].append(p["energy_score"])

    best_type = ""
    if type_energy:
        best_type = max(type_energy,
                        key=lambda t: sum(type_energy[t]) / len(type_energy[t]))

    return {
        "total": len(recent),
        "success": success_count,
        "failed": failed_count,
        "avg_energy": round(avg_energy, 1),
        "best_type": best_type,
    }
