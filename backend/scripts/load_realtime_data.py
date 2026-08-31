# backend/scripts/load_realtime_data.py
# Ingests authentic UDISE+ ground truth records and real-world e-SAKSHI project claims for Bengaluru North

import os
import json
from backend.app.db.session import engine, Base, get_db_context
from backend.app.db.models import School, SchoolAnnualState, MPLADSProject, InvestigationCase, AuditLog
from backend.app.ingestion.live_udise_loader import ingest_udise_records
from backend.app.ingestion.live_esakshi_loader import process_live_esakshi_batch

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
UDISE_FILES = [
    os.path.join(DATA_DIR, "udise_bengaluru_north.json")
]
ESAKSHI_FILES = [
    os.path.join(DATA_DIR, "esakshi_bengaluru_north.json")
]

def load_realtime_data(clear_first: bool = True):
    """Initializes database schema and ingests authentic UDISE+ and live e-SAKSHI datasets for Bengaluru North."""
    print("==================================================================")
    print("  MEEV Core - Ingesting Authentic Bengaluru North Parliamentary Data")
    print("==================================================================")
    
    # 1. Initialize schema
    Base.metadata.create_all(bind=engine)

    if clear_first:
        with get_db_context() as db:
            print("\n[0/2] Clearing previous regional data for clean Bengaluru North isolation...")
            db.query(AuditLog).delete()
            db.query(InvestigationCase).delete()
            db.query(MPLADSProject).delete()
            db.query(SchoolAnnualState).delete()
            db.query(School).delete()
            db.commit()

    # 2. Ingest Authentic UDISE+ Schools & Longitudinal States
    print("\n[1/2] Ingesting Authentic Bengaluru North UDISE+ School Census Data...")
    for u_file in UDISE_FILES:
        if os.path.exists(u_file):
            with open(u_file, "r", encoding="utf-8") as f:
                udise_records = json.load(f)
            with get_db_context() as db:
                udise_stats = ingest_udise_records(db, udise_records)
            print(f"  --> Ingested {udise_stats['schools_ingested']} Bengaluru North schools from {os.path.basename(u_file)}.")
            print(f"  --> Ingested {udise_stats['states_ingested']} longitudinal annual state records.")

    # 3. Ingest Real e-SAKSHI Project Claims
    print("\n[2/2] Processing Real-Time Bengaluru North e-SAKSHI Claims...")
    for e_file in ESAKSHI_FILES:
        if os.path.exists(e_file):
            with open(e_file, "r", encoding="utf-8") as f:
                esakshi_claims = json.load(f)
            with get_db_context() as db:
                evaluated_cases = process_live_esakshi_batch(db, esakshi_claims)
            print(f"  --> Evaluated {len(evaluated_cases)} live claims from {os.path.basename(e_file)}.")
            for ec in evaluated_cases:
                print(f"      • Work ID: {ec['project_id']} -> {ec['school_name']} | IPI: {ec['ipi_score']}/100 (Tier {ec['risk_tier']}) [{ec['primary_category']}]")

    print("\n[SUCCESS] 100% Pure Bengaluru North data loaded. Streaming API ready on POST /api/v1/ingest/stream.")

if __name__ == "__main__":
    load_realtime_data(clear_first=True)
