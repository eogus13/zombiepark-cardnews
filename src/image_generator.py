"""Step 3: AI 이미지 생성 — Stability AI SD3로 배경 이미지 생성"""

import os
import requests
from pathlib import Path


def generate_images(slides: list, output_dir: str = "/tmp") -> list:
    """각 슬라이드의 image_prompt로 배경 이미지 생성.

    Args:
        slides: [{"slide": 1, "text": "...", "image_prompt": "..."}]
        output_dir: 이미지 저장 경로

    Returns:
        ["/tmp/slide_1_raw.png", ...] 파일 경로 리스트
    """
    images = []
    api_key = os.environ.get('STABILITY_API_KEY', '')

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

        if api_key:
            success = _generate_with_stability(prompt, filepath, api_key)
            if success:
                images.append(filepath)
                print(f"   🎨 슬라이드 {slide_num}: AI 이미지 생성 완료")
                continue

        # 폴백: 단색 배경
        fallback_path = _create_fallback_image(slide_num, output_dir)
        images.append(fallback_path)
        print(f"   🎨 슬라이드 {slide_num}: 폴백 배경 사용")

    return images


def _generate_with_stability(prompt: str, filepath: str, api_key: str) -> bool:
    """Stability AI SD3 API로 이미지 생성."""
    try:
        response = requests.post(
            "https://api.stability.ai/v2beta/stable-image/generate/sd3",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "image/*"
            },
            files={"none": ''},
            data={
                "prompt": prompt,
                "output_format": "png",
                "aspect_ratio": "1:1",
                "model": "sd3-medium"
            },
            timeout=60
        )

        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"   ⚠️ Stability API 에러: {response.status_code}")
            return False

    except Exception as e:
        print(f"   ⚠️ Stability API 호출 실패: {e}")
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
