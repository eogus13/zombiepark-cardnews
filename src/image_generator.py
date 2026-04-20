"""Step 3: AI 이미지 생성 — Pollinations.ai (무료, API 키 불필요)"""

import os
import time
import requests
from pathlib import Path
from urllib.parse import quote


def generate_images(slides: list, output_dir: str = "/tmp") -> list:
    """각 슬라이드의 image_prompt로 배경 이미지 생성.

    Args:
        slides: [{"slide": 1, "text": "...", "image_prompt": "..."}]
        output_dir: 이미지 저장 경로

    Returns:
        ["/tmp/slide_1_raw.png", ...] 파일 경로 리스트
    """
    images = []

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for slide in slides:
        slide_num = slide.get('slide', len(images) + 1)
        prompt = slide.get('image_prompt', '')

        if not prompt:
            prompt = (
                "Cinematic survival horror scene, dark moody atmosphere, "
                "neon green accents, abandoned island, Instagram square 1:1, "
                "high contrast, dark purple background"
            )

        filepath = f"{output_dir}/slide_{slide_num}_raw.png"

        # 최대 2회 시도 (1회 실패 시 seed 변경 후 재시도)
        success = False
        for attempt in range(2):
            if attempt > 0:
                print(f"   🔄 슬라이드 {slide_num}: 재시도 ({attempt + 1}/2)")
                time.sleep(3)  # 재시도 전 잠깐 대기
            success = _generate_with_pollinations(prompt, filepath, attempt)
            if success:
                break

        if success:
            images.append(filepath)
            print(f"   🎨 슬라이드 {slide_num}: AI 이미지 생성 완료")
            continue

        # 폴백: 단색 배경
        fallback_path = _create_fallback_image(slide_num, output_dir)
        images.append(fallback_path)
        print(f"   🎨 슬라이드 {slide_num}: 폴백 배경 사용")

    return images


def _generate_with_pollinations(prompt: str, filepath: str, attempt: int = 0) -> bool:
    """Pollinations.ai로 이미지 생성 (무료, API 키 불필요).

    Args:
        prompt: 이미지 생성 프롬프트
        filepath: 저장 경로
        attempt: 시도 횟수 (seed 분산용)
    """
    try:
        # 좀비파크 테마에 맞는 프롬프트 보강
        enhanced_prompt = (
            f"{prompt}, dark cinematic style, horror atmosphere, "
            "neon green and dark purple color scheme, high quality, detailed"
        )

        encoded_prompt = quote(enhanced_prompt)
        seed = int(time.time()) + attempt * 1000
        url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            f"?width=1080&height=1080&nologo=true&seed={seed}"
        )

        response = requests.get(url, timeout=120, stream=True)

        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'image' in content_type or len(response.content) > 10000:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print(f"   ⚠️ Pollinations 응답이 이미지가 아님")
                return False
        else:
            print(f"   ⚠️ Pollinations API 에러: {response.status_code}")
            return False

    except requests.exceptions.Timeout:
        print(f"   ⚠️ Pollinations API 타임아웃 (120초)")
        return False
    except Exception as e:
        print(f"   ⚠️ Pollinations API 호출 실패: {e}")
        return False


def _create_fallback_image(slide_num: int, output_dir: str) -> str:
    """API 실패 시 단색 다크 퍼플 배경 생성."""
    from PIL import Image, ImageDraw

    DARK_PURPLE = (26, 10, 46)
    NEON_GREEN = (57, 255, 20)

    img = Image.new('RGB', (1080, 1080), DARK_PURPLE)
    draw = ImageDraw.Draw(img)

    # 미묘한 그라데이션 효과
    for y in range(1080):
        r = int(26 + (y / 1080) * 10)
        g = int(10 - (y / 1080) * 5)
        b = int(46 + (y / 1080) * 15)
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        draw.line([(0, y), (1080, y)], fill=(r, g, b))

    # 네온 그린 액센트 라인 (상단)
    draw.rectangle([(0, 0), (1080, 3)], fill=NEON_GREEN)

    filepath = f"{output_dir}/slide_{slide_num}_raw.png"
    img.save(filepath, quality=95)
    return filepath
