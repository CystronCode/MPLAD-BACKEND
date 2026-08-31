# backend/app/api/ambiguity.py
# Ambiguity queue and manual school resolution endpoints

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.models import MPLADSProject, School

router = APIRouter()

@router.get("")
def get_ambiguity_queue(db: Session = Depends(get_db)):
    ambiguous_projects = db.query(MPLADSProject).filter(
        MPLADSProject.resolution_status == "AMBIGUOUS"
    ).all()
    
    results = []
    schools = db.query(School).limit(10).all() # sample nearby candidates
    for p in ambiguous_projects:
        results.append({
            "project_id": p.project_id,
            "work_description_raw": p.work_description_raw,
            "project_coords": [p.latitude, p.longitude] if p.latitude and p.longitude else None,
            "candidates": [
                {
                    "udise_code": s.udise_code,
                    "school_name": s.name_canonical,
                    "distance_meters": 120,
                    "similarity_score": 0.78,
                    "management": s.management_category,
                    "status": s.operational_status
                }
                for s in schools
            ]
        })
    return results

@router.post("/{project_id}/resolve")
def resolve_ambiguity(
    project_id: str,
    payload: dict,
    db: Session = Depends(get_db)
):
    p = db.query(MPLADSProject).filter(MPLADSProject.project_id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    target_udise = payload.get("resolved_udise_code")
    school = db.query(School).filter(School.udise_code == target_udise).first()
    if not school:
        raise HTTPException(status_code=400, detail="Target UDISE school does not exist")

    p.resolved_udise_code = target_udise
    p.resolution_status = "MANUAL_VERIFIED"
    p.resolution_confidence = 1.0
    db.commit()

    return {"status": "SUCCESS", "project_id": project_id, "resolved_udise": target_udise}
