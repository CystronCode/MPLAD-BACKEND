# backend/app/api/analytics.py
# Executive district overview analytics endpoints

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.db.session import get_db
from backend.app.db.models import InvestigationCase, MPLADSProject

router = APIRouter()

@router.get("/district")
def get_district_analytics(db: Session = Depends(get_db)):
    total_projects = db.query(MPLADSProject).count()
    total_spend = db.query(func.sum(MPLADSProject.sanction_cost)).scalar() or 0.0

    t1_count = db.query(InvestigationCase).filter(InvestigationCase.risk_tier == 1).count()
    t2_count = db.query(InvestigationCase).filter(InvestigationCase.risk_tier == 2).count()
    t3_count = db.query(InvestigationCase).filter(InvestigationCase.risk_tier == 3).count()

    avg_ipi = db.query(func.avg(InvestigationCase.ipi_score)).scalar() or 0.0

    return {
        "district_name": "Bengaluru North Parliamentary Constituency (Karnataka)",
        "total_projects": total_projects,
        "total_expenditure": float(total_spend),
        "tier_distribution": {
            "tier_1": t1_count,
            "tier_2": t2_count,
            "tier_3": t3_count
        },
        "average_ipi": round(float(avg_ipi), 1),
        "anomaly_breakdown": {
            "CRITICAL_REFLECTION_GAP": db.query(InvestigationCase).filter(InvestigationCase.primary_category.like("%REFLECTION%")).count(),
            "PHYSICAL_VELOCITY_VIOLATION": db.query(InvestigationCase).filter(InvestigationCase.primary_category.like("%VELOCITY%")).count(),
            "STATUTORY_INELIGIBLE_BENEFICIARY": db.query(InvestigationCase).filter(InvestigationCase.primary_category.like("%STATUTORY%")).count(),
            "INSTITUTIONAL_SITING_INEFFICIENCY": db.query(InvestigationCase).filter(InvestigationCase.primary_category.like("%SITING%")).count()
        }
    }
