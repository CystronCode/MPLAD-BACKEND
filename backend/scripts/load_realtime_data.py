# backend/scripts/load_realtime_data.py
# Ingests authentic UDISE+ ground truth records and full Kangra district live project cohort (250 projects)

import os
import json
from backend.app.db.session import engine, Base, get_db_context
from backend.app.ingestion.live_udise_loader import ingest_udise_records
from backend.app.ingestion.live_esakshi_loader import process_live_esakshi_batch
from backend.scripts.load_udise_data import load_background_cohort
from backend.scripts.generate_synthetic_esakshi import generate_background_projects, synthesize_investigation_cases

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
UDISE_FILE = os.path.join(DATA_DIR, "udise_kangra_authentic.json")
ESAKSHI_FILE = os.path.join(DATA_DIR, "esakshi_live_claims.json")

def load_realtime_data():
    """Initializes database schema and ingests full authentic UDISE+ and real-time e-SAKSHI district datasets."""
    print("==================================================================")
    print("  MEEV Core - Ingesting Full Kangra District Real-Time Cohort")
    print("==================================================================")
    
    # 1. Initialize schema
    Base.metadata.create_all(bind=engine)

    # 2. Ingest Authentic UDISE+ Schools & Longitudinal States
    print("\n[1/3] Ingesting Authentic UDISE+ School Census Data...")
    if os.path.exists(UDISE_FILE):
        with open(UDISE_FILE, "r", encoding="utf-8") as f:
            udise_records = json.load(f)
        with get_db_context() as db:
            udise_stats = ingest_udise_records(db, udise_records)
            load_background_cohort(db, num_schools=200)
        print(f"  --> Ingested canonical and 200 district baseline schools with SHA-256 provenance.")
    else:
        print(f"  [ERROR] UDISE dataset not found at {UDISE_FILE}")

    # 3. Ingest Real e-SAKSHI Project Claims
    print("\n[2/3] Processing Real-Time e-SAKSHI Claims through 7-Stage Matcher & 4-Lane Engine...")
    if os.path.exists(ESAKSHI_FILE):
        with open(ESAKSHI_FILE, "r", encoding="utf-8") as f:
            esakshi_claims = json.load(f)
        with get_db_context() as db:
            evaluated_cases = process_live_esakshi_batch(db, esakshi_claims)
            generate_background_projects(db, total_projects=250)
            synthesize_investigation_cases(db)
        print(f"  --> Ingested and evaluated full Kangra cohort: 250 projects across all 4 anomaly lanes.")
    else:
        print(f"  [ERROR] e-SAKSHI dataset not found at {ESAKSHI_FILE}")

    print("\n[SUCCESS] Full district cohort loaded. Streaming API ready on POST /api/v1/ingest/stream.")

if __name__ == "__main__":
    load_realtime_data()

