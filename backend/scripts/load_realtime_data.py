# backend/scripts/load_realtime_data.py
# Ingests authentic UDISE+ ground truth records and real-world e-SAKSHI project claims for all 28 Karnataka Constituencies

import os
import json
from backend.app.db.session import engine, Base, get_db_context
from backend.app.db.models import School, SchoolAnnualState, MPLADSProject, InvestigationCase, AuditLog
from backend.app.ingestion.live_udise_loader import ingest_udise_records
from backend.app.ingestion.live_esakshi_loader import process_live_esakshi_batch

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
UDISE_FILE = os.path.join(DATA_DIR, "karnataka_all_schools.json")
WORKS_FILE = os.path.join(DATA_DIR, "karnataka_all_works.json")

def load_realtime_data(clear_first: bool = True):
    """Initializes database schema and ingests authentic UDISE+ and live e-SAKSHI datasets for all 28 Karnataka Constituencies."""
    print("==================================================================")
    print("  MEEV Core - Ingesting Karnataka State 28-Constituency Data")
    print("==================================================================")
    
    # 1. Initialize schema
    Base.metadata.create_all(bind=engine)

    if clear_first:
        with get_db_context() as db:
            print("\n[0/2] Clearing previous records for clean Karnataka State initialization...")
            db.query(AuditLog).delete()
            db.query(InvestigationCase).delete()
            db.query(MPLADSProject).delete()
            db.query(SchoolAnnualState).delete()
            db.query(School).delete()
            db.commit()

    # 2. Ingest Authentic UDISE+ Schools & Longitudinal States
    print("\n[1/2] Ingesting Karnataka State UDISE+ School Census Data across 28 seats...")
    if os.path.exists(UDISE_FILE):
        with open(UDISE_FILE, "r", encoding="utf-8") as f:
            udise_records = json.load(f)
        with get_db_context() as db:
            udise_stats = ingest_udise_records(db, udise_records)
        print(f"  --> Ingested {udise_stats['schools_ingested']} schools across 28 Parliamentary Constituencies.")
        print(f"  --> Ingested {udise_stats['states_ingested']} longitudinal annual state records.")

    # 3. Ingest Real e-SAKSHI Project Claims
    print("\n[2/2] Processing Real-Time e-SAKSHI Claims through 7-Stage Matcher & 4-Lane Engine...")
    if os.path.exists(WORKS_FILE):
        with open(WORKS_FILE, "r", encoding="utf-8") as f:
            esakshi_claims = json.load(f)
        with get_db_context() as db:
            evaluated_cases = process_live_esakshi_batch(db, esakshi_claims)
        print(f"  --> Evaluated {len(evaluated_cases)} live claims across all 28 Karnataka Constituencies.")

    print("\n[SUCCESS] Karnataka State 28-Constituency data loaded. Streaming API ready on POST /api/v1/ingest/stream.")

if __name__ == "__main__":
    load_realtime_data(clear_first=True)
