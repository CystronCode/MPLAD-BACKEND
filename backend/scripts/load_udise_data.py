import sys
import os
import random
from datetime import date

# Ensure root directory is in the python path for direct script execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.db.session import engine, get_db, Base
from backend.app.db.models import School, SchoolAnnualState, GeometryColumn
from backend.app.ingestion.hasher import compute_sha256_dict

def create_tables_if_not_exists():
    """Ensure database schema is created."""
    Base.metadata.create_all(bind=engine)

def clear_existing_data(db):
    """Clean tables before reload to guarantee idempotence."""
    db.query(SchoolAnnualState).delete()
    db.query(School).delete()
    db.commit()

def get_location_geom(db, lon, lat):
    """Format spatial point depending on the database dialect."""
    if db.bind.dialect.name == "sqlite":
        return f"POINT({lon} {lat})"
    else:
        from sqlalchemy import func
        return func.ST_GeomFromText(f"POINT({lon} {lat})", 4326)

def load_canonical_schools(db):
    print("Loading canonical schools...")
    
    # Define the 4 reference institutions
    schools_data = [
        {
            "udise_code": "02120100402",
            "name_canonical": "Government High School Rampur",
            "state_lgd_code": 2,
            "district_lgd_code": 12,
            "block_lgd_code": 1201,
            "village_name": "Rampur",
            "latitude": 32.1152,
            "longitude": 76.2205,
            "management_category": "GOVERNMENT",
            "operational_status": "OPERATIONAL",
            "states": [
                {
                    "academic_year": "2022-23",
                    "total_enrollment": 43,
                    "girls_enrollment": 20,
                    "boys_enrollment": 23,
                    "total_classrooms": 7,
                    "good_condition_classrooms": 5,
                    "classrooms_dilapidated": 0,
                    "has_electricity": True,
                    "has_drinking_water": True,
                    "functional_girls_toilets": 1,
                    "functional_boys_toilets": 1,
                    "has_computer_lab": False,
                    "total_computers": 0,
                    "data_freeze_date": date(2023, 9, 30),
                    "data_published_date": date(2024, 3, 31),
                },
                {
                    "academic_year": "2023-24",
                    "total_enrollment": 31,
                    "girls_enrollment": 15,
                    "boys_enrollment": 16,
                    "total_classrooms": 7,
                    "good_condition_classrooms": 5,
                    "classrooms_dilapidated": 0,
                    "has_electricity": True,
                    "has_drinking_water": True,
                    "functional_girls_toilets": 1,
                    "functional_boys_toilets": 1,
                    "has_computer_lab": False,
                    "total_computers": 0,
                    "data_freeze_date": date(2024, 9, 30),
                    "data_published_date": date(2025, 3, 31),
                }
            ]
        },
        {
            "udise_code": "02120109981",
            "name_canonical": "St. Xavier Academy Kangra",
            "state_lgd_code": 2,
            "district_lgd_code": 12,
            "block_lgd_code": 1201,
            "village_name": "Kangra Town",
            "latitude": 32.0998,
            "longitude": 76.2691,
            "management_category": "PRIVATE_UNAIDED",
            "operational_status": "OPERATIONAL",
            "states": [
                {
                    "academic_year": "2022-23",
                    "total_enrollment": 320,
                    "girls_enrollment": 150,
                    "boys_enrollment": 170,
                    "total_classrooms": 14,
                    "good_condition_classrooms": 12,
                    "classrooms_dilapidated": 0,
                    "has_electricity": True,
                    "has_drinking_water": True,
                    "functional_girls_toilets": 4,
                    "functional_boys_toilets": 4,
                    "has_computer_lab": True,
                    "total_computers": 15,
                    "data_freeze_date": date(2023, 9, 30),
                    "data_published_date": date(2024, 3, 31),
                },
                {
                    "academic_year": "2023-24",
                    "total_enrollment": 320,
                    "girls_enrollment": 150,
                    "boys_enrollment": 170,
                    "total_classrooms": 14,
                    "good_condition_classrooms": 12,
                    "classrooms_dilapidated": 0,
                    "has_electricity": True,
                    "has_drinking_water": True,
                    "functional_girls_toilets": 4,
                    "functional_boys_toilets": 4,
                    "has_computer_lab": True,
                    "total_computers": 15,
                    "data_freeze_date": date(2024, 9, 30),
                    "data_published_date": date(2025, 3, 31),
                }
            ]
        },
        {
            "udise_code": "02120200114",
            "name_canonical": "Government Primary School Dharamshala",
            "state_lgd_code": 2,
            "district_lgd_code": 12,
            "block_lgd_code": 1202,
            "village_name": "Dharamshala",
            "latitude": 32.2184,
            "longitude": 76.3201,
            "management_category": "GOVERNMENT",
            "operational_status": "OPERATIONAL",
            "states": [
                {
                    "academic_year": "2022-23",
                    "total_enrollment": 19,
                    "girls_enrollment": 9,
                    "boys_enrollment": 10,
                    "total_classrooms": 5,
                    "good_condition_classrooms": 3,
                    "classrooms_dilapidated": 0,
                    "has_electricity": True,
                    "has_drinking_water": True,
                    "functional_girls_toilets": 1,
                    "functional_boys_toilets": 1,
                    "has_computer_lab": False,
                    "total_computers": 0,
                    "data_freeze_date": date(2023, 9, 30),
                    "data_published_date": date(2024, 3, 31),
                },
                {
                    "academic_year": "2023-24",
                    "total_enrollment": 19,
                    "girls_enrollment": 9,
                    "boys_enrollment": 10,
                    "total_classrooms": 5,
                    "good_condition_classrooms": 3,
                    "classrooms_dilapidated": 0,
                    "has_electricity": True,
                    "has_drinking_water": True,
                    "functional_girls_toilets": 1,
                    "functional_boys_toilets": 1,
                    "has_computer_lab": False,
                    "total_computers": 0,
                    "data_freeze_date": date(2024, 9, 30),
                    "data_published_date": date(2025, 3, 31),
                }
            ]
        },
        {
            "udise_code": "02120300552",
            "name_canonical": "Government Senior Secondary School Palampur",
            "state_lgd_code": 2,
            "district_lgd_code": 12,
            "block_lgd_code": 1203,
            "village_name": "Palampur",
            "latitude": 32.1182,
            "longitude": 76.5306,
            "management_category": "GOVERNMENT",
            "operational_status": "OPERATIONAL",
            "states": [
                {
                    "academic_year": "2022-23",
                    "total_enrollment": 210,
                    "girls_enrollment": 100,
                    "boys_enrollment": 110,
                    "total_classrooms": 12,
                    "good_condition_classrooms": 10,
                    "classrooms_dilapidated": 0,
                    "has_electricity": True,
                    "has_drinking_water": True,
                    "functional_girls_toilets": 3,
                    "functional_boys_toilets": 3,
                    "has_computer_lab": True,
                    "total_computers": 10,
                    "data_freeze_date": date(2023, 9, 30),
                    "data_published_date": date(2024, 3, 31),
                },
                {
                    "academic_year": "2023-24",
                    "total_enrollment": 210,
                    "girls_enrollment": 100,
                    "boys_enrollment": 110,
                    "total_classrooms": 14,  # Reflected completed construction project (+2 rooms)
                    "good_condition_classrooms": 12,
                    "classrooms_dilapidated": 0,
                    "has_electricity": True,
                    "has_drinking_water": True,
                    "functional_girls_toilets": 3,
                    "functional_boys_toilets": 3,
                    "has_computer_lab": True,
                    "total_computers": 10,
                    "data_freeze_date": date(2024, 9, 30),
                    "data_published_date": date(2025, 3, 31),
                }
            ]
        }
    ]

    for data in schools_data:
        school = School(
            udise_code=data["udise_code"],
            name_canonical=data["name_canonical"],
            state_lgd_code=data["state_lgd_code"],
            district_lgd_code=data["district_lgd_code"],
            block_lgd_code=data["block_lgd_code"],
            village_name=data["village_name"],
            location=get_location_geom(db, data["longitude"], data["latitude"]),
            latitude=data["latitude"],
            longitude=data["longitude"],
            management_category=data["management_category"],
            operational_status=data["operational_status"]
        )
        db.add(school)
        db.flush()  # Push to get reference for foreign key integrity

        for s_data in data["states"]:
            # Setup payload dict for deterministic hashing
            payload = {
                "udise_code": data["udise_code"],
                "academic_year": s_data["academic_year"],
                "total_enrollment": s_data["total_enrollment"],
                "girls_enrollment": s_data["girls_enrollment"],
                "boys_enrollment": s_data["boys_enrollment"],
                "total_classrooms": s_data["total_classrooms"],
                "good_condition_classrooms": s_data["good_condition_classrooms"],
                "classrooms_dilapidated": s_data["classrooms_dilapidated"],
                "has_electricity": s_data["has_electricity"],
                "has_drinking_water": s_data["has_drinking_water"],
                "functional_girls_toilets": s_data["functional_girls_toilets"],
                "functional_boys_toilets": s_data["functional_boys_toilets"],
                "has_computer_lab": s_data["has_computer_lab"],
                "total_computers": s_data["total_computers"],
                "data_freeze_date": s_data["data_freeze_date"].isoformat(),
                "data_published_date": s_data["data_published_date"].isoformat() if s_data["data_published_date"] else None
            }
            sha_hash = compute_sha256_dict(payload)
            
            annual_state = SchoolAnnualState(
                udise_code=data["udise_code"],
                academic_year=s_data["academic_year"],
                total_enrollment=s_data["total_enrollment"],
                girls_enrollment=s_data["girls_enrollment"],
                boys_enrollment=s_data["boys_enrollment"],
                total_classrooms=s_data["total_classrooms"],
                good_condition_classrooms=s_data["good_condition_classrooms"],
                classrooms_dilapidated=s_data["classrooms_dilapidated"],
                has_electricity=s_data["has_electricity"],
                has_drinking_water=s_data["has_drinking_water"],
                functional_girls_toilets=s_data["functional_girls_toilets"],
                functional_boys_toilets=s_data["functional_boys_toilets"],
                has_computer_lab=s_data["has_computer_lab"],
                total_computers=s_data["total_computers"],
                data_freeze_date=s_data["data_freeze_date"],
                data_published_date=s_data["data_published_date"],
                source_sha256=sha_hash
            )
            db.add(annual_state)
    db.commit()
    print("Canonical schools loaded successfully.")

def load_background_cohort(db, num_schools=200):
    print(f"Generating and loading {num_schools} background schools for Kangra district baseline...")
    random.seed(42)  # Maintain 100% deterministic reproducibility
    
    generated_udise_codes = set(["02120100402", "02120109981", "02120200114", "02120300552"])
    
    school_types = [
        ("Government Primary School", "GOVERNMENT"),
        ("Government Middle School", "GOVERNMENT"),
        ("Government High School", "GOVERNMENT"),
        ("Government Senior Secondary School", "GOVERNMENT"),
        ("DAV Public School", "PRIVATE_UNAIDED"),
        ("Himachal Education Academy", "PRIVATE_UNAIDED"),
        ("Army Public School", "GOVT_AIDED")
    ]
    
    villages = ["Dhar", "Shahpur", "Nagrota", "Indora", "Dehra", "Jawali", "Baijnath", "Nurpur", "Jaisinghpur", "Fatehpur"]
    
    count = 0
    while count < num_schools:
        block_num = random.randint(1, 10)
        block_code_str = f"{block_num:02d}"
        school_num = random.randint(1, 99999)
        udise_code = f"0212{block_code_str}{school_num:05d}"
        
        if udise_code in generated_udise_codes:
            continue
            
        generated_udise_codes.add(udise_code)
        
        type_prefix, mgmt = random.choice(school_types)
        village = random.choice(villages)
        name_canonical = f"{type_prefix} {village} #{count + 1}"
        
        # Geolocation inside Kangra bounding box roughly
        latitude = round(random.uniform(32.0, 32.3), 5)
        longitude = round(random.uniform(76.1, 76.6), 5)
        
        school = School(
            udise_code=udise_code,
            name_canonical=name_canonical,
            state_lgd_code=2,
            district_lgd_code=12,
            block_lgd_code=1200 + block_num,
            village_name=village,
            location=get_location_geom(db, longitude, latitude),
            latitude=latitude,
            longitude=longitude,
            management_category=mgmt,
            operational_status="OPERATIONAL"
        )
        db.add(school)
        db.flush()
        
        # Generate states for both academic years
        total_classrooms = random.randint(3, 20)
        base_enrollment = random.randint(15, 300)
        
        for year, freeze_d, pub_d in [
            ("2022-23", date(2023, 9, 30), date(2024, 3, 31)),
            ("2023-24", date(2024, 9, 30), date(2025, 3, 31))
        ]:
            # Simple randomized longitudinal variation
            enrollment = max(10, base_enrollment + random.randint(-15, 15))
            girls = int(enrollment * random.uniform(0.4, 0.55))
            boys = enrollment - girls
            
            good_rooms = max(1, total_classrooms - random.randint(0, 3))
            dilapidated = random.randint(0, 2)
            
            has_electricity = random.random() < 0.95
            has_water = random.random() < 0.98
            girls_toilets = random.randint(1, 4)
            boys_toilets = random.randint(1, 4)
            
            has_lab = random.random() < 0.3
            total_computers = random.randint(5, 15) if has_lab else 0
            
            state_payload = {
                "udise_code": udise_code,
                "academic_year": year,
                "total_enrollment": enrollment,
                "girls_enrollment": girls,
                "boys_enrollment": boys,
                "total_classrooms": total_classrooms,
                "good_condition_classrooms": good_rooms,
                "classrooms_dilapidated": dilapidated,
                "has_electricity": has_electricity,
                "has_drinking_water": has_water,
                "functional_girls_toilets": girls_toilets,
                "functional_boys_toilets": boys_toilets,
                "has_computer_lab": has_lab,
                "total_computers": total_computers,
                "data_freeze_date": freeze_d.isoformat(),
                "data_published_date": pub_d.isoformat()
            }
            sha_hash = compute_sha256_dict(state_payload)
            
            annual_state = SchoolAnnualState(
                udise_code=udise_code,
                academic_year=year,
                total_enrollment=enrollment,
                girls_enrollment=girls,
                boys_enrollment=boys,
                total_classrooms=total_classrooms,
                good_condition_classrooms=good_rooms,
                classrooms_dilapidated=dilapidated,
                has_electricity=has_electricity,
                has_drinking_water=has_water,
                functional_girls_toilets=girls_toilets,
                functional_boys_toilets=boys_toilets,
                has_computer_lab=has_lab,
                total_computers=total_computers,
                data_freeze_date=freeze_d,
                data_published_date=pub_d,
                source_sha256=sha_hash
            )
            db.add(annual_state)
            
        count += 1
        
    db.commit()
    print(f"Loaded {num_schools} background schools successfully.")

from backend.app.db.session import get_db_context

def main():
    create_tables_if_not_exists()
    with get_db_context() as db:
        clear_existing_data(db)
        load_canonical_schools(db)
        load_background_cohort(db)
    print("Database loading script completed successfully.")

load_schools = main

if __name__ == "__main__":
    main()
