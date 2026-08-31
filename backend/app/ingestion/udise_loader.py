# backend/app/ingestion/udise_loader.py
# Ingestion and normalization of UDISE+ open data records

from datetime import date
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.db.models import School, SchoolAnnualState
from backend.app.ingestion.hasher import compute_sha256_dict

def ingest_udise_records(
    db: Session,
    schools_data: List[Dict[str, Any]],
    states_data: List[Dict[str, Any]]
) -> Dict[str, int]:
    """
    Ingests parsed UDISE+ school directory and annual infrastructure records into database.
    """
    schools_added = 0
    states_added = 0

    for s_dict in schools_data:
        code = s_dict["udise_code"]
        existing = db.query(School).filter(School.udise_code == code).first()
        if not existing:
            school = School(
                udise_code=code,
                name_canonical=s_dict.get("name_canonical", ""),
                state_lgd_code=s_dict.get("state_lgd_code", 2),
                district_lgd_code=s_dict.get("district_lgd_code", 12),
                block_lgd_code=s_dict.get("block_lgd_code", 101),
                village_name=s_dict.get("village_name"),
                latitude=s_dict.get("latitude"),
                longitude=s_dict.get("longitude"),
                management_category=s_dict.get("management_category", "GOVERNMENT"),
                operational_status=s_dict.get("operational_status", "OPERATIONAL")
            )
            db.add(school)
            schools_added += 1

    db.flush()

    for st_dict in states_data:
        code = st_dict["udise_code"]
        year = st_dict["academic_year"]
        existing_state = db.query(SchoolAnnualState).filter(
            SchoolAnnualState.udise_code == code,
            SchoolAnnualState.academic_year == year
        ).first()

        if not existing_state:
            state_record = SchoolAnnualState(
                udise_code=code,
                academic_year=year,
                total_enrollment=st_dict.get("total_enrollment", 0),
                girls_enrollment=st_dict.get("girls_enrollment", 0),
                boys_enrollment=st_dict.get("boys_enrollment", 0),
                total_classrooms=st_dict.get("total_classrooms", 0),
                good_condition_classrooms=st_dict.get("good_condition_classrooms", 0),
                classrooms_dilapidated=st_dict.get("classrooms_dilapidated", 0),
                has_electricity=st_dict.get("has_electricity", True),
                has_drinking_water=st_dict.get("has_drinking_water", True),
                functional_girls_toilets=st_dict.get("functional_girls_toilets", 0),
                functional_boys_toilets=st_dict.get("functional_boys_toilets", 0),
                has_computer_lab=st_dict.get("has_computer_lab", False),
                total_computers=st_dict.get("total_computers", 0),
                data_freeze_date=st_dict.get("data_freeze_date", date(2023, 9, 30)),
                data_published_date=st_dict.get("data_published_date"),
                source_sha256=compute_sha256_dict(st_dict)
            )
            db.add(state_record)
            states_added += 1

    db.commit()
    return {"schools_ingested": schools_added, "states_ingested": states_added}
