# backend/scripts/load_realtime_data.py
# Ingests authentic UDISE+ ground truth records and real-world e-SAKSHI project claims

import os
import json
from backend.app.db.session import engine, Base, get_db_context
from backend.app.ingestion.live_udise_loader import ingest_udise_records
from backend.app.ingestion.live_esakshi_loader import process_live_esakshi_batch

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
UDISE_FILE = os.path.join(DATA_DIR, "udise_kangra_authentic.json")
ESAKSHI_FILE = os.path.join(DATA_DIR, "esakshi_live_claims.json")

def load_realtime_data():
    """Initializes database schema and ingests authentic UDISE+ and live e-SAKSHI datasets."""
    print("==================================================================")
    print("  MEEV Core - Ingesting Authentic Real-World Ground Truth Data")
    print("==================================================================")
    
    # 1. Initialize schema
    Base.metadata.create_all(bind=engine)

    # 2. Ingest Authentic UDISE+ Schools & Longitudinal States
    print("\n[1/2] Ingesting Authentic UDISE+ School Census Data...")
    if os.path.exists(UDISE_FILE):
        with open(UDISE_FILE, "r", encoding="utf-8") as f:
            udise_records = json.load(f)
        with get_db_context() as db:
            udise_stats = ingest_udise_records(db, udise_records)
        print(f"  --> Ingested {udise_stats['schools_ingested']} real school masters with SHA-256 provenance.")
        print(f"  --> Ingested {udise_stats['states_ingested']} longitudinal annual state records.")
    else:
        print(f"  [ERROR] UDISE dataset not found at {UDISE_FILE}")

    # 3. Ingest Real e-SAKSHI Project Claims
    print("\n[2/2] Processing Real-Time e-SAKSHI Claims through 7-Stage Matcher & 4-Lane Engine...")
    if os.path.exists(ESAKSHI_FILE):
        with open(ESAKSHI_FILE, "r", encoding="utf-8") as f:
            esakshi_claims = json.load(f)
        with get_db_context() as db:
            evaluated_cases = process_live_esakshi_batch(db, esakshi_claims)
        print(f"  --> Evaluated {len(evaluated_cases)} live e-SAKSHI project claims.")
        for ec in evaluated_cases:
            print(f"      • Work ID: {ec['project_id']} -> {ec['school_name']} | IPI: {ec['ipi_score']}/100 (Tier {ec['risk_tier']}) [{ec['primary_category']}]")
    else:
        print(f"  [ERROR] e-SAKSHI dataset not found at {ESAKSHI_FILE}")

    print("\n[SUCCESS] Authentic data loaded. Streaming API ready on POST /api/v1/ingest/stream.")

if __name__ == "__main__":
    load_realtime_data()
