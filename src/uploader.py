"""Step 5: Cloudinary 업로드 — 완성된 카드 이미지를 CDN에 업로드"""

import os
import cloudinary
import cloudinary.uploader


def init_cloudinary():
    """Cloudinary 설정 초기화."""
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
        api_key=os.environ.get('CLOUDINARY_API_KEY', ''),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET', ''),
        secure=True
    )


def upload_images(image_paths: list, content_id: str = "card") -> list:
    """카드 이미지들을 Cloudinary에 업로드.

    Args:
        image_paths: 로컬 이미지 경로 리스트
        content_id: 콘텐츠 ID (폴더명에 사용)

    Returns:
        [{"url": "https://...", "public_id": "..."}] Cloudinary URL 리스트
    """
    init_cloudinary()
    uploaded = []

    for i, path in enumerate(image_paths):
        try:
            result = cloudinary.uploader.upload(
                path,
                folder=f"zombiepark/{content_id}",
                public_id=f"slide_{i+1}",
                overwrite=True,
                resource_type="image",
                transformation=[
                    {"quality": "auto:good", "fetch_format": "auto"}
                ]
            )
            uploaded.append({
                "url": result["secure_url"],
                "public_id": result["public_id"],
                "width": result.get("width", 1080),
                "height": result.get("height", 1080),
            })
            print(f"   ☁️ 슬라이드 {i+1} 업로드 완료: {result['secure_url'][:60]}...")

        except Exception as e:
            print(f"   ⚠️ 슬라이드 {i+1} 업로드 실패: {e}")
            # 실패 시 로컬 경로라도 반환 (디버그용)
            uploaded.append({
                "url": path,
                "public_id": f"local_{i+1}",
                "width": 1080,
                "height": 1080,
                "error": str(e)
            })

    return uploaded


def delete_images(content_id: str) -> bool:
    """특정 콘텐츠의 Cloudinary 이미지 삭제 (정리용).

    Args:
        content_id: 콘텐츠 ID

    Returns:
        성공 여부
    """
    init_cloudinary()
    try:
        result = cloudinary.api.delete_resources_by_prefix(
            f"zombiepark/{content_id}/"
        )
        print(f"   🗑️ Cloudinary 이미지 삭제: {content_id}")
        return True
    except Exception as e:
        print(f"   ⚠️ Cloudinary 삭제 실패: {e}")
        return False
