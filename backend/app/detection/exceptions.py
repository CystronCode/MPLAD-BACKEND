# backend/app/detection/exceptions.py
# Exception Context & Self-Criticism Engine

from typing import List, Dict, Any

def apply_exception_context(
    lane_scores: Dict[str, Any],
    school_master: Dict[str, Any],
    historical_states: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Evaluates contextual administrative records to identify benign explanations:
    1. Structure Replacement: Demolished dilapidated classrooms offset newly constructed rooms (net delta zero).
    2. School Merger: Consolidation with nearby schools explains enrollment shifts.
    """
    adjustments: List[Dict[str, Any]] = []

    # Exception 1: Dilapidated Room Replacement
    refl_score = lane_scores.get("ASSET_REFLECTION", {}).get("score", 0.0)
    if refl_score > 0.0 and len(historical_states) >= 2:
        sorted_states = sorted(historical_states, key=lambda s: s.get("academic_year", ""))
        pre_dilap = sorted_states[0].get("classrooms_dilapidated", 0)
        post_dilap = sorted_states[-1].get("classrooms_dilapidated", 0)

        if pre_dilap > post_dilap:
            rooms_demolished = pre_dilap - post_dilap
            adjustments.append({
                "type": "STRUCTURE_REPLACEMENT_EXCEPTION",
                "reduction": 0.40,
                "reason": f"School demolished {rooms_demolished} unserviceable dilapidated classrooms during replacement construction."
            })

    # Exception 2: School Merger Event
    if school_master.get("operational_status") == "MERGED":
        adjustments.append({
            "type": "SCHOOL_MERGER_EVENT",
            "reduction": 0.50,
            "reason": "School underwent administrative consolidation; demographic fluctuations are benign."
        })

    return adjustments
