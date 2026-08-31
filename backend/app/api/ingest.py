# backend/app/api/ingest.py
# Real-Time Ingestion & Streaming Webhook API Router

from typing import List, Dict, Any, Union, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.ingestion.live_esakshi_loader import process_live_esakshi_claim, process_live_esakshi_batch
from backend.app.ingestion.live_udise_loader import ingest_udise_records

router = APIRouter()

class LiveClaimPayload(BaseModel):
    work_id: str = Field(..., description="Unique e-SAKSHI work identifier, e.g. PRJ-2023-04567")
    mp_id: str = Field(default="MP-LS-HP-02", description="MP identifier")
    district_lgd_code: int = Field(default=12, description="LGD District code")
    work_description: str = Field(..., description="Raw text description of the work claim")
    sanction_cost: float = Field(..., description="Total sanctioned outlay in INR")
    recommendation_date: Optional[str] = Field(None, description="ISO date string YYYY-MM-DD")
    sanction_date: Optional[str] = Field(None, description="ISO date string YYYY-MM-DD")
    completion_date: Optional[str] = Field(None, description="ISO date string YYYY-MM-DD")
    latitude: Optional[float] = Field(None, description="Project reported latitude")
    longitude: Optional[float] = Field(None, description="Project reported longitude")

class IngestionStreamResponse(BaseModel):
    status: str
    claims_processed: int
    evaluated_cases: List[Dict[str, Any]]

@router.post("/stream", response_model=IngestionStreamResponse, status_code=status.HTTP_201_CREATED)
def stream_esakshi_claims(
    claims: Union[LiveClaimPayload, List[LiveClaimPayload]],
    db: Session = Depends(get_db)
):
    """
    Real-Time e-SAKSHI Stream Ingestion Webhook.
    Accepts single claim or batch of claims and executes sub-100ms:
    1. Regex Taxonomy Normalization
    2. 7-Stage Entity Resolution against ground-truth schools
    3. 4-Lane Anomaly & Physics Evaluation
    4. Orthogonal Max-Pooled Fusion Scoring (IPI)
    5. In-Memory D3 Provenance Graph generation
    6. Case persistence for immediate triage
    """
    if isinstance(claims, LiveClaimPayload):
        claim_list = [claims.model_dump() if hasattr(claims, "model_dump") else claims.dict()]
    else:
        claim_list = [c.model_dump() if hasattr(c, "model_dump") else c.dict() for c in claims]
    
    if not claim_list:
        raise HTTPException(status_code=400, detail="Empty claims list")

    evaluated = process_live_esakshi_batch(db, claim_list)

    return IngestionStreamResponse(
        status="SUCCESS",
        claims_processed=len(evaluated),
        evaluated_cases=evaluated
    )

@router.post("/udise-sync", status_code=status.HTTP_200_OK)
def sync_udise_ground_truth(
    records: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """
    Synchronizes authentic UDISE+ school masters and annual states with cryptographic SHA-256 provenance.
    """
    if not records:
        raise HTTPException(status_code=400, detail="Empty records list")

    res = ingest_udise_records(db, records)
    return {
        "status": "SUCCESS",
        "schools_ingested": res["schools_ingested"],
        "states_ingested": res["states_ingested"]
    }

@router.post("/seed-realtime", status_code=status.HTTP_200_OK)
def trigger_realtime_data_seed(clear_first: bool = True):
    """
    Triggers immediate ingestion of authentic UDISE+ schools and real e-SAKSHI claims across all 28 Karnataka constituencies.
    """
    from backend.scripts.load_realtime_data import load_realtime_data
    load_realtime_data(clear_first=clear_first)
    return {"status": "SUCCESS", "message": "Authentic Karnataka State 28-Constituency data successfully loaded."}

@router.get("/live-portal-status", status_code=status.HTTP_200_OK)
def get_live_government_portal_status():
    """
    Executes live real-time network HTTP telemetry probes to official government portals
    (UDISE+ MoE, Local Government Directory MoPR, and Data.gov.in OGD).
    """
    from backend.app.ingestion.live_fetcher import get_all_portal_telemetry
    telemetry = get_all_portal_telemetry()
    return {
        "status": "ONLINE",
        "live_telemetry": telemetry,
        "probed_at": datetime.utcnow().isoformat() + "Z"
    }

@router.post("/live-sync", status_code=status.HTTP_200_OK)
def trigger_live_government_sync(db: Session = Depends(get_db)):
    """
    Performs real-time live synchronization with official government portal registries.
    """
    from backend.app.ingestion.live_fetcher import get_all_portal_telemetry
    from backend.scripts.load_realtime_data import load_realtime_data
    
    telemetry = get_all_portal_telemetry()
    load_realtime_data(clear_first=False)
    
    return {
        "status": "SUCCESS",
        "message": "Live government registry synchronization complete.",
        "portal_telemetry": telemetry,
        "synced_at": datetime.utcnow().isoformat() + "Z"
    }

@router.post("/csv-pipeline", status_code=status.HTTP_200_OK)
def trigger_csv_ingestion_pipeline():
    """
    Executes automated ingestion of raw external CSV datasets (karnataka_schools_raw.csv & karnataka_works_raw.csv).
    """
    from backend.scripts.ingest_external_csv import execute_csv_ingestion
    res = execute_csv_ingestion()
    return {
        "status": "SUCCESS",
        "message": "External CSV dataset successfully ingested and evaluated through 4-lane engine.",
        "details": res
    }





