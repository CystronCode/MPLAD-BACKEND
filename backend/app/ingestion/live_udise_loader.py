# backend/app/ingestion/live_udise_loader.py
# Production UDISE+ Ingestion Connector with SHA-256 Provenance

import os
import json
import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.db.models import School, SchoolAnnualState, GeometryColumn
from backend.app.ingestion.hasher import compute_sha256_dict
from backend.app.db.session import get_db_context, engine, Base

logger = logging.getLogger("meev.ingestion.udise")

def get_location_geom(db: Session, lon: float, lat: float):
    """Format spatial point depending on the database dialect."""
    if db.bind.dialect.name == "sqlite":
        return f"POINT({lon} {lat})"
    else:
        from sqlalchemy import func
        return func.ST_GeomFromText(f"POINT({lon} {lat})", 4326)

def parse_date(val: Any) -> Optional[date]:
    if not val:
        return None
    if isinstance(val, date):
        return val
    if isinstance(val, str):
        try:
            return datetime.strptime(val[:10], "%Y-%m-%d").date()
        except Exception:
            return None
    return None

def ingest_udise_records(db: Session, records: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Ingests authentic UDISE+ school masters and longitudinal annual states with cryptographic SHA-256 provenance.
    """
    schools_ingested = 0
    states_ingested = 0

    for s_data in records:
        udise_code = str(s_data["udise_code"]).strip()
        name = str(s_data["name_canonical"]).strip()
        lat = float(s_data["latitude"]) if s_data.get("latitude") is not None else None
        lon = float(s_data["longitude"]) if s_data.get("longitude") is not None else None
        
        school = db.query(School).filter(School.udise_code == udise_code).first()
        if not school:
            school = School(
                udise_code=udise_code,
                name_canonical=name,
                state_lgd_code=int(s_data.get("state_lgd_code", 2)),
                district_lgd_code=int(s_data.get("district_lgd_code", 12)),
                block_lgd_code=int(s_data.get("block_lgd_code", 1201)),
                village_name=s_data.get("village_name", ""),
                location=get_location_geom(db, lon, lat) if lon is not None and lat is not None else None,
                latitude=lat,
                longitude=lon,
                management_category=s_data.get("management_category", "GOVERNMENT"),
                operational_status=s_data.get("operational_status", "OPERATIONAL")
            )
            db.add(school)
            schools_ingested += 1
        else:
            school.name_canonical = name
            school.management_category = s_data.get("management_category", school.management_category)
            school.operational_status = s_data.get("operational_status", school.operational_status)
            if lat is not None and lon is not None:
                school.latitude = lat
                school.longitude = lon
                school.location = get_location_geom(db, lon, lat)

        db.flush()

        for st in s_data.get("states", []):
            year = st.get("academic_year")
            if not year:
                continue

            state_payload = {
                "udise_code": udise_code,
                "academic_year": year,
                "total_enrollment": st.get("total_enrollment", 0),
                "girls_enrollment": st.get("girls_enrollment", 0),
                "boys_enrollment": st.get("boys_enrollment", 0),
                "total_classrooms": st.get("total_classrooms", 0),
                "good_condition_classrooms": st.get("good_condition_classrooms", 0),
                "classrooms_dilapidated": st.get("classrooms_dilapidated", 0),
                "has_electricity": st.get("has_electricity", True),
                "has_drinking_water": st.get("has_drinking_water", True),
                "functional_girls_toilets": st.get("functional_girls_toilets", 0),
                "functional_boys_toilets": st.get("functional_boys_toilets", 0),
                "has_computer_lab": st.get("has_computer_lab", False),
                "total_computers": st.get("total_computers", 0),
                "data_freeze_date": str(st.get("data_freeze_date")),
                "data_published_date": str(st.get("data_published_date")) if st.get("data_published_date") else None
            }
            sha_hash = compute_sha256_dict(state_payload)

            annual_state = db.query(SchoolAnnualState).filter(
                SchoolAnnualState.udise_code == udise_code,
                SchoolAnnualState.academic_year == year
            ).first()

            if not annual_state:
                annual_state = SchoolAnnualState(
                    udise_code=udise_code,
                    academic_year=year,
                    total_enrollment=st.get("total_enrollment", 0),
                    girls_enrollment=st.get("girls_enrollment", 0),
                    boys_enrollment=st.get("boys_enrollment", 0),
                    total_classrooms=st.get("total_classrooms", 0),
                    good_condition_classrooms=st.get("good_condition_classrooms", 0),
                    classrooms_dilapidated=st.get("classrooms_dilapidated", 0),
                    has_electricity=st.get("has_electricity", True),
                    has_drinking_water=st.get("has_drinking_water", True),
                    functional_girls_toilets=st.get("functional_girls_toilets", 0),
                    functional_boys_toilets=st.get("functional_boys_toilets", 0),
                    has_computer_lab=st.get("has_computer_lab", False),
                    total_computers=st.get("total_computers", 0),
                    data_freeze_date=parse_date(st.get("data_freeze_date")) or date(2023, 9, 30),
                    data_published_date=parse_date(st.get("data_published_date")),
                    source_sha256=sha_hash
                )
                db.add(annual_state)
                states_ingested += 1
            else:
                annual_state.total_enrollment = st.get("total_enrollment", annual_state.total_enrollment)
                annual_state.total_classrooms = st.get("total_classrooms", annual_state.total_classrooms)
                annual_state.source_sha256 = sha_hash

    db.commit()
    return {"schools_ingested": schools_ingested, "states_ingested": states_ingested}

def load_udise_from_file(file_path: str) -> Dict[str, int]:
    """Loads UDISE+ JSON file into database."""
    Base.metadata.create_all(bind=engine)
    with open(file_path, "r", encoding="utf-8") as f:
        records = json.load(f)
    with get_db_context() as db:
        return ingest_udise_records(db, records)
