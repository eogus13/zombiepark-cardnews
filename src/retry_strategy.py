"""자동 재시도 전략 모듈 — 실패 로그를 분석하여 재시도 전략을 결정한다.

파이프라인 실패 시:
1. failure_log.json에 실패 원인을 기록
2. 재시도 시 실패 로그를 읽어서 "이번에는 어떻게 할지" 전략 결정
3. 예: Gemini 503 → 폴백 텍스트 직접 사용 (API 호출 스킵)
      이미지 생성 실패 → 폴백 이미지로 바로 전환
      Instagram API 오류 → 대기 후 재시도
"""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

from src.utils import load_json, save_json

KST = timezone(timedelta(hours=9))
FAILURE_LOG_PATH = "data/failure_log.json"


def log_failure(step: str, error_type: str, error_msg: str,
                content_id: str = "", attempt: int = 1) -> None:
    """실패 정보를 failure_log.json에 기록.

    Args:
        step: 실패한 파이프라인 단계 (selector, text_generator, image_generator 등)
        error_type: 에러 분류 (api_503, api_timeout, parse_error, upload_fail 등)
        error_msg: 상세 에러 메시지
        content_id: 콘텐츠 ID
        attempt: 몇 번째 시도인지
    """
    log = load_json(FAILURE_LOG_PATH)
    if "failures" not in log:
        log["failures"] = []

    entry = {
        "timestamp": datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S"),
        "date": datetime.now(KST).strftime("%Y-%m-%d"),
        "step": step,
        "error_type": error_type,
        "error_msg": error_msg[:500],
        "content_id": content_id,
        "attempt": attempt,
        "resolved": False,
    }

    log["failures"].append(entry)

    # 최근 30일만 유지
    cutoff = (datetime.now(KST) - timedelta(days=30)).strftime("%Y-%m-%d")
    log["failures"] = [f for f in log["failures"] if f.get("date", "") >= cutoff]

    save_json(FAILURE_LOG_PATH, log)
    print(f"   📝 실패 로그 기록: [{step}] {error_type}")


def mark_resolved(date: str = None) -> None:
    """해당 날짜의 실패를 해결됨으로 표시."""
    if date is None:
        date = datetime.now(KST).strftime("%Y-%m-%d")

    log = load_json(FAILURE_LOG_PATH)
    for f in log.get("failures", []):
        if f.get("date") == date:
            f["resolved"] = True
    save_json(FAILURE_LOG_PATH, log)


def get_retry_strategy() -> dict:
    """오늘의 실패 로그를 분석하여 재시도 전략을 결정.

    Returns:
        {
            "should_retry": True/False,
            "attempt": 2,  # 몇 번째 재시도인지
            "skip_gemini_text": True/False,  # Gemini 텍스트 생성 건너뛰기
            "skip_gemini_agent": True/False,  # Gemini 에이전트 건너뛰기
            "force_fallback_images": True/False,  # 폴백 이미지 강제 사용
            "extra_wait_seconds": 0,  # Instagram API 등 대기 시간
            "reason": "설명 문자열",
            "today_failures": [...],  # 오늘의 실패 목록
        }
    """
    log = load_json(FAILURE_LOG_PATH)
    today = datetime.now(KST).strftime("%Y-%m-%d")

    today_failures = [
        f for f in log.get("failures", [])
        if f.get("date") == today and not f.get("resolved")
    ]

    if not today_failures:
        return {
            "should_retry": False,
            "attempt": 1,
            "skip_gemini_text": False,
            "skip_gemini_agent": False,
            "force_fallback_images": False,
            "extra_wait_seconds": 0,
            "reason": "오늘 실패 기록 없음 — 정상 실행",
            "today_failures": [],
        }

    # 최대 재시도 횟수 체크
    max_attempt = max(f.get("attempt", 1) for f in today_failures)
    if max_attempt >= 3:
        return {
            "should_retry": False,
            "attempt": max_attempt,
            "skip_gemini_text": False,
            "skip_gemini_agent": False,
            "force_fallback_images": False,
            "extra_wait_seconds": 0,
            "reason": f"오늘 이미 {max_attempt}회 시도 — 재시도 중단",
            "today_failures": today_failures,
        }

    # 실패 원인별 전략 결정
    failed_steps = {f["step"] for f in today_failures}
    error_types = {f.get("error_type", "") for f in today_failures}

    strategy = {
        "should_retry": True,
        "attempt": max_attempt + 1,
        "skip_gemini_text": False,
        "skip_gemini_agent": False,
        "force_fallback_images": False,
        "extra_wait_seconds": 0,
        "reason": "",
        "today_failures": today_failures,
    }

    reasons = []

    # Gemini API 관련 실패
    if any(t in error_types for t in ("api_503", "api_unavailable", "api_overloaded")):
        strategy["skip_gemini_text"] = True
        strategy["skip_gemini_agent"] = True
        reasons.append("Gemini API 불안정 → 폴백 텍스트 직접 사용")

    # 텍스트 생성 단계 실패
    if "text_generator" in failed_steps:
        strategy["skip_gemini_text"] = True
        reasons.append("텍스트 생성 실패 → 폴백 텍스트 사용")

    # 에이전트 실패 (치명적이지 않음)
    if "agent_enhancer" in failed_steps and len(failed_steps) == 1:
        strategy["skip_gemini_agent"] = True
        reasons.append("에이전트만 실패 → 에이전트 건너뛰고 재시도")

    # 이미지 생성 실패
    if "image_generator" in failed_steps:
        strategy["force_fallback_images"] = True
        reasons.append("이미지 생성 실패 → 폴백 이미지 강제 사용")

    # Instagram API 실패 (rate limit 등)
    if "publisher" in failed_steps:
        strategy["extra_wait_seconds"] = 60
        reasons.append("Instagram API 실패 → 60초 대기 후 재시도")

    # Cloudinary 업로드 실패
    if "uploader" in failed_steps:
        strategy["extra_wait_seconds"] = 30
        reasons.append("Cloudinary 실패 → 30초 대기 후 재시도")

    # 콘텐츠 선택 실패 (재시도 의미 없음)
    if "selector" in failed_steps:
        strategy["should_retry"] = False
        reasons.append("콘텐츠 없음 → 재시도 불가")

    strategy["reason"] = " | ".join(reasons) if reasons else "일반 재시도"

    return strategy


def get_failure_summary(days: int = 7) -> dict:
    """최근 N일간 실패 통계 요약.

    Returns:
        {
            "total_failures": 5,
            "resolved": 3,
            "unresolved": 2,
            "by_step": {"text_generator": 3, "publisher": 2},
            "by_type": {"api_503": 4, "upload_fail": 1},
            "most_common_step": "text_generator",
            "most_common_type": "api_503",
        }
    """
    log = load_json(FAILURE_LOG_PATH)
    cutoff = (datetime.now(KST) - timedelta(days=days)).strftime("%Y-%m-%d")

    recent = [f for f in log.get("failures", []) if f.get("date", "") >= cutoff]

    if not recent:
        return {"total_failures": 0, "resolved": 0, "unresolved": 0,
                "by_step": {}, "by_type": {},
                "most_common_step": "", "most_common_type": ""}

    by_step = {}
    by_type = {}
    resolved_count = 0

    for f in recent:
        step = f.get("step", "unknown")
        etype = f.get("error_type", "unknown")
        by_step[step] = by_step.get(step, 0) + 1
        by_type[etype] = by_type.get(etype, 0) + 1
        if f.get("resolved"):
            resolved_count += 1

    return {
        "total_failures": len(recent),
        "resolved": resolved_count,
        "unresolved": len(recent) - resolved_count,
        "by_step": by_step,
        "by_type": by_type,
        "most_common_step": max(by_step, key=by_step.get) if by_step else "",
        "most_common_type": max(by_type, key=by_type.get) if by_type else "",
    }
