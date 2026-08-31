# tests/e2e/test_adversarial_suite.py
# Complete 15-scenario Adversarial Verification Suite for SIH26102 MEEV

from datetime import date
import pytest
from backend.app.normalization.taxonomy import normalize_asset_description, CanonicalAssetType
from backend.app.resolution.matcher import calculate_composite_match_score
from backend.app.detection.lane1_statutory import evaluate_lane1_statutory
from backend.app.detection.lane2_need import evaluate_lane2_need
from backend.app.detection.lane3_reflection import evaluate_lane3_reflection
from backend.app.detection.lane4_physics import evaluate_lane4_physics
from backend.app.detection.temporal_guard import check_temporal_lag_guardrail
from backend.app.detection.exceptions import apply_exception_context
from backend.app.fusion.scoring import compute_investigation_priority_index
from backend.app.explainability.graph_builder import build_case_evidence_graph
from backend.app.audit.hash_chain import compute_record_hash, verify_audit_chain, GENESIS_HASH

def test_adv_01_standard_school_match():
    score, status = calculate_composite_match_score(
        "Construction of 2 rooms at GHS Rampur",
        "Government High School Rampur",
        (31.1423, 77.1724), (31.1421, 77.1722)
    )
    assert score >= 0.85
    assert status == "AUTO_ACCEPTED"

def test_adv_02_renamed_school_reverse_spatial_fallback():
    score, status = calculate_composite_match_score(
        "Shaheed Bhagat Singh Memorial High School",
        "Government High School Rampur",
        (31.1423, 77.1724), (31.1421, 77.1722)
    )
    assert score >= 0.85
    assert "REVERSE_SPATIAL" in status

def test_adv_03_distant_collision_spatial_rejection():
    score, status = calculate_composite_match_score(
        "GHS Rampur", "Government High School Rampur",
        (31.1423, 77.1724), (31.2500, 77.3500)
    )
    assert score == 0.0
    assert "SPATIAL_REJECT" in status

def test_adv_04_census_lag_suppression():
    guard = check_temporal_lag_guardrail(date(2024, 10, 15), date(2024, 9, 30))
    assert guard["eligible"] is False
    assert guard["status"] == "SUPPRESSED_CENSUS_LAG"

def test_adv_05_concrete_curing_velocity_violation():
    res = evaluate_lane4_physics("ADDITIONAL_CLASSROOM", date(2023, 4, 15), date(2023, 5, 8))
    assert res["score"] >= 0.70
    assert res["violation"] is not None

def test_adv_06_statutory_private_school_flag():
    res = evaluate_lane1_statutory("PRIVATE_UNAIDED", date(2023, 1, 1), date(2023, 1, 20), 500000.0)
    assert res["score"] == 1.0

def test_adv_07_75_day_sanction_window_delay():
    res = evaluate_lane1_statutory("GOVERNMENT", date(2023, 1, 1), date(2023, 4, 1), 500000.0)
    assert res["score"] == 0.40

def test_adv_08_critical_asset_reflection_gap():
    res = evaluate_lane3_reflection(
        "ADDITIONAL_CLASSROOM", 2, date(2023, 5, 8),
        {"total_classrooms": 7, "data_freeze_date": date(2022, 9, 30)},
        {"total_classrooms": 7, "data_freeze_date": date(2024, 9, 30)}
    )
    assert res["score"] == 0.90
    assert res["status"] == "CRITICAL_REFLECTION_GAP"

def test_adv_09_dilapidated_room_demolition_exception():
    exc = apply_exception_context(
        {"ASSET_REFLECTION": {"score": 0.90}},
        {"operational_status": "OPERATIONAL"},
        [{"academic_year": "2022-23", "classrooms_dilapidated": 2},
         {"academic_year": "2024-25", "classrooms_dilapidated": 0}]
    )
    assert len(exc) == 1
    assert exc[0]["reduction"] == 0.40

def test_adv_10_compound_risk_scoring_and_tier_3():
    lane_scores = {
        "STATUTORY": {"score": 0.80},
        "INSTITUTIONAL_NEED": {"score": 0.45},
        "ASSET_REFLECTION": {"score": 0.90},
        "TIMELINE_PHYSICS": {"score": 0.95}
    }
    fusion = compute_investigation_priority_index(lane_scores, [], mean_confidence=0.92)
    assert fusion["ipi_score"] >= 70.0
    assert fusion["risk_tier"] == 3

def test_adv_11_provenance_graph_node_link_integrity():
    proj = {"project_id": "PRJ-2023-04567", "sanction_cost": 1240000, "canonical_asset_type": "ADDITIONAL_CLASSROOM"}
    school = {"udise_code": "02120100402", "name_canonical": "GHS Rampur"}
    lane_scores = {"ASSET_REFLECTION": {"score": 0.90, "observed_delta": 0, "expected_delta": 2}}
    graph = build_case_evidence_graph(proj, school, lane_scores)
    assert len(graph["nodes"]) >= 2
    assert len(graph["links"]) >= 1

def test_adv_12_audit_hash_chaining_and_tamper_detection():
    now = date.today()
    h1 = compute_record_hash({"action": "STEP_1"}, "ACTOR_1", now, GENESIS_HASH)
    h2 = compute_record_hash({"action": "STEP_2"}, "ACTOR_2", now, h1)

    chain = [
        {"payload": {"action": "STEP_1"}, "actor_id": "ACTOR_1", "recorded_at": now, "previous_hash": GENESIS_HASH, "current_hash": h1},
        {"payload": {"action": "STEP_2"}, "actor_id": "ACTOR_2", "recorded_at": now, "previous_hash": h1, "current_hash": h2}
    ]
    assert verify_audit_chain(chain) is True

    # Tampering check
    tampered_chain = [
        {"payload": {"action": "TAMPERED"}, "actor_id": "ACTOR_1", "recorded_at": now, "previous_hash": GENESIS_HASH, "current_hash": h1},
        {"payload": {"action": "STEP_2"}, "actor_id": "ACTOR_2", "recorded_at": now, "previous_hash": h1, "current_hash": h2}
    ]
    assert verify_audit_chain(tampered_chain) is False

def test_adv_13_asset_taxonomy_regex_coverage():
    types = [
        ("Const of girls toilet block", CanonicalAssetType.TOILET_BLOCK),
        ("Setup of ICT computer smart lab", CanonicalAssetType.COMPUTER_LAB),
        ("Const of physics science lab", CanonicalAssetType.SCIENCE_LAB),
        ("Provision of RO drinking water plant", CanonicalAssetType.DRINKING_WATER),
        ("Const of school boundary wall", CanonicalAssetType.BOUNDARY_WALL)
    ]
    for desc, expected in types:
        asset, _ = normalize_asset_description(desc)
        assert asset == expected

def test_adv_14_low_enrollment_need_calculation():
    states = [
        {"academic_year": "2022-23", "total_enrollment": 50, "total_classrooms": 5},
        {"academic_year": "2024-25", "total_enrollment": 20, "total_classrooms": 5}
    ]
    res = evaluate_lane2_need(states, 2)
    assert res["score"] >= 0.50
    assert res["metrics"]["latest_scr"] == 4.0

def test_adv_15_legitimate_project_clean_pass():
    refl = evaluate_lane3_reflection(
        "ADDITIONAL_CLASSROOM", 2, date(2023, 8, 30),
        {"total_classrooms": 12, "data_freeze_date": date(2022, 9, 30)},
        {"total_classrooms": 14, "data_freeze_date": date(2024, 9, 30)}
    )
    assert refl["score"] == 0.0
    assert refl["status"] == "ASSET_FULLY_REFLECTED"

    phys = evaluate_lane4_physics("ADDITIONAL_CLASSROOM", date(2023, 2, 20), date(2023, 8, 30))
    assert phys["score"] == 0.0
