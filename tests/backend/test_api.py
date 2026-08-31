# tests/backend/test_api.py
# Backend API integration tests using FastAPI TestClient

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.scripts.load_udise_data import load_schools
from backend.scripts.generate_synthetic_esakshi import generate_projects

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Hydrate database with schools and projects
    load_schools()
    generate_projects()

def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "HEALTHY"

def test_get_cases_endpoint():
    resp = client.get("/api/v1/cases")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Demo case PRJ-2023-04567 should be in the queue
    demo_case = next((c for c in data if c["project_id"] == "PRJ-2023-04567"), None)
    assert demo_case is not None
    assert demo_case["ipi_score"] >= 70.0 # Tier 3

def test_get_case_detail_and_graph():
    resp_cases = client.get("/api/v1/cases")
    case_id = resp_cases.json()[0]["case_id"]

    resp_detail = client.get(f"/api/v1/cases/{case_id}")
    assert resp_detail.status_code == 200
    detail = resp_detail.json()
    assert "evidence_graph" in detail
    assert "explanation_narrative" in detail

    resp_graph = client.get(f"/api/v1/cases/{case_id}/evidence-graph")
    assert resp_graph.status_code == 200
    graph = resp_graph.json()
    assert "nodes" in graph
    assert "links" in graph
    assert len(graph["nodes"]) > 0

def test_download_notice_pdf():
    resp_cases = client.get("/api/v1/cases")
    case_id = resp_cases.json()[0]["case_id"]

    resp_pdf = client.get(f"/api/v1/cases/{case_id}/notice/pdf")
    assert resp_pdf.status_code == 200
    assert resp_pdf.headers["content-type"] == "application/pdf"
    assert len(resp_pdf.content) > 100

def test_record_case_decision_and_audit():
    resp_cases = client.get("/api/v1/cases")
    case_id = resp_cases.json()[0]["case_id"]

    decision_payload = {
        "decision": "ESCALATE_FIELD_INSPECTION",
        "notes": "Verified post-completion census discrepancy. Dispatched inspecting engineer.",
        "investigator_id": "OFFICER_IDA_001"
    }
    resp = client.post(f"/api/v1/cases/{case_id}/decision", json=decision_payload)
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["status"] == "ESCALATED"
    assert "audit_hash" in res_data
    assert len(res_data["audit_hash"]) == 64

def test_district_analytics():
    resp = client.get("/api/v1/analytics/district")
    assert resp.status_code == 200
    data = resp.json()
    assert "district_name" in data
    assert "tier_distribution" in data
    assert data["total_projects"] > 0
