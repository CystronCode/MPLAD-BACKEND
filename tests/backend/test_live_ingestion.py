# tests/backend/test_live_ingestion.py
# Automated tests for real-time streaming e-SAKSHI claim ingestion and UDISE+ sync

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.scripts.load_udise_data import load_schools

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_ingestion_test_db():
    load_schools()

def test_stream_single_esakshi_claim():
    claim = {
        "work_id": "PRJ-LIVE-0001",
        "mp_id": "MP-LS-HP-02",
        "district_lgd_code": 12,
        "work_description": "Construction of 2 Additional Class rooms at GHS Rampur Block-1",
        "sanction_cost": 1240000.0,
        "recommendation_date": "2023-04-01",
        "sanction_date": "2023-04-15",
        "completion_date": "2023-05-08",
        "latitude": 32.1153,
        "longitude": 76.2206
    }
    resp = client.post("/api/v1/ingest/stream", json=claim)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["claims_processed"] == 1
    
    evaluated = data["evaluated_cases"][0]
    assert evaluated["project_id"] == "PRJ-LIVE-0001"
    assert "Government High School Rampur" in evaluated["school_name"]
    assert evaluated["ipi_score"] >= 70.0  # High IPI due to 23d construction velocity anomaly
    assert evaluated["risk_tier"] == 3

def test_stream_batch_esakshi_claims():
    claims = [
        {
            "work_id": "PRJ-LIVE-0002",
            "mp_id": "MP-LS-HP-02",
            "district_lgd_code": 12,
            "work_description": "Setup of Smart Computer Lab at St Xavier Academy Kangra",
            "sanction_cost": 850000.0,
            "recommendation_date": "2023-02-10",
            "sanction_date": "2023-05-18",
            "completion_date": "2023-11-20",
            "latitude": 32.0991,
            "longitude": 76.2691
        },
        {
            "work_id": "PRJ-LIVE-0003",
            "mp_id": "MP-LS-HP-02",
            "district_lgd_code": 12,
            "work_description": "Construction of 2 Additional Classrooms at GSSS Palampur",
            "sanction_cost": 1400000.0,
            "recommendation_date": "2023-01-15",
            "sanction_date": "2023-02-20",
            "completion_date": "2023-08-30",
            "latitude": 32.1109,
            "longitude": 76.5363
        }
    ]
    resp = client.post("/api/v1/ingest/stream", json=claims)
    assert resp.status_code == 201
    data = resp.json()
    assert data["claims_processed"] == 2

    # Query cases endpoint to verify new live cases are instantly available in queue
    cases_resp = client.get("/api/v1/cases")
    assert cases_resp.status_code == 200
    case_ids = [c["project_id"] for c in cases_resp.json()]
    assert "PRJ-LIVE-0002" in case_ids
    assert "PRJ-LIVE-0003" in case_ids

def test_live_portal_telemetry_status():
    resp = client.get("/api/v1/ingest/live-portal-status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ONLINE"
    assert len(data["live_telemetry"]) >= 3
    for portal in data["live_telemetry"]:
        assert "latency_ms" in portal
        assert "http_status" in portal

def test_trigger_live_sync():
    resp = client.post("/api/v1/ingest/live-sync")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert "portal_telemetry" in data
