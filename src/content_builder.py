"""Step 0-B: 콘텐츠 빌더 — 매주 7개 카드뉴스 자동 생성"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta

from src.utils import load_json, save_json

# 요일별 콘텐츠 유형
WEEKLY_TYPE_MAP = {
    "Saturday": "scenario",
    "Sunday": "yeongheung_tmi",
    "Monday": "did_you_know",
    "Tuesday": "quiz",
    "Wednesday": "fact_check",
    "Thursday": "survival_skill",
    "Friday": "culture_story"
}


def build_weekly_content(changes: dict,
                         obsidian_path: str = "obsidian_data") -> list:
    """다음 주 7일치 카드뉴스를 한 번에 생성.

    Args:
        changes: scanner.py 출력 (new_files, modified_files 등)
        obsidian_path: 옵시디언 폴더 경로

    Returns:
        7개 콘텐츠 dict 리스트
    """
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        print("   ⚠️ Gemini API 키 없음. 콘텐츠 생성 불가.")
        return []

    from google import genai
    client = genai.Client(api_key=api_key)

    # 1) 전체 옵시디언 자료 수집
    all_source_texts = _collect_source_material(Path(obsidian_path))

    # 2) 이번 주 변경 하이라이트
    change_highlight = _format_changes(changes)

    # 3) 발행 히스토리 (겹침 방지)
    published_titles = _get_published_titles()

    # 4) 성과 피드백 (있으면)
    feedback_hint = _get_feedback_hint()

    # 5) 다음 주 요일별 유형 목록
    next_week_types = _get_next_week_type_list()

    prompt = f"""당신은 좀비파크 인스타그램 카드뉴스 콘텐츠 기획자입니다.

다음 주 7일간 발행할 카드뉴스를 **정확히 7개** 만들어주세요.
각 날짜에 지정된 콘텐츠 유형에 맞게 제작합니다.

[다음 주 스케줄 — 이 순서대로 7개 생성]
{next_week_types}

[콘텐츠 유형별 슬라이드 수]
- did_you_know: 충격적 사실 1장짜리 (임팩트 한 방)
- quiz: 3장 (질문→보기→정답+해설)
- survival_skill: 4장 (타이틀→스킬1→스킬2→CTA)
- fact_check: 3장 (작품소개→"과학적으로 가능?"→결론)
- culture_story: 3장 (문화권 소개→핵심 스토리→현대 연결)
- scenario: 3장 ("당신이라면?"→상황설명→선택지+해설)
- yeongheung_tmi: 3장 (영흥도 소개→흥미로운 사실→좀비파크 연결)

[전체 자료 — 이 안에서 소재 발굴]
{all_source_texts}
{change_highlight}

[이미 발행한 콘텐츠 — 겹치면 안 됨]
{published_titles}
{feedback_hint}

[출력 형식 — JSON 배열, 정확히 7개]
[
  {{
    "type": "지정된 유형",
    "weekday": "요일명(영문)",
    "title": "카드뉴스 제목",
    "slides": [
      {{"slide": 1, "text": "카드에 들어갈 한글 텍스트"}}
    ],
    "caption": "인스타그램 캡션 (후킹 첫줄 + 본문 + CTA)",
    "hashtags": ["#좀비파크", "#영흥도", ...최대 20개],
    "source_file": "참고한 원본 파일 경로",
    "angle": "이 소재를 어떤 각도로 다뤘는지 한 줄"
  }}
]

규칙:
- 반드시 7개, 하나도 빠지면 안 됨
- 이미 발행한 제목/소재와 겹치지 않게 — 같은 자료도 새 각도로
- 이번 주 새로 추가된 자료가 있으면 우선 반영
- 한글, 짧고 임팩트 있게, 이모지 적절히
- 캡션은 호기심 유발하는 첫 줄이 핵심
- JSON만 출력하세요. 설명 없이."""

    # Gemini API 호출 (최대 3회 재시도, 503/429 등 일시 오류 대응)
    import time
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                wait_sec = 10 * attempt  # 10초, 20초 대기
                print(f"   ⏳ {wait_sec}초 대기 후 재시도 ({attempt + 1}/{max_retries})")
                time.sleep(wait_sec)

            response = client.models.generate_content(
                model='gemini-2.5-flash', contents=prompt
            )

            # JSON 블록 추출 (```json ... ``` 형태일 수 있음)
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]  # 첫 줄 제거
                text = text.rsplit("```", 1)[0]  # 마지막 ``` 제거
            contents = json.loads(text)
            if len(contents) != 7:
                print(f"   ⚠️ {len(contents)}개 생성됨 (7개 필요)")
            return contents

        except json.JSONDecodeError as e:
            print(f"   ⚠️ AI 응답 파싱 실패: {e}")
            if attempt < max_retries - 1:
                continue
            return []
        except Exception as e:
            error_msg = str(e)
            print(f"   ⚠️ Gemini API 오류 (시도 {attempt + 1}/{max_retries}): {error_msg}")
            if attempt >= max_retries - 1:
                print(f"   ❌ 최대 재시도 횟수 초과. 콘텐츠 생성 실패.")
                return []

    return []


def save_weekly_content(contents: list) -> dict:
    """생성된 7개 콘텐츠를 content_pool.json에 저장 + next_week_schedule.json 생성.

    Returns:
        next_week_schedule dict
    """
    pool = load_json("data/content_pool.json")
    if "content" not in pool:
        pool["content"] = []

    today = datetime.now()
    week_id = today.strftime('%Y-W%W')

    # ID 채번
    existing_nums = []
    for c in pool["content"]:
        cid = c.get("id", "")
        if cid.startswith("W") and cid[1:].isdigit():
            existing_nums.append(int(cid[1:]))
    max_num = max(existing_nums, default=0)

    next_week = {}

    for i, content in enumerate(contents):
        max_num += 1
        day = today + timedelta(days=i + 1)
        date_str = day.strftime('%Y-%m-%d')
        weekday = day.strftime('%A')

        content["id"] = f"W{max_num:04d}"
        content["published"] = False
        content["published_date"] = None
        content["created_date"] = today.strftime('%Y-%m-%d')
        content["scheduled_date"] = date_str
        content["week_id"] = week_id

        pool["content"].append(content)

        next_week[date_str] = {
            "id": content["id"],
            "type": content.get("type", "did_you_know"),
            "title": content["title"],
            "weekday": weekday
        }

    save_json("data/content_pool.json", pool)
    save_json("data/next_week_schedule.json", next_week)

    return next_week


# === 내부 헬퍼 함수 ===

def _collect_source_material(obsidian_root: Path) -> str:
    """전체 옵시디언 자료를 요약 형태로 수집 (최대 15000자)."""
    texts = []
    total_chars = 0
    max_total = 15000

    if not obsidian_root.exists():
        return "(옵시디언 폴더 없음)"

    for md_file in sorted(obsidian_root.rglob("*.md")):
        if total_chars >= max_total:
            break
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception:
            continue
        rel_path = str(md_file.relative_to(obsidian_root))
        snippet = content[:2000]
        texts.append(f"=== {rel_path} ===\n{snippet}")
        total_chars += len(snippet)

    return "\n\n".join(texts) if texts else "(자료 없음)"


def _format_changes(changes: dict) -> str:
    """이번 주 변경사항 하이라이트."""
    changed_files = changes.get("new_files", []) + changes.get("modified_files", [])
    if not changed_files:
        return ""

    highlight = "\n\n[이번 주 새로 추가/수정된 내용 — 우선 반영]\n"
    for f in changed_files[:5]:
        highlight += f"--- {f['path']} ---\n{f['content'][:2000]}\n"
    return highlight


def _get_published_titles() -> str:
    """이미 발행한 콘텐츠 제목 (최근 30개)."""
    log = load_json("data/publish_log.json")
    published = log.get("published", [])
    if not published:
        return "아직 발행한 콘텐츠 없음 (첫 주)"

    titles = [f"- [{p.get('type', '?')}] {p.get('title', '?')}" for p in published]
    return "\n".join(titles[-30:])


def _get_feedback_hint() -> str:
    """데이터분석가 피드백에서 콘텐츠 제작 힌트."""
    fb = load_json("data/agent_feedback.json")
    if not fb:
        return ""

    hints = []
    recs = fb.get("recommendations", {})

    # recommendations가 리스트일 수도 있고 딕셔너리일 수도 있음
    if isinstance(recs, list):
        # 리스트 형태: 문자열 항목들을 그대로 힌트로 활용
        for rec in recs[:3]:
            hints.append(f"[피드백] {rec}")
    elif isinstance(recs, dict):
        if recs.get("to_marketer"):
            hints.append(f"[마케터 피드백] {recs['to_marketer']}")
        if recs.get("to_strategist"):
            hints.append(f"[전략가 피드백] {recs['to_strategist']}")

    # top_copy_patterns 또는 top_caption_patterns 둘 다 지원
    patterns = fb.get("top_copy_patterns", []) or fb.get("top_caption_patterns", [])
    if patterns and isinstance(patterns, list) and len(patterns) > 0:
        top = patterns[0]
        if isinstance(top, dict):
            hints.append(f"[고성과 패턴] {top.get('pattern', '')} — 예: {top.get('example', '')}")

    return "\n".join(hints) if hints else ""


def _get_next_week_type_list() -> str:
    """다음 주 7일의 날짜 + 요일 + 유형 목록."""
    today = datetime.now()
    day_kr = {"Saturday": "토", "Sunday": "일", "Monday": "월",
              "Tuesday": "화", "Wednesday": "수", "Thursday": "목",
              "Friday": "금"}
    lines = []
    for i in range(1, 8):
        day = today + timedelta(days=i)
        weekday = day.strftime('%A')
        date_str = day.strftime('%Y-%m-%d')
        content_type = WEEKLY_TYPE_MAP.get(weekday, "did_you_know")
        lines.append(f"{i}. {date_str} ({day_kr.get(weekday, '?')}) → {content_type}")
    return "\n".join(lines)
