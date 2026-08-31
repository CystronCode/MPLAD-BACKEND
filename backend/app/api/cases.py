# backend/app/api/cases.py
# REST API endpoints for Investigation Cases and Decisioning

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.models import InvestigationCase, MPLADSProject, School, SchoolAnnualState, AuditLog
from contracts.models import (
    InvestigationCaseSummary,
    InvestigationCaseDetail,
    CaseDecisionRequest,
    CaseDecisionResponse,
    CaseStatus,
    D3GraphPayload,
    MPLADSProjectSchema,
    SchoolMasterSchema,
    SchoolAnnualStateSchema,
    CanonicalAssetType
)
from backend.app.notices.generator import generate_mplads_insp1_notice
from backend.app.audit.hash_chain import compute_record_hash, GENESIS_HASH

router = APIRouter()

def get_canonical_asset_enum(asset_val) -> CanonicalAssetType:
    if not asset_val:
        return CanonicalAssetType.GENERIC_CIVIL_REPAIR
    if isinstance(asset_val, CanonicalAssetType):
        return asset_val
    val_str = str(asset_val).upper()
    if val_str in ("CLASSROOM", "ADDITIONAL_CLASSROOM"):
        return CanonicalAssetType.ADDITIONAL_CLASSROOM
    if val_str in ("SANITATION", "TOILET_BLOCK", "TOILETS"):
        return CanonicalAssetType.TOILET_BLOCK
    try:
        return CanonicalAssetType(val_str)
    except ValueError:
        return CanonicalAssetType.GENERIC_CIVIL_REPAIR

@router.get("", response_model=List[InvestigationCaseSummary])
def get_cases(
    tier: Optional[int] = Query(None, description="Filter by Risk Tier (1, 2, 3)"),
    min_ipi: Optional[float] = Query(None, description="Filter by minimum IPI score"),
    status: Optional[str] = Query(None, description="Filter by case status"),
    constituency_code: Optional[str] = Query(None, description="Filter by Constituency Code e.g. KA-24"),
    db: Session = Depends(get_db)
):
    query = db.query(InvestigationCase).join(MPLADSProject).join(School)

    if constituency_code and constituency_code != "ALL":
        query = query.filter(MPLADSProject.project_id.like(f"PRJ-{constituency_code}-%"))
    if tier:
        query = query.filter(InvestigationCase.risk_tier == tier)
    if min_ipi:
        query = query.filter(InvestigationCase.ipi_score >= min_ipi)
    if status:
        query = query.filter(InvestigationCase.status == status)

    cases = query.order_by(InvestigationCase.ipi_score.desc()).all()

    results = []
    for c in cases:
        p = c.project
        s = p.resolved_school if p else None
        asset_enum = get_canonical_asset_enum(p.canonical_asset_type if p else None)
        results.append(
            InvestigationCaseSummary(
                case_id=str(c.case_id),
                project_id=c.project_id,
                school_name=s.name_canonical if s else "Unresolved School",
                udise_code=s.udise_code if s else "00000000000",
                sanction_cost=float(p.sanction_cost) if p else 0.0,
                canonical_asset_type=asset_enum,
                ipi_score=c.ipi_score,
                ipi_lower=c.ipi_lower,
                ipi_upper=c.ipi_upper,
                risk_tier=c.risk_tier,
                primary_category=c.primary_category,
                status=c.status,
                created_at=c.created_at
            )
        )
    return results

def find_case_by_id(db: Session, case_id: str) -> Optional[InvestigationCase]:
    cases = db.query(InvestigationCase).all()
    return next((c for c in cases if str(c.case_id) == str(case_id)), None)

@router.get("/{case_id}", response_model=InvestigationCaseDetail)
def get_case_detail(case_id: str, db: Session = Depends(get_db)):
    c = find_case_by_id(db, case_id)
    if not c:
        raise HTTPException(status_code=404, detail="Investigation case not found")

    p = c.project
    s = p.resolved_school if p else None

    if not p or not s:
        raise HTTPException(status_code=400, detail="Incomplete case relationships")

    states = db.query(SchoolAnnualState).filter(
        SchoolAnnualState.udise_code == s.udise_code
    ).order_by(SchoolAnnualState.data_freeze_date.asc()).all()

    pre_state = states[0] if states else None
    post_state = states[-1] if len(states) >= 2 else None

    asset_enum = get_canonical_asset_enum(p.canonical_asset_type)

    project_schema = MPLADSProjectSchema(
        project_id=p.project_id,
        mp_id=p.mp_id,
        district_lgd_code=p.district_lgd_code,
        work_description_raw=p.work_description_raw,
        canonical_asset_type=asset_enum,
        target_quantity=p.target_quantity,
        sanction_cost=float(p.sanction_cost),
        recommendation_date=p.recommendation_date or datetime.utcnow().date(),
        sanction_date=p.sanction_date or datetime.utcnow().date(),
        completion_date=p.completion_date,
        latitude=p.latitude,
        longitude=p.longitude,
        resolved_udise_code=p.resolved_udise_code,
        resolution_confidence=p.resolution_confidence,
        resolution_status=p.resolution_status
    )

    school_schema = SchoolMasterSchema(
        udise_code=s.udise_code,
        name_canonical=s.name_canonical,
        state_lgd_code=s.state_lgd_code,
        district_lgd_code=s.district_lgd_code,
        block_lgd_code=s.block_lgd_code,
        village_name=s.village_name,
        management_category=s.management_category,
        operational_status=s.operational_status,
        latitude=s.latitude,
        longitude=s.longitude
    )

    return InvestigationCaseDetail(
        case_id=str(c.case_id),
        project_id=c.project_id,
        school_name=s.name_canonical,
        udise_code=s.udise_code,
        sanction_cost=float(p.sanction_cost),
        canonical_asset_type=asset_enum,
        ipi_score=c.ipi_score,
        ipi_lower=c.ipi_lower,
        ipi_upper=c.ipi_upper,
        risk_tier=c.risk_tier,
        primary_category=c.primary_category,
        status=c.status,
        created_at=c.created_at,
        evidence_graph=c.evidence_graph,
        explanation_narrative=c.explanation_narrative,
        lane_scores={},
        project_details=project_schema,
        school_details=school_schema
    )

@router.get("/{case_id}/evidence-graph", response_model=D3GraphPayload)
def get_case_evidence_graph(case_id: str, db: Session = Depends(get_db)):
    c = find_case_by_id(db, case_id)
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
    return c.evidence_graph

@router.get("/{case_id}/notice/pdf")
def download_notice_pdf(case_id: str, db: Session = Depends(get_db)):
    c = find_case_by_id(db, case_id)
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
    p = c.project
    s = p.resolved_school if p else None

    case_data = {
        "project_details": {
            "project_id": p.project_id if p else "N/A",
            "work_description_raw": p.work_description_raw if p else "N/A",
            "sanction_cost": float(p.sanction_cost) if p else 0.0,
            "sanction_date": str(p.sanction_date) if p and p.sanction_date else "",
            "completion_date": str(p.completion_date) if p and p.completion_date else ""
        },
        "school_details": {
            "name_canonical": s.name_canonical if s else "N/A",
            "udise_code": s.udise_code if s else "N/A",
            "latitude": s.latitude if s else 0.0,
            "longitude": s.longitude if s else 0.0
        },
        "ipi_score": c.ipi_score,
        "risk_tier": c.risk_tier,
        "primary_category": c.primary_category,
        "explanation_narrative": c.explanation_narrative,
        "investigator_id": "DISTRICT_COLLECTOR_DESK"
    }

    pdf_bytes = generate_mplads_insp1_notice(case_data)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=MPLADS_INSP1_{c.project_id}.pdf"}
    )

@router.post("/{case_id}/decision", response_model=CaseDecisionResponse)
def record_case_decision(
    case_id: str,
    req: CaseDecisionRequest,
    db: Session = Depends(get_db)
):
    c = find_case_by_id(db, case_id)
    if not c:
        raise HTTPException(status_code=404, detail="Investigation case not found")

    new_status = CaseStatus.PENDING_REVIEW
    if req.decision.value == "ESCALATE_FIELD_INSPECTION":
        new_status = CaseStatus.ESCALATED
    elif req.decision.value == "DISMISS_BENIGN_CONTEXT":
        new_status = CaseStatus.DISMISSED
    elif req.decision.value == "RESOLVE_AS_VERIFIED":
        new_status = CaseStatus.VERIFIED

    c.status = new_status.value

    # Fetch last audit record for SHA-256 hash chaining
    last_log = db.query(AuditLog).order_by(AuditLog.log_id.desc()).first()
    prev_hash = last_log.current_hash if last_log else GENESIS_HASH

    now = datetime.utcnow()
    payload = {
        "case_id": str(c.case_id),
        "project_id": c.project_id,
        "decision": req.decision.value,
        "notes": req.notes
    }

    current_hash = compute_record_hash(
        payload=payload,
        actor_id=req.investigator_id,
        recorded_at=now,
        previous_hash=prev_hash
    )

    audit_entry = AuditLog(
        entity_type="INVESTIGATOR_DECISION",
        entity_id=str(c.case_id),
        action_performed=req.decision.value,
        actor_id=req.investigator_id,
        payload=payload,
        previous_hash=prev_hash,
        current_hash=current_hash,
        recorded_at=now
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)

    return CaseDecisionResponse(
        case_id=str(c.case_id),
        status=new_status,
        audit_hash=current_hash,
        recorded_at=now
    )
