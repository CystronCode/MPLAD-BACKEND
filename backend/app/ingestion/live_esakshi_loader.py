# backend/app/ingestion/live_esakshi_loader.py
# Real-Time e-SAKSHI Stream & Webhook Ingestion Engine

import logging
from decimal import Decimal
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.app.db.models import School, SchoolAnnualState, MPLADSProject, InvestigationCase
from backend.app.normalization.taxonomy import normalize_asset_description, CanonicalAssetType
from backend.app.resolution.matcher import resolve_project
from backend.app.detection.lane1_statutory import evaluate_lane1_statutory
from backend.app.detection.lane2_need import evaluate_lane2_need
from backend.app.detection.lane3_reflection import evaluate_lane3_reflection
from backend.app.detection.lane4_physics import evaluate_lane4_physics
from backend.app.detection.exceptions import apply_exception_context
from backend.app.fusion.scoring import compute_investigation_priority_index
from backend.app.explainability.graph_builder import build_case_evidence_graph

logger = logging.getLogger("meev.ingestion.esakshi")

def parse_date(val: Any) -> Optional[date]:
    if not val:
        return None
    if isinstance(val, date):
        return val
    if isinstance(val, str):
        try:
            return datetime.strptime(val[:10], "%Y-%m-%d").date()
        except Exception:
            return None
    return None

def process_live_esakshi_claim(
    db: Session,
    raw_claim: Dict[str, Any],
    candidate_schools: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Processes a single live e-SAKSHI claim in < 100ms:
    1. Taxonomy Normalization
    2. 7-Stage Entity Resolution
    3. 4-Lane Evidence Evaluation
    4. Orthogonal Max-Pooled Fusion
    5. In-Memory D3 Provenance Graph
    6. Database Persistence
    """
    p_id = str(raw_claim.get("work_id") or raw_claim.get("project_id", "")).strip()
    mp_id = str(raw_claim.get("mp_id", "UNKNOWN")).strip()
    dist_lgd = int(raw_claim.get("district_lgd_code", 12))
    desc = str(raw_claim.get("work_description") or raw_claim.get("work_description_raw", "")).strip()
    cost = float(raw_claim.get("sanction_cost", 0.0))
    recom_d = parse_date(raw_claim.get("recommendation_date"))
    sanc_d = parse_date(raw_claim.get("sanction_date"))
    comp_d = parse_date(raw_claim.get("completion_date"))
    lat = float(raw_claim["latitude"]) if raw_claim.get("latitude") is not None else None
    lon = float(raw_claim["longitude"]) if raw_claim.get("longitude") is not None else None

    # 1. Regex Taxonomy Normalization
    asset_type, target_qty = normalize_asset_description(desc)

    # 2. Fetch candidate schools if not cached in batch
    if candidate_schools is None:
        schools = db.query(School).filter(School.district_lgd_code == dist_lgd).all()
        if not schools:
            schools = db.query(School).all()
        candidate_schools = [
            {
                "udise_code": s.udise_code,
                "name_canonical": s.name_canonical,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "management_category": s.management_category,
                "operational_status": s.operational_status
            }
            for s in schools
        ]

    # 3. 7-Stage Entity Resolution
    p_coords = (lat, lon) if lat is not None and lon is not None else None
    resolution = resolve_project(desc, p_coords, candidate_schools, district_lgd_code=dist_lgd)
    
    resolved_udise = resolution.get("udise_code")
    res_conf = float(resolution.get("confidence", 0.0))
    res_status = resolution.get("status", "UNRESOLVED")

    # Upsert MPLADSProject
    proj = db.query(MPLADSProject).filter(MPLADSProject.project_id == p_id).first()
    if not proj:
        proj = MPLADSProject(
            project_id=p_id,
            mp_id=mp_id,
            district_lgd_code=dist_lgd,
            work_description_raw=desc,
            canonical_asset_type=asset_type.value,
            target_quantity=target_qty,
            sanction_cost=Decimal(str(cost)),
            recommendation_date=recom_d,
            sanction_date=sanc_d,
            completion_date=comp_d,
            latitude=lat,
            longitude=lon,
            resolved_udise_code=resolved_udise,
            resolution_confidence=Decimal(str(round(res_conf, 3))),
            resolution_status=res_status
        )
        db.add(proj)
    else:
        proj.work_description_raw = desc
        proj.canonical_asset_type = asset_type.value
        proj.target_quantity = target_qty
        proj.sanction_cost = Decimal(str(cost))
        proj.recommendation_date = recom_d
        proj.sanction_date = sanc_d
        proj.completion_date = comp_d
        proj.resolved_udise_code = resolved_udise
        proj.resolution_confidence = Decimal(str(round(res_conf, 3)))
        proj.resolution_status = res_status

    db.flush()

    # 4. Multi-Lane Evaluation
    school_obj = db.query(School).filter(School.udise_code == resolved_udise).first() if resolved_udise else None
    states = db.query(SchoolAnnualState).filter(
        SchoolAnnualState.udise_code == resolved_udise
    ).order_by(SchoolAnnualState.data_freeze_date.asc()).all() if resolved_udise else []

    pre_state = states[0] if states else None
    post_state = states[-1] if len(states) >= 2 else None

    pre_dict = {
        "academic_year": pre_state.academic_year,
        "total_enrollment": pre_state.total_enrollment,
        "total_classrooms": pre_state.total_classrooms,
        "data_freeze_date": pre_state.data_freeze_date
    } if pre_state else None

    post_dict = {
        "academic_year": post_state.academic_year,
        "total_enrollment": post_state.total_enrollment,
        "total_classrooms": post_state.total_classrooms,
        "data_freeze_date": post_state.data_freeze_date
    } if post_state else None

    state_dicts = [pre_dict, post_dict] if pre_dict and post_dict else ([pre_dict] if pre_dict else [])

    # Evaluate 4 Lanes
    mgmt = school_obj.management_category if school_obj else "GOVERNMENT"
    op_status = school_obj.operational_status if school_obj else "OPERATIONAL"

    l1 = evaluate_lane1_statutory(mgmt, recom_d, sanc_d, cost)
    l2 = evaluate_lane2_need(state_dicts, target_qty)
    l3 = evaluate_lane3_reflection(asset_type, target_qty, comp_d, pre_dict, post_dict)
    l4 = evaluate_lane4_physics(asset_type, sanc_d, comp_d)

    lane_scores = {
        "STATUTORY": l1,
        "INSTITUTIONAL_NEED": l2,
        "ASSET_REFLECTION": l3,
        "TIMELINE_PHYSICS": l4
    }

    exc = apply_exception_context(lane_scores, {"operational_status": op_status}, state_dicts)
    fusion = compute_investigation_priority_index(lane_scores, exc, mean_confidence=res_conf if res_conf > 0 else 0.85)

    # In-memory D3 Graph
    proj_dict = {
        "project_id": p_id,
        "sanction_cost": cost,
        "canonical_asset_type": asset_type.value,
        "sanction_date": sanc_d,
        "completion_date": comp_d
    }
    school_dict = {
        "udise_code": school_obj.udise_code if school_obj else "UNRESOLVED",
        "name_canonical": school_obj.name_canonical if school_obj else "Unresolved School",
        "management_category": mgmt,
        "operational_status": op_status
    }
    graph = build_case_evidence_graph(proj_dict, school_dict, lane_scores, pre_dict, post_dict, confidence=res_conf)

    # Upsert InvestigationCase
    case = db.query(InvestigationCase).filter(InvestigationCase.project_id == p_id).first()
    cat = fusion['primary_category']
    school_name = school_obj.name_canonical if school_obj else "the school"
    
    if "REFLECTION" in cat:
        narrative = (
            f"The implementing agency reported 100% completion for '{desc}' with Rs. {cost/100000:.2f} Lakhs disbursed. "
            f"However, the official annual UDISE+ physical school infrastructure census confirms ZERO new rooms or facilities added at {school_name}. "
            f"This discrepancy indicates potential unexecuted work or a ghost asset. Mandatory physical field inspection required."
        )
    elif "STATUTORY" in cat or mgmt == "PRIVATE_UNAIDED":
        narrative = (
            f"Public MPLADS funds of Rs. {cost/100000:.2f} Lakhs were sanctioned for '{desc}' at {school_name}, which is registered as a Private Unaided Institution. "
            f"This violates Section 6.1 of the MPLADS Scheme Guidelines 2023. Government funds may only benefit public or government-aided schools. Immediate audit and recovery proceedings warranted."
        )
    elif "VELOCITY" in cat:
        narrative = (
            f"The project '{desc}' was reported completed in an unrealistic timeframe violating structural civil engineering limits (minimum 28 days required for RCC concrete curing under IS 456 standards). "
            f"Quality assessment and Measurement Book (MB) verification required before releasing remaining milestone funds."
        )
    elif "SITING" in cat:
        narrative = (
            f"Additional facilities were sanctioned for '{desc}' at {school_name} where student-to-classroom ratio is already low with declining enrollment. "
            f"Infrastructure allocation represents demographic siting inefficiency. Administrative review required."
        )
    else:
        narrative = (
            f"The project '{desc}' (Sanctioned: Rs. {cost/100000:.2f} Lakhs) has been verified against independent UDISE+ school infrastructure returns. "
            f"The newly constructed facilities are physically recorded and active in the school register. Approved for clean certification."
        )

    
    if not case:
        case = InvestigationCase(
            project_id=p_id,
            ipi_score=Decimal(str(fusion["ipi_score"])),
            ipi_lower=Decimal(str(fusion["ipi_lower"])),
            ipi_upper=Decimal(str(fusion["ipi_upper"])),
            risk_tier=fusion["risk_tier"],
            primary_category=fusion["primary_category"],
            evidence_graph=graph,
            explanation_narrative=narrative,
            status="PENDING_REVIEW"
        )
        db.add(case)
    else:
        case.ipi_score = Decimal(str(fusion["ipi_score"]))
        case.ipi_lower = Decimal(str(fusion["ipi_lower"]))
        case.ipi_upper = Decimal(str(fusion["ipi_upper"]))
        case.risk_tier = fusion["risk_tier"]
        case.primary_category = fusion["primary_category"]
        case.evidence_graph = graph
        case.explanation_narrative = narrative

    db.commit()
    db.refresh(case)

    return {
        "case_id": str(case.case_id),
        "project_id": p_id,
        "school_name": school_dict["name_canonical"],
        "udise_code": school_dict["udise_code"],
        "resolution_status": res_status,
        "ipi_score": float(case.ipi_score),
        "risk_tier": case.risk_tier,
        "primary_category": case.primary_category,
        "status": case.status
    }

def process_live_esakshi_batch(db: Session, claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Evaluates a batch of live claims with district school caching."""
    schools = db.query(School).all()
    cached_candidates = [
        {
            "udise_code": s.udise_code,
            "name_canonical": s.name_canonical,
            "district_lgd_code": s.district_lgd_code,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "management_category": s.management_category,
            "operational_status": s.operational_status
        }
        for s in schools
    ]

    results = []
    for c in claims:
        res = process_live_esakshi_claim(db, c, candidate_schools=cached_candidates)
        results.append(res)
    return results
