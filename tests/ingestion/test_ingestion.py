import sys
import os
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Ensure root directory is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.db.session import Base
from backend.app.db.models import School, SchoolAnnualState, MPLADSProject, InvestigationCase, AuditLog
from backend.app.ingestion.hasher import compute_sha256_dict, compute_sha256_bytes

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def test_db():
    """Fixture to provide a clean, isolated in-memory test database."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_schema_creation(test_db):
    """Verify that all 5 database tables create without SQL syntax errors."""
    inspector = inspect(test_db.bind)
    tables = inspector.get_table_names()
    
    assert "schools" in tables, "schools table not found"
    assert "school_annual_states" in tables, "school_annual_states table not found"
    assert "mplads_projects" in tables, "mplads_projects table not found"
    assert "investigation_cases" in tables, "investigation_cases table not found"
    assert "audit_log" in tables, "audit_log table not found"

def test_udise_loading(test_db):
    """Verify load_udise_data.py inserts schools and longitudinal annual states with valid FKs."""
    from backend.scripts.load_udise_data import load_canonical_schools, load_background_cohort
    
    load_canonical_schools(test_db)
    load_background_cohort(test_db, num_schools=15)
    
    # Check canonical school GHS Rampur
    rampur = test_db.query(School).filter(School.udise_code == "02120100402").first()
    assert rampur is not None
    assert rampur.name_canonical == "Government High School Rampur"
    assert rampur.management_category == "GOVERNMENT"
    
    # Check foreign key linkage to annual states
    states = test_db.query(SchoolAnnualState).filter(SchoolAnnualState.udise_code == "02120100402").all()
    assert len(states) == 2
    for state in states:
        assert state.school.name_canonical == "Government High School Rampur"
        
    # Check total school count (4 canonical + 15 background = 19)
    assert test_db.query(School).count() == 19

def test_sha256_provenance(test_db):
    """Verify that every school_annual_states record has a 64-character SHA-256 hash in source_sha256."""
    from backend.scripts.load_udise_data import load_canonical_schools
    
    load_canonical_schools(test_db)
    
    states = test_db.query(SchoolAnnualState).all()
    assert len(states) > 0
    for state in states:
        assert state.source_sha256 is not None
        assert len(state.source_sha256) == 64
        # Assert it's a valid hex digest
        assert all(c in "0123456789abcdef" for c in state.source_sha256.lower())

def test_spatial_geometry(test_db):
    """Verify that coordinates parse into valid floating-point latitude/longitude points and location."""
    from backend.scripts.load_udise_data import load_canonical_schools
    
    load_canonical_schools(test_db)
    
    school = test_db.query(School).filter(School.udise_code == "02120200114").first()
    assert school.latitude == 32.2184
    assert school.longitude == 76.3201
    
    # Check the location column formats as a text-encoded POINT for SQLite
    assert school.location is not None
    assert "POINT" in school.location
    assert "76.3201" in school.location
    assert "32.2184" in school.location

def test_deterministic_project_generation(test_db):
    """Verify generate_synthetic_esakshi.py deterministically populates project records."""
    from backend.scripts.load_udise_data import load_canonical_schools, load_background_cohort
    from backend.scripts.generate_synthetic_esakshi import load_canonical_projects, generate_background_projects
    
    # Load dependency schools
    load_canonical_schools(test_db)
    load_background_cohort(test_db, num_schools=10)
    
    # Load and generate projects
    load_canonical_projects(test_db)
    generate_background_projects(test_db, total_projects=40)
    
    # Assert canonical projects match constraints
    p_rampur = test_db.query(MPLADSProject).filter(MPLADSProject.project_id == "PRJ-2023-04567").first()
    assert p_rampur is not None
    assert p_rampur.resolved_udise_code == "02120100402"
    assert p_rampur.sanction_cost == 1240000.00
    assert p_rampur.canonical_asset_type == "CLASSROOM"
    
    p_xavier = test_db.query(MPLADSProject).filter(MPLADSProject.project_id == "PRJ-2023-01124").first()
    assert p_xavier is not None
    assert p_xavier.resolved_udise_code == "02120109981"
    assert p_xavier.sanction_cost == 850000.00
    
    p_dharamshala = test_db.query(MPLADSProject).filter(MPLADSProject.project_id == "PRJ-2023-08912").first()
    assert p_dharamshala is not None
    assert p_dharamshala.resolved_udise_code == "02120200114"
    assert p_dharamshala.sanction_cost == 450000.00
    
    p_palampur = test_db.query(MPLADSProject).filter(MPLADSProject.project_id == "PRJ-2023-03319").first()
    assert p_palampur is not None
    assert p_palampur.resolved_udise_code == "02120300552"
    assert p_palampur.sanction_cost == 1400000.00
    
    # Assert total projects generated matches count
    assert test_db.query(MPLADSProject).count() == 40
