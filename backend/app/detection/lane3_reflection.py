# backend/app/detection/lane3_reflection.py
# Lane 3: Bitemporal Asset Reflection Diff Engine

from datetime import date
from typing import Optional, Dict, Any
from backend.app.detection.temporal_guard import check_temporal_lag_guardrail

def evaluate_lane3_reflection(
    canonical_asset_type: str,
    target_quantity: int,
    completion_date: Optional[date],
    pre_state: Optional[Dict[str, Any]],
    post_state: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evaluates physical asset reflection between pre-sanction baseline (T-1) and post-completion (T+1):
    1. Runs Temporal Lag Guardrail check.
    2. Measures physical delta against target quantity.
    3. Flags Critical Reflection Gap (score 0.90) or Partial Reflection Gap (score 0.50).
    """
    if not pre_state:
        return {
            "lane": "ASSET_REFLECTION",
            "score": 0.0,
            "status": "MISSING_PRE_SANCTION_BASELINE",
            "explanation": "Pre-sanction baseline school state record unavailable."
        }

    post_freeze_date = post_state.get("data_freeze_date") if post_state else None
    
    # Check Temporal Lag Guardrail
    guard = check_temporal_lag_guardrail(completion_date, post_freeze_date)
    if not guard["eligible"]:
        return {
            "lane": "ASSET_REFLECTION",
            "score": 0.0,
            "status": guard["status"],
            "explanation": guard["reason"]
        }

    # Asset delta calculation
    if canonical_asset_type == "ADDITIONAL_CLASSROOM":
        pre_val = pre_state.get("total_classrooms", 0)
        post_val = post_state.get("total_classrooms", 0)
    elif canonical_asset_type == "TOILET_BLOCK":
        pre_val = pre_state.get("functional_girls_toilets", 0) + pre_state.get("functional_boys_toilets", 0)
        post_val = post_state.get("functional_girls_toilets", 0) + post_state.get("functional_boys_toilets", 0)
    elif canonical_asset_type == "COMPUTER_LAB":
        pre_val = 1 if pre_state.get("has_computer_lab") else 0
        post_val = 1 if post_state.get("has_computer_lab") else 0
    else:
        pre_val = pre_state.get("total_classrooms", 0)
        post_val = post_state.get("total_classrooms", 0)

    observed_delta = post_val - pre_val
    expected_delta = max(1, target_quantity)

    if observed_delta <= 0:
        return {
            "lane": "ASSET_REFLECTION",
            "score": 0.90,
            "status": "CRITICAL_REFLECTION_GAP",
            "observed_delta": observed_delta,
            "expected_delta": expected_delta,
            "explanation": f"Observed physical delta ({observed_delta}) is <= 0 despite project completion (expected +{expected_delta})."
        }
    elif observed_delta < expected_delta:
        return {
            "lane": "ASSET_REFLECTION",
            "score": 0.50,
            "status": "PARTIAL_REFLECTION_GAP",
            "observed_delta": observed_delta,
            "expected_delta": expected_delta,
            "explanation": f"Observed physical delta (+{observed_delta}) is less than sanctioned quantity (+{expected_delta})."
        }

    return {
        "lane": "ASSET_REFLECTION",
        "score": 0.0,
        "status": "ASSET_FULLY_REFLECTED",
        "observed_delta": observed_delta,
        "expected_delta": expected_delta,
        "explanation": f"Physical asset fully verified in post-completion census (+{observed_delta} units)."
    }
