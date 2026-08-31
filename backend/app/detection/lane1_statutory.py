# backend/app/detection/lane1_statutory.py
# Lane 1: Statutory Guidelines & Beneficiary Compliance Engine

from datetime import date
from typing import Optional, Dict, Any, List

def evaluate_lane1_statutory(
    school_management: str,
    recommendation_date: Optional[date],
    sanction_date: Optional[date],
    sanction_cost: float
) -> Dict[str, Any]:
    """
    Evaluates statutory compliance under MPLADS Guidelines 2023:
    1. Chapter 6.1: Private unaided institutions are strictly ineligible for infrastructure grants.
    2. Chapter 4: Sanction window exceeding 75 days from MP recommendation is an administrative delay irregularity.
    """
    violations: List[str] = []
    score = 0.0

    # Rule 1: Private Unaided Beneficiary Gating
    if school_management and school_management.upper() == "PRIVATE_UNAIDED":
        violations.append("RULE_VIOLATION_PRIVATE_UNAIDED_BENEFICIARY (MPLADS Guidelines Ch 6.1)")
        score = 1.0

    # Rule 2: 75-Day Sanction Window
    if recommendation_date and sanction_date:
        days_to_sanction = (sanction_date - recommendation_date).days
        if days_to_sanction < 0:
            violations.append(f"RETROACTIVE_SANCTION_DATE_ANOMALY (Sanction {sanction_date} prior to Recom {recommendation_date})")
            score = max(score, 0.80)
        elif days_to_sanction > 75:
            violations.append(f"STATUTORY_SANCTION_WINDOW_EXCEEDED ({days_to_sanction} days vs max allowable 75 days)")
            score = max(score, 0.40)

    return {
        "lane": "STATUTORY",
        "score": round(score, 2),
        "violations": violations
    }
