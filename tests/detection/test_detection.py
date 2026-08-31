# tests/detection/test_detection.py
# Anomaly detection, temporal lag guardrail, and physics validation tests

from datetime import date
import pytest
from backend.app.detection.lane1_statutory import evaluate_lane1_statutory
from backend.app.detection.lane2_need import evaluate_lane2_need
from backend.app.detection.lane3_reflection import evaluate_lane3_reflection
from backend.app.detection.lane4_physics import evaluate_lane4_physics
from backend.app.detection.temporal_guard import check_temporal_lag_guardrail
from backend.app.detection.exceptions import apply_exception_context
from backend.app.fusion.scoring import compute_investigation_priority_index

def test_lane1_statutory_private_school_violation():
    res = evaluate_lane1_statutory(
        school_management="PRIVATE_UNAIDED",
        recommendation_date=date(2023, 1, 1),
        sanction_date=date(2023, 1, 20),
        sanction_cost=500000.0
    )
    assert res["score"] == 1.0
    assert len(res["violations"]) > 0
    assert "PRIVATE_UNAIDED" in res["violations"][0]

def test_lane1_statutory_delay_violation():
    res = evaluate_lane1_statutory(
        school_management="GOVERNMENT",
        recommendation_date=date(2023, 1, 1),
        sanction_date=date(2023, 4, 1), # 90 days (> 75d)
        sanction_cost=500000.0
    )
    assert res["score"] == 0.40
    assert "STATUTORY_SANCTION_WINDOW_EXCEEDED" in res["violations"][0]

def test_lane3_temporal_lag_guardrail_suppression():
    # Project completed Oct 15, 2024; census frozen Sep 30, 2024 (prior to completion)
    guard = check_temporal_lag_guardrail(
        completion_date=date(2024, 10, 15),
        post_freeze_date=date(2024, 9, 30)
    )
    assert guard["eligible"] is False
    assert guard["status"] == "SUPPRESSED_CENSUS_LAG"

    # Evaluator hold should result in 0 score penalty in Lane 3
    refl = evaluate_lane3_reflection(
        canonical_asset_type="ADDITIONAL_CLASSROOM",
        target_quantity=2,
        completion_date=date(2024, 10, 15),
        pre_state={"total_classrooms": 6, "data_freeze_date": date(2023, 9, 30)},
        post_state={"total_classrooms": 6, "data_freeze_date": date(2024, 9, 30)}
    )
    assert refl["score"] == 0.0
    assert refl["status"] == "SUPPRESSED_CENSUS_LAG"

def test_lane3_critical_reflection_gap():
    # Valid post-completion census frozen 1 year later shows ZERO classroom increase
    refl = evaluate_lane3_reflection(
        canonical_asset_type="ADDITIONAL_CLASSROOM",
        target_quantity=2,
        completion_date=date(2023, 5, 8),
        pre_state={"total_classrooms": 7, "data_freeze_date": date(2022, 9, 30)},
        post_state={"total_classrooms": 7, "data_freeze_date": date(2024, 9, 30)}
    )
    assert refl["score"] == 0.90
    assert refl["status"] == "CRITICAL_REFLECTION_GAP"
    assert refl["observed_delta"] == 0

def test_lane4_physics_velocity_violation():
    # 23 days for structural RCC additional classroom violates IS 456 standard
    res = evaluate_lane4_physics(
        canonical_asset_type="ADDITIONAL_CLASSROOM",
        sanction_date=date(2023, 4, 15),
        completion_date=date(2023, 5, 8)
    )
    assert res["score"] == 0.70 or res["score"] == 0.95
    assert res["violation"] is not None
    assert "COMPRESSED_CIVIL_TIMELINE" in res["violation"] or "PHYSICALLY_IMPOSSIBLE" in res["violation"]

def test_exception_dilapidated_room_replacement():
    lane_scores = {"ASSET_REFLECTION": {"score": 0.90}}
    school_master = {"operational_status": "OPERATIONAL"}
    historical_states = [
        {"academic_year": "2022-23", "classrooms_dilapidated": 2},
        {"academic_year": "2024-25", "classrooms_dilapidated": 0}
    ]
    exceptions = apply_exception_context(lane_scores, school_master, historical_states)
    assert len(exceptions) == 1
    assert exceptions[0]["type"] == "STRUCTURE_REPLACEMENT_EXCEPTION"
    assert exceptions[0]["reduction"] == 0.40
