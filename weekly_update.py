#!/usr/bin/env python3
"""좀비파크 카드뉴스 주간 콘텐츠 생성.

매주 금요일 10:00 KST GitHub Actions에서 실행.
파이프라인: 옵시디언 스캔 → 7개 콘텐츠 생성 → 전략가 강화 → 스케줄 저장 → 알림
"""

import sys
import os
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.scanner import scan_obsidian_folder
from src.content_builder import build_weekly_content, save_weekly_content
from src.agent_enhancer import strategy_enhance
from src.reviewer import send_weekly_report
from src.logger import log_weekly_generation, log_error

KST = timezone(timedelta(hours=9))


def run_weekly_update():
    """주간 콘텐츠 생성 파이프라인."""
    now = datetime.now(KST)
    print(f"\n{'='*60}")
    print(f"  📋 좀비파크 주간 콘텐츠 생성")
    print(f"  📅 {now.strftime('%Y-%m-%d %H:%M KST')}")
    print(f"{'='*60}\n")

    # 옵시디언 폴더 경로 (GitHub Actions 환경)
    obsidian_path = os.environ.get(
        'OBSIDIAN_VAULT_PATH',
        'obsidian_data'  # 기본 경로 (repo 내)
    )

    try:
        # ─── Step 1: 옵시디언 폴더 스캔 ───
        print("🔍 Step 1: 옵시디언 폴더 스캔")
        changes = scan_obsidian_folder(obsidian_path)

        new_count = len(changes.get("new_files", []))
        mod_count = len(changes.get("modified_files", []))
        print(f"   ✅ 새 파일: {new_count}, 수정됨: {mod_count}")

        # ─── Step 2: AI 콘텐츠 7개 생성 ───
        print("\n🤖 Step 2: AI 콘텐츠 생성 (7개)")
        contents = build_weekly_content(changes)

        if not contents:
            print("   ⚠️ 콘텐츠 생성 실패")
            log_error("content_builder", "주간 콘텐츠 생성 실패")
            return False

        print(f"   ✅ {len(contents)}개 콘텐츠 생성 완료")

        # ─── Step 3: 전략가 에이전트 강화 ───
        print("\n🎯 Step 3: 전략가 에이전트")
        contents = strategy_enhance(contents)
        print(f"   ✅ 전략 메타데이터 추가 완료")

        # ─── Step 4: 저장 ───
        print("\n💾 Step 4: 콘텐츠 저장")
        save_weekly_content(contents)
        print(f"   ✅ content_pool.json + next_week_schedule.json 업데이트")

        # ─── Step 5: 알림 ───
        print("\n📱 Step 5: 알림 전송")
        send_weekly_report(contents)
        log_weekly_generation(contents)

        # 요약 출력
        print(f"\n{'='*60}")
        print(f"  ✅ 주간 업데이트 완료! {len(contents)}개 콘텐츠 준비됨")
        print(f"{'='*60}")
        for c in contents:
            print(f"  📌 {c.get('scheduled_date', '?')} "
                  f"({c.get('type', '')}): {c.get('title', '')}")
        print()

        return True

    except Exception as e:
        error_msg = f"주간 업데이트 예외: {str(e)}"
        print(f"\n❌ {error_msg}")
        log_error("weekly_update", error_msg)
        return False


if __name__ == "__main__":
    success = run_weekly_update()
    sys.exit(0 if success else 1)
