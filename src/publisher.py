"""Step 6: Instagram 발행 — Graph API로 캐러셀(슬라이드) 포스트 발행"""

import os
import time
import requests


# Instagram Graph API 엔드포인트
GRAPH_API_BASE = "https://graph.facebook.com/v19.0"


def publish_carousel(image_urls: list, caption: str) -> dict:
    """Instagram 캐러셀 포스트 발행.

    Instagram Graph API 캐러셀 발행 3단계:
    1) 각 이미지를 개별 미디어 컨테이너로 생성
    2) 캐러셀 컨테이너 생성 (자식 미디어 포함)
    3) 캐러셀 발행

    Args:
        image_urls: Cloudinary에 업로드된 이미지 URL 리스트
        caption: 인스타그램 캡션 (해시태그 포함)

    Returns:
        {"success": True, "post_id": "...", "permalink": "..."}
        또는 {"success": False, "error": "..."}
    """
    access_token = os.environ.get('INSTAGRAM_ACCESS_TOKEN', '')
    ig_user_id = os.environ.get('INSTAGRAM_BUSINESS_ID', '')

    if not access_token or not ig_user_id:
        return {"success": False, "error": "Instagram 인증 정보 없음"}

    if not image_urls:
        return {"success": False, "error": "업로드된 이미지 없음"}

    try:
        # === Step 1: 개별 미디어 컨테이너 생성 ===
        child_ids = []
        for i, url in enumerate(image_urls):
            container = _create_media_container(
                ig_user_id, access_token, url, is_carousel_item=True
            )
            if container:
                child_ids.append(container)
                print(f"   📦 슬라이드 {i+1} 컨테이너 생성: {container}")
            else:
                print(f"   ⚠️ 슬라이드 {i+1} 컨테이너 생성 실패")
                return {"success": False, "error": f"슬라이드 {i+1} 컨테이너 실패"}

            # API 레이트 리밋 방지
            time.sleep(1)

        # === Step 2: 캐러셀 컨테이너 생성 ===
        carousel_id = _create_carousel_container(
            ig_user_id, access_token, child_ids, caption
        )
        if not carousel_id:
            return {"success": False, "error": "캐러셀 컨테이너 생성 실패"}

        print(f"   🎠 캐러셀 컨테이너 생성: {carousel_id}")

        # 미디어 처리 대기 (Instagram 서버 측)
        time.sleep(5)

        # === Step 3: 발행 ===
        post_id = _publish_container(ig_user_id, access_token, carousel_id)
        if not post_id:
            return {"success": False, "error": "캐러셀 발행 실패"}

        # 발행 후 permalink 조회
        permalink = _get_permalink(post_id, access_token)

        print(f"   ✅ Instagram 발행 완료! Post ID: {post_id}")
        return {
            "success": True,
            "post_id": post_id,
            "permalink": permalink,
            "slides_count": len(image_urls)
        }

    except Exception as e:
        print(f"   ❌ Instagram 발행 중 오류: {e}")
        return {"success": False, "error": str(e)}


def publish_single_image(image_url: str, caption: str) -> dict:
    """단일 이미지 포스트 발행 (슬라이드 1장일 때).

    Args:
        image_url: 이미지 URL
        caption: 캡션

    Returns:
        {"success": True, "post_id": "..."} 또는 에러
    """
    access_token = os.environ.get('INSTAGRAM_ACCESS_TOKEN', '')
    ig_user_id = os.environ.get('INSTAGRAM_BUSINESS_ID', '')

    if not access_token or not ig_user_id:
        return {"success": False, "error": "Instagram 인증 정보 없음"}

    try:
        container_id = _create_media_container(
            ig_user_id, access_token, image_url, is_carousel_item=False,
            caption=caption
        )
        if not container_id:
            return {"success": False, "error": "미디어 컨테이너 생성 실패"}

        time.sleep(5)

        post_id = _publish_container(ig_user_id, access_token, container_id)
        if not post_id:
            return {"success": False, "error": "발행 실패"}

        permalink = _get_permalink(post_id, access_token)

        return {
            "success": True,
            "post_id": post_id,
            "permalink": permalink,
            "slides_count": 1
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# ─── 내부 함수들 ───────────────────────────────────────


def _create_media_container(ig_user_id: str, token: str,
                            image_url: str, is_carousel_item: bool = False,
                            caption: str = "") -> str | None:
    """개별 미디어 컨테이너 생성."""
    url = f"{GRAPH_API_BASE}/{ig_user_id}/media"
    params = {
        "image_url": image_url,
        "access_token": token,
    }

    if is_carousel_item:
        params["is_carousel_item"] = "true"
    else:
        params["caption"] = caption

    resp = requests.post(url, data=params, timeout=30)
    data = resp.json()

    if "id" in data:
        return data["id"]

    print(f"   ⚠️ 컨테이너 생성 에러: {data.get('error', data)}")
    return None


def _create_carousel_container(ig_user_id: str, token: str,
                               children: list, caption: str) -> str | None:
    """캐러셀 컨테이너 생성."""
    url = f"{GRAPH_API_BASE}/{ig_user_id}/media"
    params = {
        "caption": caption,
        "media_type": "CAROUSEL",
        "children": ",".join(children),
        "access_token": token,
    }

    resp = requests.post(url, data=params, timeout=30)
    data = resp.json()

    if "id" in data:
        return data["id"]

    print(f"   ⚠️ 캐러셀 컨테이너 에러: {data.get('error', data)}")
    return None


def _publish_container(ig_user_id: str, token: str,
                       container_id: str) -> str | None:
    """미디어 컨테이너 발행."""
    url = f"{GRAPH_API_BASE}/{ig_user_id}/media_publish"
    params = {
        "creation_id": container_id,
        "access_token": token,
    }

    # 최대 3회 재시도 (미디어 처리 지연 대응)
    for attempt in range(3):
        resp = requests.post(url, data=params, timeout=30)
        data = resp.json()

        if "id" in data:
            return data["id"]

        error = data.get("error", {})
        error_code = error.get("code", 0)

        # 미디어 아직 처리 중 → 대기 후 재시도
        if error_code == 9:
            wait = 10 * (attempt + 1)
            print(f"   ⏳ 미디어 처리 중... {wait}초 대기 (시도 {attempt+1}/3)")
            time.sleep(wait)
            continue

        print(f"   ⚠️ 발행 에러: {error}")
        return None

    print("   ⚠️ 발행 재시도 초과")
    return None


def _get_permalink(post_id: str, token: str) -> str:
    """발행된 포스트의 permalink 조회."""
    try:
        url = f"{GRAPH_API_BASE}/{post_id}"
        params = {
            "fields": "permalink",
            "access_token": token,
        }
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()
        return data.get("permalink", "")
    except Exception:
        return ""


def check_api_status() -> dict:
    """Instagram API 연결 상태 확인."""
    access_token = os.environ.get('INSTAGRAM_ACCESS_TOKEN', '')
    ig_user_id = os.environ.get('INSTAGRAM_BUSINESS_ID', '')

    if not access_token or not ig_user_id:
        return {"connected": False, "error": "환경변수 미설정"}

    try:
        url = f"{GRAPH_API_BASE}/{ig_user_id}"
        params = {
            "fields": "name,username,media_count",
            "access_token": access_token,
        }
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()

        if "error" in data:
            return {"connected": False, "error": data["error"].get("message", "")}

        return {
            "connected": True,
            "username": data.get("username", ""),
            "name": data.get("name", ""),
            "media_count": data.get("media_count", 0),
        }

    except Exception as e:
        return {"connected": False, "error": str(e)}
