#!/usr/bin/env python3
"""좀비파크 카드뉴스 인사이트 수집.

매일 21:00 KST GitHub Actions에서 실행.
파이프라인: 인사이트 수집 → performance_log 업데이트 → 주간 분석 (일요일) → 로깅
"""

import sys
import os
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent_enhancer import update_performance_insights, generate_weekly_analysis
from src.logger import log_insights_collected, log_error

KST = timezone(timedelta(hours=9))


def run_collect_insights():
    """인사이트 수집 파이프라인."""
    now = datetime.now(KST)
    print(f"\n{'='*60}")
    print(f"  📈 좀비파크 인사이트 수집")
    print(f"  📅 {now.strftime('%Y-%m-%d %H:%M KST')} ({now.strftime('%A')})")
    print(f"{'='*60}\n")

    try:
        # ─── Step 1: 인사이트 수집 ───
        print("📊 Step 1: Instagram 인사이트 수집")
        updated_count = update_performance_insights()
        print(f"   ✅ {updated_count}개 포스트 인사이트 업데이트")

        # ─── Step 2: 주간 분석 (일요일에만, KST 기준) ───
        kst_now = datetime.now(KST)
        if kst_now.weekday() == 6:  # 일요일 (KST 기준)
            print("\n🧠 Step 2: 주간 성과 분석")
            analysis = generate_weekly_analysis()

            if analysis:
                avg = analysis.get("overall_avg_energy", 0)
                best = analysis.get("best_post", {})
                print(f"   ✅ 주간 분석 완료")
                print(f"      평균 에너지: {avg}")
                print(f"      베스트: {best.get('title', 'N/A')} "
                      f"(에너지: {best.get('energy', 0)})")

                # Discord 로깅
                log_insights_collected(
                    analysis.get("period_posts", 0),
                    avg
                )
            else:
                print("   ⚠️ 분석할 데이터 없음")
        else:
            print("\n⏭️ Step 2: 주간 분석은 일요일에 실행됩니다.")

        print(f"\n{'='*60}")
        print(f"  ✅ 인사이트 수집 완료!")
        print(f"{'='*60}\n")

        return True

    except Exception as e:
        error_msg = f"인사이트 수집 예외: {str(e)}"
        print(f"\n❌ {error_msg}")
        log_error("collect_insights", error_msg)
        return False


if __name__ == "__main__":
    success = run_collect_insights()
    sys.exit(0 if success else 1)
