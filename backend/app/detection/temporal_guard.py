# backend/app/detection/temporal_guard.py
# Temporal Lag Compensation Guardrail for UDISE+ Annual Census Cycles

from datetime import date
from typing import Optional, Dict, Any

def check_temporal_lag_guardrail(
    completion_date: Optional[date],
    post_freeze_date: Optional[date],
    min_buffer_days: int = 180
) -> Dict[str, Any]:
    """
    Temporal Invariant Check:
    Ensures post-completion census freeze date is at least 180 days after project completion date.
    Prevents false alarms caused by annual census lag.
    """
    if not completion_date:
        return {
            "eligible": False,
            "status": "PROJECT_NOT_MARKED_COMPLETED",
            "reason": "Project does not have a recorded completion date."
        }

    if not post_freeze_date:
        return {
            "eligible": False,
            "status": "PENDING_CENSUS_CYCLE",
            "reason": "Post-completion UDISE+ annual census has not been published yet. Guardrail active: 0 penalty."
        }

    delta_days = (post_freeze_date - completion_date).days

    if delta_days < min_buffer_days:
        return {
            "eligible": False,
            "status": "SUPPRESSED_CENSUS_LAG",
            "reason": f"Post-completion census was frozen only {delta_days} days after completion (min buffer is {min_buffer_days}d). Guardrail hold active."
        }

    return {
        "eligible": True,
        "status": "ELIGIBLE_FOR_REFLECTION_EVALUATION",
        "reason": f"Sufficient temporal buffer elapsed ({delta_days} days)."
    }
