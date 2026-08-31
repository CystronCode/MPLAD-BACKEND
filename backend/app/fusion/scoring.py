# backend/app/fusion/scoring.py
# Orthogonal Max-Pooling Evidence Fusion & IPI Scoring

from typing import Dict, List, Any
from contracts.models import RiskTier

WEIGHT_STATUTORY = 0.30
WEIGHT_NEED = 0.15
WEIGHT_REFLECTION = 0.35
WEIGHT_PHYSICS = 0.20

def compute_investigation_priority_index(
    lane_scores: Dict[str, Any],
    exception_adjustments: List[Dict[str, Any]],
    mean_confidence: float = 0.85
) -> Dict[str, Any]:
    """
    Computes the composite Investigation Priority Index (IPI) using dimension max-pooling:
    IPI = 100 * (0.30*S_stat + 0.15*max(S_need) + 0.35*S_refl + 0.20*S_phys) * compound_multiplier - exceptions
    """
    s_stat = float(lane_scores.get("STATUTORY", {}).get("score", 0.0))
    s_need = float(lane_scores.get("INSTITUTIONAL_NEED", {}).get("score", 0.0))
    s_refl = float(lane_scores.get("ASSET_REFLECTION", {}).get("score", 0.0))
    s_phys = float(lane_scores.get("TIMELINE_PHYSICS", {}).get("score", 0.0))

    # Determine Primary Anomaly Category
    primary_category = "NORMAL_COMPLIANT"
    if s_refl >= 0.85:
        primary_category = "CRITICAL_REFLECTION_GAP"
    elif s_phys >= 0.70:
        primary_category = "PHYSICAL_VELOCITY_VIOLATION"
    elif s_stat >= 0.80:
        primary_category = "STATUTORY_INELIGIBLE_BENEFICIARY"
    elif s_need >= 0.40:
        primary_category = "INSTITUTIONAL_SITING_INEFFICIENCY"

    # Base weighted sum
    base_score = (
        (WEIGHT_STATUTORY * s_stat) +
        (WEIGHT_NEED * s_need) +
        (WEIGHT_REFLECTION * s_refl) +
        (WEIGHT_PHYSICS * s_phys)
    )

    # Compound Urgency Multiplier: When multiple orthogonal high-severity anomalies co-occur
    compound_multiplier = 1.0
    if (s_refl >= 0.85 and s_phys >= 0.70) or (s_stat >= 0.80 and s_refl >= 0.85):
        compound_multiplier = 1.45

    ipi_raw = (base_score * compound_multiplier) * 100.0

    # Subtract legitimate administrative exceptions
    total_reduction = 0.0
    for exc in exception_adjustments:
        total_reduction += float(exc.get("reduction", 0.0)) * 100.0

    final_ipi = max(0.0, min(100.0, ipi_raw - total_reduction))

    # Calculate Confidence Interval Uncertainty Band
    uncertainty = 15.0 * (1.0 - mean_confidence)
    ipi_lower = max(0.0, final_ipi - uncertainty)
    ipi_upper = min(100.0, final_ipi + uncertainty)

    # Triage Tier Assignment
    if final_ipi >= 70.0:
        risk_tier = RiskTier.TIER_3_FIELD_INSPECTION.value
    elif final_ipi >= 35.0:
        risk_tier = RiskTier.TIER_2_DESK_REVIEW.value
    else:
        risk_tier = RiskTier.TIER_1_AUTO_ARCHIVE.value

    return {
        "ipi_score": round(final_ipi, 1),
        "ipi_lower": round(ipi_lower, 1),
        "ipi_upper": round(ipi_upper, 1),
        "risk_tier": risk_tier,
        "primary_category": primary_category,
        "base_score": round(base_score, 3),
        "compound_multiplier": compound_multiplier,
        "exception_reductions": round(total_reduction, 1)
    }
