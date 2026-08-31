import json
from pathlib import Path
import pytest
from contracts.models import (
    CanonicalAssetType,
    SchoolManagement,
    OperationalStatus,
    ResolutionStatus,
    RiskTier,
    CaseStatus,
    SchoolMasterSchema,
    SchoolAnnualStateSchema,
    MPLADSProjectSchema,
    InvestigationCaseSummary,
    InvestigationCaseDetail,
    D3GraphPayload
)

def test_contract_models_and_enums():
    assert CanonicalAssetType.ADDITIONAL_CLASSROOM == "ADDITIONAL_CLASSROOM"
    assert RiskTier.TIER_3_FIELD_INSPECTION == 3
    assert SchoolManagement.GOVERNMENT == "GOVERNMENT"

def test_mock_data_validity():
    mock_file = Path("contracts/mock_data.json")
    assert mock_file.exists(), "mock_data.json must exist"
    
    with open(mock_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert "cases" in data
    assert len(data["cases"]) > 0
    
    # Validate each case with Pydantic
    for case_raw in data["cases"]:
        detail = InvestigationCaseDetail(**case_raw)
        assert detail.case_id
        assert detail.ipi_score >= 0
        assert len(detail.evidence_graph.nodes) > 0
        assert len(detail.evidence_graph.links) > 0

def test_db_schema_exists():
    schema_file = Path("contracts/db_schema.sql")
    assert schema_file.exists()
    content = schema_file.read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS schools" in content
    assert "CREATE TABLE IF NOT EXISTS school_annual_states" in content
    assert "CREATE TABLE IF NOT EXISTS mplads_projects" in content
    assert "CREATE TABLE IF NOT EXISTS investigation_cases" in content
    assert "CREATE TABLE IF NOT EXISTS audit_log" in content

def test_openapi_spec_exists():
    openapi_file = Path("contracts/openapi.yaml")
    assert openapi_file.exists()
    content = openapi_file.read_text(encoding="utf-8")
    assert "/cases" in content
    assert "/cases/{case_id}/evidence-graph" in content
    assert "/cases/{case_id}/notice/pdf" in content
