#!/usr/bin/env python3
"""
scripts/run_demo_rehearsal.py
SIH26102 MEEV 4-Minute Winning Demo Flow Rehearsal Script
Validates the end-to-end flow for Case PRJ-2023-04567 (GHS Rampur).
"""

import sys
from datetime import date

# Configure UTF-8 for Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from backend.app.normalization.taxonomy import normalize_asset_description
from backend.app.resolution.matcher import calculate_composite_match_score
from backend.app.detection.lane1_statutory import evaluate_lane1_statutory
from backend.app.detection.lane2_need import evaluate_lane2_need
from backend.app.detection.lane3_reflection import evaluate_lane3_reflection
from backend.app.detection.lane4_physics import evaluate_lane4_physics
from backend.app.fusion.scoring import compute_investigation_priority_index
from backend.app.explainability.graph_builder import build_case_evidence_graph
from backend.app.notices.generator import generate_statutory_notice_pdf
from backend.app.audit.hash_chain import compute_record_hash, GENESIS_HASH

def run_demo():
    print("=" * 80)
    print("  SIH26102 — MEEV (MPLADS Education Ecosystem Validator)")
    print("  4-MINUTE WINNING DEMONSTRATION REHEARSAL CHECK")
    print("=" * 80)

    # 1. THE HOOK: e-SAKSHI Work Claim
    project_id = "PRJ-2023-04567"
    raw_desc = "Construction of 2 additional class rooms at GHS Rampur"
    sanction_cost = 1240000.00
    sanc_date = date(2023, 4, 15)
    comp_date = date(2023, 5, 8)
    proj_coords = (31.1423, 77.1724)

    print(f"\n[PHASE 1: e-SAKSHI CLAIM INGESTION]")
    print(f"  • Work ID:         {project_id}")
    print(f"  • Description:     \"{raw_desc}\"")
    print(f"  • Outlay:          ₹{sanction_cost:,.2f} (100% Disbursed in e-SAKSHI)")
    print(f"  • Claimed Status:  COMPLETED (Sanction: {sanc_date} -> Completion: {comp_date})")

    # 2. TAXONOMY NORMALIZATION
    asset_type, qty = normalize_asset_description(raw_desc)
    print(f"\n[PHASE 2: REGEX TAXONOMY NORMALIZATION]")
    print(f"  • Canonical Asset: {asset_type.value}")
    print(f"  • Target Quantity: {qty} units")

    # 3. 7-STAGE ENTITY RESOLUTION
    school_name = "Government High School Rampur"
    udise_code = "02120100402"
    school_coords = (31.1421, 77.1722)
    score, status = calculate_composite_match_score(raw_desc, school_name, proj_coords, school_coords)

    print(f"\n[PHASE 3: 7-STAGE ENTITY RESOLUTION]")
    print(f"  • Resolved School: {school_name} (UDISE: {udise_code})")
    print(f"  • Match Score:     {score * 100:.1f}% ({status})")
    assert score >= 0.85, "Entity resolution failed auto-accept threshold!"

    # 4. 4-LANE EVIDENCE EVALUATION
    pre_state = {"academic_year": "2022-23", "total_enrollment": 43, "total_classrooms": 7, "data_freeze_date": date(2022, 9, 30)}
    post_state = {"academic_year": "2024-25", "total_enrollment": 31, "total_classrooms": 7, "data_freeze_date": date(2024, 9, 30)}
    states = [pre_state, post_state]

    lane1 = evaluate_lane1_statutory("GOVERNMENT", date(2023, 4, 1), sanc_date, sanction_cost)
    lane2 = evaluate_lane2_need(states, qty)
    lane3 = evaluate_lane3_reflection(asset_type.value, qty, comp_date, pre_state, post_state)
    lane4 = evaluate_lane4_physics(asset_type.value, sanc_date, comp_date)

    lane_scores = {
        "STATUTORY": lane1,
        "INSTITUTIONAL_NEED": lane2,
        "ASSET_REFLECTION": lane3,
        "TIMELINE_PHYSICS": lane4
    }

    print(f"\n[PHASE 4: 4-LANE EVIDENCE EVALUATION]")
    print(f"  • Lane 1 (Statutory):    Score {lane1['score']:.2f} (Eligible Govt School)")
    print(f"  • Lane 2 (Need Context): Score {lane2['score']:.2f} (SCR: {lane2['metrics']['latest_scr']:.1f}, Enrollment Drop: {lane2['metrics']['3yr_enrollment_growth']*100:.1f}%)")
    print(f"  • Lane 3 (Asset Diff):   Score {lane3['score']:.2f} (Status: {lane3['status']}, Observed Delta: {lane3['observed_delta']})")
    print(f"  • Lane 4 (Velocity):     Score {lane4['score']:.2f} (Duration: {lane4['duration_days']} days vs 45d RCC minimum)")

    # 5. ORTHOGONAL MAX-POOLED FUSION & IPI
    fusion = compute_investigation_priority_index(lane_scores, [], mean_confidence=score)
    print(f"\n[PHASE 5: ORTHOGONAL FUSION & CASE TRIAGE]")
    print(f"  • IPI Score:             {fusion['ipi_score']}/100 [Confidence Band: {fusion['ipi_lower']} – {fusion['ipi_upper']}]")
    print(f"  • Action Tier:           TIER {fusion['risk_tier']} (MANDATORY FIELD INSPECTION)")
    print(f"  • Anomaly Category:      {fusion['primary_category']}")
    assert fusion['ipi_score'] >= 70.0, f"Expected Tier 3 score >= 70, got {fusion['ipi_score']}"

    # 6. D3 EVIDENCE GRAPH GENERATION
    proj_dict = {"project_id": project_id, "sanction_cost": sanction_cost, "canonical_asset_type": asset_type.value, "sanction_date": sanc_date, "completion_date": comp_date}
    school_dict = {"udise_code": udise_code, "name_canonical": school_name, "management_category": "GOVERNMENT", "operational_status": "OPERATIONAL"}
    graph = build_case_evidence_graph(proj_dict, school_dict, lane_scores, pre_state, post_state, confidence=score)

    print(f"\n[PHASE 6: IN-MEMORY PROVENANCE GRAPH (D3.JS)]")
    print(f"  • Nodes Generated:       {len(graph['nodes'])} ({[n['type'] for n in graph['nodes']]})")
    print(f"  • Links Generated:       {len(graph['links'])}")

    # 7. STATUTORY NOTICE GENERATION
    case_data = {
        "project_details": proj_dict,
        "school_details": school_dict,
        "ipi_score": fusion['ipi_score'],
        "risk_tier": fusion['risk_tier'],
        "primary_category": fusion['primary_category'],
        "explanation_narrative": "Bitemporal asset reflection shows 0 classroom delta in UDISE+ and concrete curing velocity violation.",
        "investigator_id": "DISTRICT_MAGISTRATE_DESK"
    }
    pdf_bytes = generate_statutory_notice_pdf(case_data)
    print(f"\n[PHASE 7: STATUTORY NOTICE (FORM MPLADS-INSP-1)]")
    print(f"  • Generated Notice PDF:  {len(pdf_bytes)} bytes (Ready for download / dispatch)")

    # 8. APPEND-ONLY CRYPTOGRAPHIC AUDIT LOG
    now = date.today()
    decision_payload = {"case_id": "DEMO-CASE-001", "decision": "ESCALATE_FIELD_INSPECTION", "notes": "Dispatched PWD Exec Engineer"}
    audit_hash = compute_record_hash(decision_payload, "DM_KANGRA", now, GENESIS_HASH)
    print(f"\n[PHASE 8: CRYPTOGRAPHIC AUDIT LOG (SHA-256)]")
    print(f"  • Decision Hash:         {audit_hash}")

    print("\n" + "=" * 80)
    print("  [SUCCESS] 4-MINUTE DEMO WORKFLOW VALIDATION PASSED 100%")
    print("=" * 80)

if __name__ == "__main__":
    run_demo()
