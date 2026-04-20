"""Step 4: 텍스트 오버레이 — 배경 이미지 위에 한글 텍스트 + 로고 합성"""

import os
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 브랜드 컬러
NEON_GREEN = (57, 255, 20)       # #39FF14
DARK_PURPLE = (26, 10, 46)       # #1a0a2e
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SHADOW = (0, 0, 0, 180)

# 폰트 경로 (GitHub Actions에서 다운로드됨)
FONT_PATH = "assets/fonts/Pretendard-Bold.otf"
FALLBACK_FONT_PATHS = [
    "assets/fonts/Pretendard-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
]


def compose_card(bg_path: str, text: str, slide_num: int,
                 total_slides: int, output_dir: str = "/tmp") -> str:
    """배경 이미지 + 텍스트 + 로고를 합성하여 최종 카드 생성.

    Args:
        bg_path: 배경 이미지 경로
        text: 카드에 들어갈 텍스트
        slide_num: 현재 슬라이드 번호
        total_slides: 전체 슬라이드 수
        output_dir: 출력 경로

    Returns:
        완성된 카드 이미지 경로
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 1) 배경 이미지 열기 + 1080x1080 리사이즈
    bg = Image.open(bg_path).convert('RGBA').resize((1080, 1080))

    # 2) 하단 그라데이션 오버레이 (텍스트 가독성)
    overlay = Image.new('RGBA', (1080, 1080), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    for y in range(540, 1080):
        alpha = int(220 * (y - 540) / (1080 - 540))
        draw_overlay.rectangle([(0, y), (1080, y)],
                               fill=(26, 10, 46, alpha))
    bg = Image.alpha_composite(bg, overlay)

    # 3) 텍스트 그리기
    draw = ImageDraw.Draw(bg)
    font_main = _load_font(48)
    font_small = _load_font(28)
    font_tag = _load_font(22)

    # 텍스트 줄바꿈 처리
    lines = text.split('\n')
    # 너무 긴 줄은 자동 줄바꿈
    wrapped_lines = []
    for line in lines:
        if len(line) > 18:
            wrapped_lines.extend(textwrap.wrap(line, width=18))
        else:
            wrapped_lines.append(line)

    # 텍스트 영역 시작 Y (줄 수에 따라 동적)
    line_height = 62
    total_text_height = len(wrapped_lines) * line_height
    text_y = max(680, 1080 - total_text_height - 120)

    for line in wrapped_lines:
        # 그림자
        draw.text((42, text_y + 2), line, fill=BLACK, font=font_main)
        draw.text((38, text_y + 2), line, fill=BLACK, font=font_main)
        # 본문 (흰색)
        draw.text((40, text_y), line, fill=WHITE, font=font_main)
        text_y += line_height

    # 4) 슬라이드 번호 (좌상단, 네온 그린)
    if total_slides > 1:
        # 번호 배경
        draw.rounded_rectangle(
            [(30, 30), (110, 70)],
            radius=8,
            fill=(26, 10, 46, 200)
        )
        draw.text((42, 35), f"{slide_num}/{total_slides}",
                  fill=NEON_GREEN, font=font_small)

    # 5) 로고 삽입 (우하단)
    logo_path = Path("assets/logo.png")
    if logo_path.exists():
        logo = Image.open(str(logo_path)).convert('RGBA').resize((100, 100))
        bg.paste(logo, (960, 960), logo)
    else:
        # 로고 없으면 텍스트 워터마크
        draw.text((880, 1040), "ZOMBIE PARK", fill=NEON_GREEN, font=font_tag)

    # 6) 상단 네온 그린 액센트 바
    draw.rectangle([(0, 0), (1080, 4)], fill=NEON_GREEN)

    # 7) 저장
    output_path = f"{output_dir}/slide_{slide_num}_final.png"
    bg.convert('RGB').save(output_path, quality=95)
    return output_path


def compose_all_cards(slides: list, raw_images: list,
                      output_dir: str = "/tmp") -> list:
    """전체 슬라이드를 한 번에 합성.

    Args:
        slides: [{"slide": 1, "text": "...", "image_prompt": "..."}]
        raw_images: ["/tmp/slide_1_raw.png", ...]

    Returns:
        ["/tmp/slide_1_final.png", ...] 완성된 카드 경로 리스트
    """
    total = len(slides)
    final_images = []

    for i, (slide, img_path) in enumerate(zip(slides, raw_images)):
        composed = compose_card(
            bg_path=img_path,
            text=slide.get('text', ''),
            slide_num=i + 1,
            total_slides=total,
            output_dir=output_dir
        )
        final_images.append(composed)
        print(f"   🖼️ 슬라이드 {i+1}/{total} 합성 완료")

    return final_images


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """폰트 로드. 여러 경로 시도."""
    paths_to_try = [FONT_PATH] + FALLBACK_FONT_PATHS

    for path in paths_to_try:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue

    # 모든 경로 실패 → 기본 폰트
    print("   ⚠️ 한글 폰트를 찾지 못함. 기본 폰트 사용.")
    return ImageFont.load_default()
