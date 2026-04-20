"""Day 3 테스트: uploader, publisher, reviewer 모듈 검증.

API 키 없이도 로직 흐름과 폴백 동작을 검증한다.
"""

import os
import sys
import json
import tempfile

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_uploader_import():
    """uploader 모듈 임포트 테스트."""
    from src.uploader import upload_images, delete_images, init_cloudinary
    print("✅ uploader 모듈 임포트 성공")


def test_uploader_no_api():
    """API 키 없이 업로드 시 에러 처리."""
    # 환경변수 제거
    for key in ['CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET']:
        os.environ.pop(key, None)

    from src.uploader import upload_images

    # 임시 테스트 이미지 생성
    from PIL import Image
    with tempfile.TemporaryDirectory() as tmpdir:
        img = Image.new('RGB', (100, 100), (26, 10, 46))
        path = os.path.join(tmpdir, 'test.png')
        img.save(path)

        result = upload_images([path], "test_content")

        # API 없이도 폴백 결과 반환 (로컬 경로)
        assert len(result) == 1
        assert "error" in result[0]  # 에러 포함
        assert result[0]["url"] == path  # 로컬 경로 폴백
        print(f"✅ API 없이 업로드 폴백 정상: error={result[0]['error'][:50]}...")


def test_publisher_import():
    """publisher 모듈 임포트 테스트."""
    from src.publisher import (
        publish_carousel, publish_single_image,
        check_api_status
    )
    print("✅ publisher 모듈 임포트 성공")


def test_publisher_no_credentials():
    """Instagram 인증 없이 발행 시 적절한 에러."""
    os.environ.pop('INSTAGRAM_ACCESS_TOKEN', None)
    os.environ.pop('INSTAGRAM_BUSINESS_ID', None)

    from src.publisher import publish_carousel, publish_single_image, check_api_status

    # 캐러셀 발행
    result = publish_carousel(
        ["https://example.com/img1.png", "https://example.com/img2.png"],
        "테스트 캡션"
    )
    assert result["success"] is False
    assert "인증" in result["error"]
    print(f"✅ 캐러셀 발행 인증 없음 처리: {result['error']}")

    # 단일 이미지 발행
    result2 = publish_single_image("https://example.com/img.png", "테스트")
    assert result2["success"] is False
    print(f"✅ 단일 이미지 발행 인증 없음 처리: {result2['error']}")

    # API 상태 확인
    status = check_api_status()
    assert status["connected"] is False
    print(f"✅ API 상태 확인: connected={status['connected']}")


def test_publisher_carousel_flow():
    """캐러셀 발행 흐름 (빈 이미지 리스트)."""
    os.environ['INSTAGRAM_ACCESS_TOKEN'] = 'test_token'
    os.environ['INSTAGRAM_BUSINESS_ID'] = 'test_id'

    from src.publisher import publish_carousel

    # 빈 이미지 리스트
    result = publish_carousel([], "테스트")
    assert result["success"] is False
    assert "이미지 없음" in result["error"]
    print(f"✅ 빈 이미지 리스트 처리: {result['error']}")

    # 정리
    os.environ.pop('INSTAGRAM_ACCESS_TOKEN', None)
    os.environ.pop('INSTAGRAM_BUSINESS_ID', None)


def test_reviewer_import():
    """reviewer 모듈 임포트 테스트."""
    from src.reviewer import (
        send_preview, send_publish_result,
        send_weekly_report
    )
    print("✅ reviewer 모듈 임포트 성공")


def test_reviewer_no_telegram():
    """Telegram 미설정 시 graceful 처리."""
    os.environ.pop('TELEGRAM_BOT_TOKEN', None)
    os.environ.pop('TELEGRAM_CHAT_ID', None)

    from src.reviewer import send_preview, send_publish_result, send_weekly_report

    # 미리보기 전송
    content = {
        "id": "W0001",
        "title": "좀비 곰팡이의 비밀",
        "type": "did_you_know",
        "slides": [{"slide": 1, "text": "테스트"}]
    }
    result = send_preview(content, ["/tmp/test.png"], "테스트 캡션")
    assert result["sent"] is False
    print(f"✅ Telegram 미설정 미리보기: sent={result['sent']}")

    # 발행 결과 알림
    ok = send_publish_result("W0001", {"success": True, "post_id": "123"})
    assert ok is False
    print(f"✅ Telegram 미설정 발행 알림: {ok}")

    # 주간 리포트
    ok2 = send_weekly_report([{"title": "테스트", "type": "quiz", "scheduled_date": "2026-04-21"}])
    assert ok2 is False
    print(f"✅ Telegram 미설정 주간 리포트: {ok2}")


def test_reviewer_summary_build():
    """미리보기 요약 텍스트 빌드."""
    from src.reviewer import _build_summary

    content = {
        "id": "W0003",
        "title": "좀비 서바이벌 5가지 팁",
        "type": "survival_skill",
        "scheduled_date": "2026-04-24",
        "slides": [
            {"slide": 1, "text": "서바이벌 팁 #1"},
            {"slide": 2, "text": "서바이벌 팁 #2"},
            {"slide": 3, "text": "서바이벌 팁 #3"},
        ]
    }
    caption = "좀비파크에서 살아남는 법 🧟\n\n#좀비파크 #서바이벌"

    summary = _build_summary(content, caption)
    assert "W0003" in summary
    assert "survival_skill" in summary
    assert "3장" in summary
    assert "서바이벌 팁 #1" in summary
    print(f"✅ 요약 텍스트 빌드 정상 (길이: {len(summary)}자)")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  Day 3 모듈 테스트: 업로드 + 발행 + 알림")
    print("="*50 + "\n")

    tests = [
        test_uploader_import,
        test_uploader_no_api,
        test_publisher_import,
        test_publisher_no_credentials,
        test_publisher_carousel_flow,
        test_reviewer_import,
        test_reviewer_no_telegram,
        test_reviewer_summary_build,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} 실패: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"  결과: {passed} 통과 / {failed} 실패")
    print(f"{'='*50}\n")
