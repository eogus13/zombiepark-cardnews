"""Step 1: 콘텐츠 선택 — 오늘 발행할 카드뉴스 1개 선택"""

import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

from src.utils import load_json

# KST 타임존
KST = timezone(timedelta(hours=9))

# 요일별 콘텐츠 유형 (폴백용)
SCHEDULE = {
    "Monday": "did_you_know",
    "Tuesday": "quiz",
    "Wednesday": "fact_check",
    "Thursday": "survival_skill",
    "Friday": "culture_story",
    "Saturday": "scenario",
    "Sunday": "yeongheung_tmi"
}


def select_content() -> dict | None:
    """오늘 발행할 콘텐츠 1개를 선택.

    우선순위:
    1. next_week_schedule.json에 오늘 날짜가 있으면 그것 사용
    2. 없으면 요일 기반으로 content_pool에서 미발행 콘텐츠 선택

    Returns:
        선택된 콘텐츠 dict, 없으면 None
    """
    today = datetime.now(KST)
    today_str = today.strftime('%Y-%m-%d')
    weekday = today.strftime('%A')

    pool = load_json("data/content_pool.json")
    contents = pool.get("content", [])

    # 1) 주간 스케줄 확인
    schedule_path = Path("data/next_week_schedule.json")
    if schedule_path.exists():
        schedule = json.loads(schedule_path.read_text(encoding='utf-8'))
        if today_str in schedule and schedule[today_str].get('id'):
            target_id = schedule[today_str]['id']
            for c in contents:
                if c["id"] == target_id and not c.get("published"):
                    print(f"   📅 주간 스케줄 사용: [{c['id']}] {c['title']}")
                    return c
            print(f"   ⚠️ 스케줄 ID {target_id}을 풀에서 못 찾음. 폴백 진행.")

    # 2) 요일 기반 폴백
    content_type = SCHEDULE.get(weekday, "did_you_know")
    print(f"   📆 요일 기반 선택: {weekday} → {content_type}")

    candidates = [
        c for c in contents
        if c.get("type") == content_type and not c.get("published")
    ]

    if not candidates:
        # 해당 유형이 없으면 아무 미발행 콘텐츠
        print(f"   ⚠️ {content_type} 유형 없음. 다른 유형에서 선택.")
        candidates = [c for c in contents if not c.get("published")]

    if not candidates:
        print("   ❌ 발행할 콘텐츠가 없습니다.")
        return None

    # 가장 오래된 (먼저 만들어진) 콘텐츠 선택
    selected = candidates[0]
    print(f"   ✅ 선택: [{selected['id']}] {selected['title']}")
    return selected


def mark_as_published(content_id: str, post_id: str) -> None:
    """발행 완료 처리: content_pool에서 published=True + publish_log에 기록."""

    # content_pool.json 업데이트
    pool = load_json("data/content_pool.json")
    now = datetime.now(KST).strftime('%Y-%m-%d %H:%M')

    title = ""
    content_type = ""
    for c in pool.get("content", []):
        if c["id"] == content_id:
            c["published"] = True
            c["published_date"] = now
            title = c.get("title", "")
            content_type = c.get("type", "")
            break

    from src.utils import save_json
    save_json("data/content_pool.json", pool)

    # publish_log.json에 추가
    log = load_json("data/publish_log.json")
    log.setdefault("published", []).append({
        "id": content_id,
        "date": datetime.now(KST).strftime('%Y-%m-%d'),
        "post_id": post_id,
        "type": content_type,
        "title": title
    })
    save_json("data/publish_log.json", log)
