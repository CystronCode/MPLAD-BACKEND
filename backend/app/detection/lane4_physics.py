# backend/app/detection/lane4_physics.py
# Lane 4: Timeline Physics & Velocity Engine (IS 456 Construction Bounds)

from datetime import date
from typing import Optional, Dict, Any

def evaluate_lane4_physics(
    canonical_asset_type: str,
    sanction_date: Optional[date],
    completion_date: Optional[date]
) -> Dict[str, Any]:
    """
    Evaluates civil engineering timeline plausibility against IS 456 concrete curing specifications:
    - Structural RCC civil construction (Classrooms) requires minimum 28 days wet curing, 45 days total completion.
    - Minor civil repairs / installations require minimum 21 days.
    """
    if not sanction_date or not completion_date:
        return {
            "lane": "TIMELINE_PHYSICS",
            "score": 0.0,
            "note": "SANCTION_OR_COMPLETION_DATE_UNAVAILABLE"
        }

    duration_days = (completion_date - sanction_date).days

    if duration_days < 0:
        return {
            "lane": "TIMELINE_PHYSICS",
            "score": 1.0,
            "violation": f"RETROACTIVE_COMPLETION_DATE_ANOMALY (Completed {completion_date} prior to Sanction {sanction_date})",
            "duration_days": duration_days
        }

    min_bound = 45 if canonical_asset_type == "ADDITIONAL_CLASSROOM" else 21

    if duration_days < 21:
        return {
            "lane": "TIMELINE_PHYSICS",
            "score": 0.95,
            "violation": f"PHYSICALLY_IMPOSSIBLE_DURATION ({duration_days} days reported vs absolute minimum 21 days for civil works)",
            "duration_days": duration_days
        }
    elif duration_days < min_bound:
        return {
            "lane": "TIMELINE_PHYSICS",
            "score": 0.70,
            "violation": f"COMPRESSED_CIVIL_TIMELINE ({duration_days} days reported vs mandatory {min_bound}-day RCC curing standard)",
            "duration_days": duration_days
        }

    return {
        "lane": "TIMELINE_PHYSICS",
        "score": 0.0,
        "violation": None,
        "duration_days": duration_days
    }
