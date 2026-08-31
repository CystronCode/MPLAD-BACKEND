# backend/app/api/analytics.py
# Executive district & state-wide Karnataka constituency analytics endpoints

import os
import json
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.db.session import get_db
from backend.app.db.models import InvestigationCase, MPLADSProject, School

router = APIRouter()

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
MASTER_FILE = os.path.join(DATA_DIR, "karnataka_constituencies_master.json")

def load_constituency_master():
    if os.path.exists(MASTER_FILE):
        with open(MASTER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@router.get("/constituencies")
def get_all_constituencies(db: Session = Depends(get_db)):
    """Returns list of all 28 Karnataka Parliamentary Constituencies with live KPI summaries."""
    master = load_constituency_master()
    results = []
    
    for c in master:
        dist_code = c["district_lgd_code"]
        c_code = c["code"]
        
        q_proj = db.query(MPLADSProject).filter(
            (MPLADSProject.district_lgd_code == dist_code) | (MPLADSProject.project_id.like(f"PRJ-{c_code}-%"))
        )
        total_projects = q_proj.count()
        total_spend = q_proj.with_entities(func.sum(MPLADSProject.sanction_cost)).scalar() or 0.0
        
        q_cases = db.query(InvestigationCase).join(MPLADSProject).filter(
            (MPLADSProject.district_lgd_code == dist_code) | (MPLADSProject.project_id.like(f"PRJ-{c_code}-%"))
        )
        t3_count = q_cases.filter(InvestigationCase.risk_tier == 3).count()
        t2_count = q_cases.filter(InvestigationCase.risk_tier == 2).count()
        avg_ipi = q_cases.with_entities(func.avg(InvestigationCase.ipi_score)).scalar() or 0.0

        results.append({
            "code": c["code"],
            "name": c["name"],
            "mp_id": c["mp_id"],
            "district_lgd_code": dist_code,
            "headquarters": c["headquarters"],
            "total_projects": total_projects,
            "total_expenditure": float(total_spend),
            "tier_3_warrants": t3_count,
            "tier_2_reviews": t2_count,
            "average_ipi": round(float(avg_ipi), 1)
        })
        
    return results

@router.get("/district")
def get_district_analytics(
    constituency_code: Optional[str] = Query(None, description="e.g. KA-24 or ALL"),
    db: Session = Depends(get_db)
):
    master = load_constituency_master()
    code_map = {c["code"]: c for c in master}
    
    if constituency_code and constituency_code != "ALL" and constituency_code in code_map:
        c_info = code_map[constituency_code]
        dist_code = c_info["district_lgd_code"]
        district_name = f"{c_info['name']} Parliamentary Constituency ({constituency_code}, Karnataka)"
        
        proj_filter = (MPLADSProject.district_lgd_code == dist_code) | (MPLADSProject.project_id.like(f"PRJ-{constituency_code}-%"))
        case_filter = (MPLADSProject.district_lgd_code == dist_code) | (MPLADSProject.project_id.like(f"PRJ-{constituency_code}-%"))
        
        q_proj = db.query(MPLADSProject).filter(proj_filter)
        q_cases = db.query(InvestigationCase).join(MPLADSProject).filter(case_filter)
    else:
        district_name = "Karnataka State (All 28 Parliamentary Constituencies)"
        q_proj = db.query(MPLADSProject)
        q_cases = db.query(InvestigationCase)

    total_projects = q_proj.count()
    total_spend = q_proj.with_entities(func.sum(MPLADSProject.sanction_cost)).scalar() or 0.0

    t1_count = q_cases.filter(InvestigationCase.risk_tier == 1).count()
    t2_count = q_cases.filter(InvestigationCase.risk_tier == 2).count()
    t3_count = q_cases.filter(InvestigationCase.risk_tier == 3).count()
    avg_ipi = q_cases.with_entities(func.avg(InvestigationCase.ipi_score)).scalar() or 0.0

    return {
        "district_name": district_name,
        "total_projects": total_projects,
        "total_expenditure": float(total_spend),
        "tier_distribution": {
            "tier_1": t1_count,
            "tier_2": t2_count,
            "tier_3": t3_count
        },
        "average_ipi": round(float(avg_ipi), 1),
        "anomaly_breakdown": {
            "CRITICAL_REFLECTION_GAP": q_cases.filter(InvestigationCase.primary_category.like("%REFLECTION%")).count(),
            "PHYSICAL_VELOCITY_VIOLATION": q_cases.filter(InvestigationCase.primary_category.like("%VELOCITY%")).count(),
            "STATUTORY_INELIGIBLE_BENEFICIARY": q_cases.filter(InvestigationCase.primary_category.like("%STATUTORY%")).count(),
            "INSTITUTIONAL_SITING_INEFFICIENCY": q_cases.filter(InvestigationCase.primary_category.like("%SITING%")).count()
        }
    }
