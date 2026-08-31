# backend/app/detection/lane2_need.py
# Lane 2: Institutional Need & Demographic Siting Engine

from typing import List, Dict, Any

def evaluate_lane2_need(
    annual_states: List[Dict[str, Any]],
    target_quantity: int
) -> Dict[str, Any]:
    """
    Evaluates institutional siting efficiency:
    1. Student-to-Classroom Ratio (SCR): Measures underutilization (< 15 pupils/classroom).
    2. Longitudinal Enrollment Trend: Measures multi-year demographic decline (slope < 0).
    """
    if not annual_states or len(annual_states) < 1:
        return {
            "lane": "INSTITUTIONAL_NEED",
            "score": 0.0,
            "note": "INSUFFICIENT_HISTORICAL_DATA"
        }

    sorted_states = sorted(annual_states, key=lambda s: s.get("academic_year", ""))
    latest = sorted_states[-1]

    # Student-to-Classroom Ratio
    total_rooms = max(1, latest.get("total_classrooms", 1))
    total_enr = latest.get("total_enrollment", 0)
    scr = total_enr / total_rooms

    # If SCR < 15, calculate underutilization score (lower SCR -> higher risk of siting redundancy)
    ratio_score = max(0.0, min(1.0, (15.0 - scr) / 15.0)) if scr < 15.0 else 0.0

    # 3-Year Enrollment Growth Slope
    if len(sorted_states) >= 2:
        baseline_enr = max(1, sorted_states[0].get("total_enrollment", 1))
        latest_enr = sorted_states[-1].get("total_enrollment", 0)
        enr_growth = (latest_enr - baseline_enr) / baseline_enr
        trend_score = max(0.0, min(1.0, -enr_growth)) if enr_growth < 0 else 0.0
    else:
        enr_growth = 0.0
        trend_score = 0.0

    need_score = (0.60 * ratio_score) + (0.40 * trend_score)

    return {
        "lane": "INSTITUTIONAL_NEED",
        "score": round(need_score, 3),
        "metrics": {
            "latest_scr": round(scr, 2),
            "3yr_enrollment_growth": round(enr_growth, 3),
            "ratio_score": round(ratio_score, 3),
            "trend_score": round(trend_score, 3)
        }
    }
