import sys
import os
import random
from datetime import date, timedelta
from decimal import Decimal

# Ensure root directory is in the python path for direct script execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.db.session import engine, get_db, Base
from backend.app.db.models import School, MPLADSProject

def clear_existing_projects(db):
    """Clean the projects table to guarantee idempotence."""
    db.query(MPLADSProject).delete()
    db.commit()

def get_location_geom(db, lon, lat):
    """Format spatial point depending on the database dialect."""
    if db.bind.dialect.name == "sqlite":
        return f"POINT({lon} {lat})"
    else:
        from sqlalchemy import func
        return func.ST_GeomFromText(f"POINT({lon} {lat})", 4326)

def load_canonical_projects(db):
    print("Loading canonical demo projects...")
    
    # Coordinates of canonical schools (defined in load_udise_data.py)
    # Rampur: 32.1152, 76.2205
    # St. Xavier: 32.0998, 76.2691
    # Dharamshala: 32.2184, 76.3201
    # Palampur: 32.1182, 76.5306
    
    canonical_projects = [
        # 1. PRJ-2023-04567: Rampur Classroom Construction Anomaly (Baseline 7, Post 7 - reflection failure)
        {
            "project_id": "PRJ-2023-04567",
            "mp_id": "MP-LOK-HP-04",
            "district_lgd_code": 12,
            "work_description_raw": "Construction of 2 Additional Class rooms at GHS Rampur Block-1",
            "canonical_asset_type": "CLASSROOM",
            "target_quantity": 2,
            "sanction_cost": Decimal("1240000.00"),
            "recommendation_date": date(2023, 3, 10),
            "sanction_date": date(2023, 4, 15),
            "completion_date": date(2023, 5, 8),  # 23 days (Velocity violation / Physical impossibility!)
            "latitude": 32.1153,  # minor offset from 32.1152
            "longitude": 76.2206, # minor offset from 76.2205
            "resolved_udise_code": "02120100402",
            "resolution_confidence": Decimal("0.985"),
            "resolution_status": "AUTO_ACCEPTED"
        },
        # 2. PRJ-2023-01124: Private Beneficiary Anomaly (St Xavier Academy Kangra)
        {
            "project_id": "PRJ-2023-01124",
            "mp_id": "MP-LOK-HP-04",
            "district_lgd_code": 12,
            "work_description_raw": "Setup of Smart Computer Lab at St Xavier Academy Kangra",
            "canonical_asset_type": "COMPUTER_LAB",
            "target_quantity": 1,
            "sanction_cost": Decimal("850000.00"),
            "recommendation_date": date(2023, 2, 1),
            "sanction_date": date(2023, 5, 18),  # 106 days (Statutory lag >75 days recom-to-sanction sanction delay)
            "completion_date": date(2023, 10, 10),
            "latitude": 32.0999,
            "longitude": 76.2692,
            "resolved_udise_code": "02120109981", # PRIVATE_UNAIDED school - statutory violation!
            "resolution_confidence": Decimal("0.970"),
            "resolution_status": "AUTO_ACCEPTED"
        },
        # 3. PRJ-2023-08912: GPS Dharamshala Girls Sanitation Facility (Low enrollment anomaly)
        {
            "project_id": "PRJ-2023-08912",
            "mp_id": "MP-LOK-HP-04",
            "district_lgd_code": 12,
            "work_description_raw": "Construction of Girls Sanitation Facility at GPS Dharamshala",
            "canonical_asset_type": "SANITATION",
            "target_quantity": 1,
            "sanction_cost": Decimal("450000.00"),
            "recommendation_date": date(2023, 3, 1),
            "sanction_date": date(2023, 3, 20),
            "completion_date": date(2023, 5, 10),
            "latitude": 32.2185,
            "longitude": 76.3202,
            "resolved_udise_code": "02120200114", # 19 kids - low enrollment context
            "resolution_confidence": Decimal("0.990"),
            "resolution_status": "AUTO_ACCEPTED"
        },
        # 4. PRJ-2023-03319: GSSS Palampur legitimate construction (6 months duration, 2 rooms reflected in census)
        {
            "project_id": "PRJ-2023-03319",
            "mp_id": "MP-LOK-HP-04",
            "district_lgd_code": 12,
            "work_description_raw": "Construction of 2 Additional Classrooms at GSSS Palampur",
            "canonical_asset_type": "CLASSROOM",
            "target_quantity": 2,
            "sanction_cost": Decimal("1400000.00"),
            "recommendation_date": date(2023, 1, 10),
            "sanction_date": date(2023, 2, 15),
            "completion_date": date(2023, 8, 15), # 6 months - realistic velocity!
            "latitude": 32.1183,
            "longitude": 76.5307,
            "resolved_udise_code": "02120300552", # Classrooms count changes 12 -> 14. Perfect reflection!
            "resolution_confidence": Decimal("0.995"),
            "resolution_status": "AUTO_ACCEPTED"
        }
    ]

    for data in canonical_projects:
        project = MPLADSProject(
            project_id=data["project_id"],
            mp_id=data["mp_id"],
            district_lgd_code=data["district_lgd_code"],
            work_description_raw=data["work_description_raw"],
            canonical_asset_type=data["canonical_asset_type"],
            target_quantity=data["target_quantity"],
            sanction_cost=data["sanction_cost"],
            recommendation_date=data["recommendation_date"],
            sanction_date=data["sanction_date"],
            completion_date=data["completion_date"],
            project_location=get_location_geom(db, data["longitude"], data["latitude"]),
            latitude=data["latitude"],
            longitude=data["longitude"],
            resolved_udise_code=data["resolved_udise_code"],
            resolution_confidence=data["resolution_confidence"],
            resolution_status=data["resolution_status"]
        )
        db.add(project)
    db.commit()
    print("Canonical projects loaded successfully.")

def generate_background_projects(db, total_projects=250):
    print(f"Generating remaining {total_projects - 4} background projects...")
    random.seed(42)
    
    # Query loaded schools to use as resolution targets
    schools = db.query(School).all()
    if not schools:
        print("ERROR: No schools found in the database. Please run load_udise_data.py first.")
        sys.exit(1)
        
    mp_ids = ["MP-LOK-HP-01", "MP-LOK-HP-02", "MP-LOK-HP-03", "MP-LOK-HP-04", "MP-RAJ-HP-01"]
    
    work_templates = [
        ("Construction of {qty} additional classroom(s) at {school_name}", "CLASSROOM", 1000000.00, 1600000.00),
        ("Sanitation Block installation for boys/girls at {school_name}", "SANITATION", 300000.00, 600000.00),
        ("Drinking water filter plant and pipelines at {school_name}", "DRINKING_WATER", 150000.00, 400000.00),
        ("Setup of computer laboratory and tables at {school_name}", "COMPUTER_LAB", 500000.00, 900000.00),
        ("Supply of student desks and benches for classes at {school_name}", "DESKS", 200000.00, 500000.00),
        ("Renovation and painting of school buildings at {school_name}", "RENOVATION", 100000.00, 300000.00)
    ]
    
    loaded_canonical_ids = set(["PRJ-2023-04567", "PRJ-2023-01124", "PRJ-2023-08912", "PRJ-2023-03319"])
    
    count = len(loaded_canonical_ids)
    while count < total_projects:
        proj_id_num = random.randint(10000, 99999)
        project_id = f"PRJ-2023-{proj_id_num:05d}"
        if project_id in loaded_canonical_ids:
            continue
            
        loaded_canonical_ids.add(project_id)
        
        # Pick a target school
        target_school = random.choice(schools)
        
        # Select work template
        template, asset_type, min_cost, max_cost = random.choice(work_templates)
        qty = random.randint(1, 2)
        work_desc = template.format(qty=qty, school_name=target_school.name_canonical)
        cost = round(random.uniform(min_cost, max_cost), 2)
        
        # Set dates
        recom_date = date(2023, 1, 1) + timedelta(days=random.randint(0, 150))
        sanc_delay = random.randint(10, 60)
        sanc_date = recom_date + timedelta(days=sanc_delay)
        
        comp_delay = random.randint(30, 180)
        # 10% projects are still active / not completed
        comp_date = sanc_date + timedelta(days=comp_delay) if random.random() > 0.1 else None
        
        # Geolocation: 90% are near school campus (<= 100m offset)
        # 10% are highly displaced (> 1.5km offset) to trigger coordinate mismatch warnings
        is_displaced = random.random() < 0.1
        if is_displaced:
            lat_offset = random.choice([-1.0, 1.0]) * random.uniform(0.015, 0.030) # ~1.5km - 3km
            lon_offset = random.choice([-1.0, 1.0]) * random.uniform(0.015, 0.030)
        else:
            lat_offset = random.uniform(-0.0005, 0.0005) # <= 50m
            lon_offset = random.uniform(-0.0005, 0.0005)
            
        proj_lat = round(target_school.latitude + lat_offset, 5)
        proj_lon = round(target_school.longitude + lon_offset, 5)
        
        # Resolution metrics
        confidence = round(random.uniform(0.50, 0.99), 3)
        if confidence >= 0.85:
            res_status = "AUTO_ACCEPTED"
        elif confidence >= 0.60:
            res_status = "AMBIGUOUS"
        else:
            res_status = "UNRESOLVED"
            
        project = MPLADSProject(
            project_id=project_id,
            mp_id=random.choice(mp_ids),
            district_lgd_code=12,
            work_description_raw=work_desc,
            canonical_asset_type=asset_type,
            target_quantity=qty,
            sanction_cost=Decimal(str(cost)),
            recommendation_date=recom_date,
            sanction_date=sanc_date,
            completion_date=comp_date,
            project_location=get_location_geom(db, proj_lon, proj_lat),
            latitude=proj_lat,
            longitude=proj_lon,
            resolved_udise_code=target_school.udise_code if res_status != "UNRESOLVED" else None,
            resolution_confidence=Decimal(str(confidence)),
            resolution_status=res_status
        )
        db.add(project)
        count += 1
        
    db.commit()
    print(f"Loaded {total_projects} projects successfully.")

from backend.app.normalization.taxonomy import CanonicalAssetType
from backend.app.detection.lane1_statutory import evaluate_lane1_statutory
from backend.app.detection.lane2_need import evaluate_lane2_need
from backend.app.detection.lane3_reflection import evaluate_lane3_reflection
from backend.app.detection.lane4_physics import evaluate_lane4_physics
from backend.app.detection.exceptions import apply_exception_context
from backend.app.fusion.scoring import compute_investigation_priority_index
from backend.app.explainability.graph_builder import build_case_evidence_graph
from backend.app.db.models import InvestigationCase, SchoolAnnualState
from backend.app.db.session import get_db_context

def synthesize_investigation_cases(db):
    db.query(InvestigationCase).delete()
    projects = db.query(MPLADSProject).filter(MPLADSProject.resolved_udise_code.isnot(None)).all()
    for p in projects:
        s = p.resolved_school
        if not s:
            continue
        states = db.query(SchoolAnnualState).filter(SchoolAnnualState.udise_code == s.udise_code).order_by(SchoolAnnualState.data_freeze_date.asc()).all()
        pre_state = states[0] if states else None
        post_state = states[-1] if len(states) >= 2 else None
        
        pre_dict = {"academic_year": pre_state.academic_year, "total_enrollment": pre_state.total_enrollment, "total_classrooms": pre_state.total_classrooms, "data_freeze_date": pre_state.data_freeze_date} if pre_state else None
        post_dict = {"academic_year": post_state.academic_year, "total_enrollment": post_state.total_enrollment, "total_classrooms": post_state.total_classrooms, "data_freeze_date": post_state.data_freeze_date} if post_state else None
        state_dicts = [pre_dict, post_dict] if pre_dict and post_dict else ([pre_dict] if pre_dict else [])

        asset_enum = CanonicalAssetType.ADDITIONAL_CLASSROOM if p.canonical_asset_type in ("CLASSROOM", "ADDITIONAL_CLASSROOM") else (
            CanonicalAssetType.TOILET_BLOCK if p.canonical_asset_type in ("SANITATION", "TOILET_BLOCK") else (
                CanonicalAssetType.COMPUTER_LAB if p.canonical_asset_type in ("COMPUTER_LAB", "COMPUTERS") else CanonicalAssetType.GENERIC_CIVIL_REPAIR
            )
        )

        l1 = evaluate_lane1_statutory(s.management_category, p.recommendation_date, p.sanction_date, float(p.sanction_cost))
        l2 = evaluate_lane2_need(state_dicts, p.target_quantity or 1)
        l3 = evaluate_lane3_reflection(asset_enum, p.target_quantity or 1, p.completion_date, pre_dict, post_dict)
        l4 = evaluate_lane4_physics(asset_enum, p.sanction_date, p.completion_date)

        lane_scores = {"STATUTORY": l1, "INSTITUTIONAL_NEED": l2, "ASSET_REFLECTION": l3, "TIMELINE_PHYSICS": l4}
        exc = apply_exception_context(lane_scores, {"operational_status": s.operational_status}, state_dicts)
        fusion = compute_investigation_priority_index(lane_scores, exc, mean_confidence=float(p.resolution_confidence or 0.85))

        proj_dict = {"project_id": p.project_id, "sanction_cost": float(p.sanction_cost), "canonical_asset_type": asset_enum.value, "sanction_date": p.sanction_date, "completion_date": p.completion_date}
        school_dict = {"udise_code": s.udise_code, "name_canonical": s.name_canonical, "management_category": s.management_category, "operational_status": s.operational_status}
        graph = build_case_evidence_graph(proj_dict, school_dict, lane_scores, pre_dict, post_dict, confidence=float(p.resolution_confidence or 0.85))

        case = InvestigationCase(
            project_id=p.project_id,
            ipi_score=Decimal(str(fusion["ipi_score"])),
            ipi_lower=Decimal(str(fusion["ipi_lower"])),
            ipi_upper=Decimal(str(fusion["ipi_upper"])),
            risk_tier=fusion["risk_tier"],
            primary_category=fusion["primary_category"],
            evidence_graph=graph,
            explanation_narrative=f"Automated bitemporal analysis shows {fusion['primary_category']} with composite IPI score {fusion['ipi_score']}.",
            status="PENDING_REVIEW"
        )
        db.add(case)
    db.commit()

def main():
    with get_db_context() as db:
        clear_existing_projects(db)
        load_canonical_projects(db)
        generate_background_projects(db, 250)
        synthesize_investigation_cases(db)
    print("Synthetic e-SAKSHI project generation & case synthesis completed successfully.")

generate_projects = main

if __name__ == "__main__":
    main()
