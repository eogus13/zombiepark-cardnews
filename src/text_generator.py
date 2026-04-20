"""Step 2: AI 텍스트 생성 — Gemini로 카드 텍스트 다듬기 + 이미지 프롬프트 생성"""

import os
import json

from src.image_generator import get_style_for_type

# Gemini는 런타임에만 임포트 (API 키 필요)


def generate_text(content: dict) -> dict:
    """선택된 콘텐츠를 인스타그램 최적화 형태로 다듬기.

    Args:
        content: selector.py에서 선택된 콘텐츠 dict

    Returns:
        {
            "slides": [{"slide": 1, "text": "...", "image_prompt": "..."}],
            "caption": "...",
            "hashtags": [...]
        }
    """
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        print("   ⚠️ Gemini API 키 없음. 폴백 텍스트 사용.")
        return _fallback_text(content)

    from google import genai
    client = genai.Client(api_key=api_key)

    content_type = content.get('type', '')
    type_style = get_style_for_type(content_type)

    prompt = f"""당신은 좀비파크 인스타그램 카드뉴스 작가입니다.
아래 콘텐츠를 인스타그램에 최적화된 형태로 다듬어주세요.

[원본 콘텐츠]
제목: {content.get('title', '')}
유형: {content_type}
장별 텍스트: {json.dumps(content.get('slides', []), ensure_ascii=False)}
캡션: {content.get('caption', '')}
타겟 페르소나: {content.get('target_persona', '전체')}

[요청사항]
1. 각 장별 카드 텍스트: 한글, 짧고 임팩트 있게, 이모지 적절히
   - 한 줄은 최대 15자 내외
   - 줄바꿈으로 리듬감
2. 각 장별 이미지 생성용 영문 프롬프트 1개씩
   (이 유형의 이미지 분위기: {type_style}
    공통: Instagram 1:1, high contrast, neon green and dark purple tones)
   ※ 슬라이드마다 다른 장면을 그릴 것 — 동일 이미지 반복 금지
3. 인스타그램 캡션: 후킹 첫줄 + 본문 2줄 + CTA + 해시태그 20개

JSON만 출력:
{{"slides": [{{"slide": 1, "text": "...", "image_prompt": "..."}}],
  "caption": "...",
  "hashtags": [...]}}"""

    response = client.models.generate_content(
        model='gemini-2.5-flash', contents=prompt
    )

    try:
        text = response.text.strip()
        # ```json ... ``` 형태 처리
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        result = json.loads(text)

        # 필수 키 보장
        result.setdefault("slides", content.get("slides", []))
        result.setdefault("caption", content.get("caption", ""))
        result.setdefault("hashtags", content.get("hashtags", ["#좀비파크"]))

        return result

    except (json.JSONDecodeError, Exception) as e:
        print(f"   ⚠️ AI 텍스트 파싱 실패: {e}. 원본 텍스트 사용.")
        # 폴백: 원본 텍스트에 기본 이미지 프롬프트 추가
        return _fallback_text(content)


def _fallback_text(content: dict) -> dict:
    """AI 실패 시 원본 텍스트 기반 폴백."""
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
