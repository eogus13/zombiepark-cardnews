"""Step 9: 에이전트 협업 — 전략가·마케터·데이터분석가 3개 에이전트 연동

전략가 (Strategy): 주간 단위 — 페르소나 매칭 + 저니 스테이지 + 우선순위 리밸런싱
마케터 (Marketing): 일일 단위 — PAS 카피 + 심리 기법 + A/B 캡션
데이터분석가 (Data): 인사이트 수집 + 에너지 점수 + 주간 분석 → 피드백 루프
"""

import os
import json
from datetime import datetime, timezone, timedelta

from src.utils import load_json, save_json

KST = timezone(timedelta(hours=9))
FEEDBACK_PATH = "data/agent_feedback.json"
PERFORMANCE_LOG_PATH = "data/performance_log.json"
INSIGHT_QUEUE_PATH = "data/insight_queue.json"


# ═══════════════════════════════════════════════════
#  1. 전략가 에이전트 (Strategy) — 주간 단위
# ═══════════════════════════════════════════════════

def strategy_enhance(contents: list) -> list:
    """주간 콘텐츠에 전략적 메타데이터 추가.

    - 타겟 페르소나 매칭
    - 고객 여정 스테이지 배정
    - 피드백 기반 우선순위 조정

    Args:
        contents: 주간 생성된 7개 콘텐츠 리스트

    Returns:
        전략 메타데이터가 추가된 콘텐츠 리스트
    """
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        print("   ⚠️ Gemini API 키 없음. 전략 강화 건너뜀.")
        # 폴백: 기본 메타데이터
        for content in contents:
            content.setdefault("target_persona", "일반_관광")
            content.setdefault("journey_stage", "awareness")
            content.setdefault("priority", 3)
            content.setdefault("angle", "")
        return contents

    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # 피드백 데이터 로드
    feedback = load_json(FEEDBACK_PATH)
    feedback_hint = json.dumps(feedback, ensure_ascii=False)[:1000] if feedback else "없음"

    contents_json = json.dumps(contents, ensure_ascii=False)

    prompt = f"""당신은 좀비파크 마케팅 전략가입니다.
이번 주 카드뉴스 7개에 전략적 메타데이터를 추가하세요.

[이번 주 콘텐츠]
{contents_json}

[지난주 성과 피드백]
{feedback_hint}

[페르소나 목록]
1. 탐험가_20대: 20대, 새로운 경험/도전을 좋아하는 액티비티 중심
2. 공포팬_30대: 30-40대, 공포/좀비 콘텐츠를 즐기는 매니아층
3. 가족_부모: 30-40대 부모, 아이와 특별한 체험을 원함
4. 커플: 20-30대 커플, 데이트 코스 탐색
5. 일반_관광: 영흥도/인천 여행 계획자

[고객 여정]
1. awareness: 좀비파크를 처음 알게 되는 단계
2. interest: 관심을 갖고 더 알아보는 단계
3. desire: 가고 싶다는 욕구가 생기는 단계
4. action: 예약/방문 결정 단계

각 콘텐츠에 다음을 추가하세요:
- target_persona: 가장 적합한 페르소나 1개
- journey_stage: 고객 여정 단계
- priority: 1-5 (5가 최고, 피드백 기반 조정)
- angle: 콘텐츠 차별화 각도 (한 줄)

JSON 배열만 출력 (원본 필드 유지 + 위 4개 추가):"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]

        enhanced = json.loads(text)

        # 원본 데이터 보존 + 새 필드 병합
        for i, content in enumerate(contents):
            if i < len(enhanced):
                content["target_persona"] = enhanced[i].get("target_persona", "일반_관광")
                content["journey_stage"] = enhanced[i].get("journey_stage", "awareness")
                content["priority"] = enhanced[i].get("priority", 3)
                content["angle"] = enhanced[i].get("angle", "")

        print("   🎯 전략가 에이전트: 페르소나/여정/우선순위 매칭 완료")
        return contents

    except Exception as e:
        print(f"   ⚠️ 전략가 에이전트 실패: {e}. 기본값 적용.")
        # 폴백: 기본 메타데이터
        for content in contents:
            content.setdefault("target_persona", "일반_관광")
            content.setdefault("journey_stage", "awareness")
            content.setdefault("priority", 3)
            content.setdefault("angle", "")
        return contents


# ═══════════════════════════════════════════════════
#  2. 마케터 에이전트 (Marketing) — 일일 단위
# ═══════════════════════════════════════════════════

def marketer_enhance(content: dict, slides_text: list) -> dict:
    """일일 콘텐츠의 카피를 마케팅 심리 기법으로 강화.

    - PAS (Problem-Agitate-Solve) 프레임워크
    - 심리 트리거 (호기심 갭, 소셜 프루프, 희소성 등)
    - A/B 캡션 생성

    Args:
        content: 오늘의 콘텐츠 dict
        slides_text: 현재 슬라이드 텍스트 리스트

    Returns:
        강화된 캡션과 대안 캡션 포함 dict
    """
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        print("   ⚠️ Gemini API 키 없음. 마케터 강화 건너뜀.")
        return content

    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    feedback = load_json(FEEDBACK_PATH)
    top_patterns = feedback.get("top_caption_patterns", [])
    patterns_hint = ", ".join(top_patterns[:3]) if top_patterns else "없음"

    prompt = f"""당신은 좀비파크 SNS 마케팅 전문가입니다.
아래 카드뉴스의 인스타그램 캡션을 강화하세요.

[콘텐츠 정보]
제목: {content.get('title', '')}
유형: {content.get('type', '')}
타겟: {content.get('target_persona', '전체')}
여정 단계: {content.get('journey_stage', 'awareness')}

[슬라이드 텍스트]
{json.dumps(slides_text, ensure_ascii=False)}

[현재 캡션]
{content.get('caption', '')}

[잘 먹힌 캡션 패턴]
{patterns_hint}

[요구사항]
1. PAS 프레임워크 적용:
   - Problem: 타겟의 니즈/고민 언급
   - Agitate: 감정 자극
   - Solve: 좀비파크가 해결책

2. 심리 트리거 1-2개 적용:
   - 호기심 갭: "이것을 모르면..."
   - 소셜 프루프: "N명이 이미..."
   - 희소성: "한정", "오직"
   - FOMO: "놓치면 후회"

3. A/B 캡션 2개 제공

JSON만 출력:
{{"enhanced_caption": "메인 캡션",
  "alt_caption": "대안 캡션",
  "hook_line": "첫 줄 후킹 문구",
  "cta": "CTA 문구",
  "psychology_used": ["사용된 심리 기법"]}}"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]

        result = json.loads(text)

        content["caption"] = result.get("enhanced_caption", content.get("caption", ""))
        content["alt_caption"] = result.get("alt_caption", "")
        content["hook_line"] = result.get("hook_line", "")
        content["cta"] = result.get("cta", "")
        content["psychology_used"] = result.get("psychology_used", [])

        print("   💡 마케터 에이전트: PAS 캡션 + 심리 트리거 적용 완료")
        return content

    except Exception as e:
        print(f"   ⚠️ 마케터 에이전트 실패: {e}. 원본 캡션 유지.")
        return content


# ═══════════════════════════════════════════════════
#  3. 데이터분석가 에이전트 (Data) — 인사이트 수집 + 분석
# ═══════════════════════════════════════════════════

def collect_post_insights(post_id: str) -> dict | None:
    """Instagram Graph API로 포스트 인사이트 수집.

    에너지 점수 = likes + comments×2 + saved×3 + shares×4

    Args:
        post_id: Instagram 포스트 ID

    Returns:
        {"likes": N, "comments": N, "saved": N, "shares": N,
         "reach": N, "energy_score": N} 또는 None
    """
    access_token = os.environ.get('INSTAGRAM_ACCESS_TOKEN', '')
    if not access_token or not post_id:
        return None

    try:
        # 기본 메트릭 (likes, comments)
        url = f"https://graph.facebook.com/v19.0/{post_id}"
        params = {
            "fields": "like_count,comments_count,timestamp",
            "access_token": access_token,
        }
        resp = requests.get(url, params=params, timeout=15)
        basic = resp.json()

        likes = basic.get("like_count", 0)
        comments = basic.get("comments_count", 0)

        # 인사이트 메트릭 (saved, shares, reach)
        insight_url = f"https://graph.facebook.com/v19.0/{post_id}/insights"
        insight_params = {
            "metric": "saved,shares,reach",
            "access_token": access_token,
        }
        resp2 = requests.get(insight_url, params=insight_params, timeout=15)
        insight_data = resp2.json()

        saved = 0
        shares = 0
        reach = 0

        for item in insight_data.get("data", []):
            name = item.get("name", "")
            value = item.get("values", [{}])[0].get("value", 0)
            if name == "saved":
                saved = value
            elif name == "shares":
                shares = value
            elif name == "reach":
                reach = value

        energy = likes + comments * 2 + saved * 3 + shares * 4

        return {
            "likes": likes,
            "comments": comments,
            "saved": saved,
            "shares": shares,
            "reach": reach,
            "energy_score": energy,
        }

    except Exception as e:
        print(f"   ⚠️ 인사이트 수집 실패 ({post_id}): {e}")
        return None


def update_performance_insights() -> int:
    """performance_log에서 인사이트 미수집 포스트를 업데이트.

    Returns:
        업데이트된 포스트 수
    """
    import requests  # noqa: F811 (함수 내 임포트)

    perf = load_json(PERFORMANCE_LOG_PATH)
    posts = perf.get("posts", [])
    updated = 0

    for post in posts:
        if (post.get("success") and
                post.get("post_id") and
                post.get("insights") is None):

            insights = collect_post_insights(post["post_id"])
            if insights:
                post["insights"] = insights
                post["energy_score"] = insights["energy_score"]
                updated += 1
                print(f"   📈 {post['content_id']}: energy={insights['energy_score']}")

    if updated > 0:
        save_json(PERFORMANCE_LOG_PATH, perf)
        print(f"   📊 {updated}개 포스트 인사이트 업데이트 완료")

    return updated


def generate_weekly_analysis() -> dict:
    """주간 성과 분석 → agent_feedback.json 생성.

    분석 내용:
    - 유형별 평균 에너지 점수
    - 베스트/워스트 콘텐츠
    - 캡션 패턴 분석
    - 다음 주 추천사항

    Returns:
        분석 결과 dict (agent_feedback.json에도 저장됨)
    """
    perf = load_json(PERFORMANCE_LOG_PATH)
    posts = perf.get("posts", [])

    # 인사이트 있는 포스트만
    scored = [p for p in posts if p.get("energy_score") is not None]

    if not scored:
        print("   ⚠️ 분석할 인사이트 데이터 없음.")
        return {}

    # 유형별 통계
    type_stats = {}
    for p in scored:
        t = p.get("type", "unknown")
        if t not in type_stats:
            type_stats[t] = {"scores": [], "count": 0}
        type_stats[t]["scores"].append(p["energy_score"])
        type_stats[t]["count"] += 1

    type_averages = {}
    for t, data in type_stats.items():
        avg = sum(data["scores"]) / len(data["scores"])
        type_averages[t] = round(avg, 1)

    # 베스트/워스트
    best = max(scored, key=lambda p: p["energy_score"])
    worst = min(scored, key=lambda p: p["energy_score"])

    # 전체 평균
    all_scores = [p["energy_score"] for p in scored]
    overall_avg = sum(all_scores) / len(all_scores)

    # 추천사항 생성
    recommendations = []
    if type_averages:
        best_type = max(type_averages, key=type_averages.get)
        worst_type = min(type_averages, key=type_averages.get)
        recommendations.append(f"{best_type} 유형이 가장 높은 반응 (평균 {type_averages[best_type]})")
        recommendations.append(f"{worst_type} 유형 개선 필요 (평균 {type_averages[worst_type]})")

    feedback = {
        "generated_at": datetime.now(KST).strftime("%Y-%m-%d %H:%M"),
        "period_posts": len(scored),
        "overall_avg_energy": round(overall_avg, 1),
        "type_averages": type_averages,
        "best_post": {
            "id": best.get("content_id", ""),
            "title": best.get("title", ""),
            "type": best.get("type", ""),
            "energy": best["energy_score"],
        },
        "worst_post": {
            "id": worst.get("content_id", ""),
            "title": worst.get("title", ""),
            "type": worst.get("type", ""),
            "energy": worst["energy_score"],
        },
        "recommendations": recommendations,
        "top_caption_patterns": [],  # 향후 NLP 분석으로 확장 가능
    }

    save_json(FEEDBACK_PATH, feedback)
    print(f"   🧠 주간 분석 완료: 평균 에너지 {overall_avg:.1f}, "
          f"분석 포스트 {len(scored)}개")

    return feedback
