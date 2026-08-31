# backend/app/ingestion/esakshi_loader.py
# Ingestion of e-SAKSHI project records with entity resolution and case synthesis

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.db.models import MPLADSProject, School, SchoolAnnualState, InvestigationCase
from backend.app.normalization.taxonomy import normalize_asset_description
from backend.app.resolution.matcher import resolve_project
from backend.app.detection.lane1_statutory import evaluate_lane1_statutory
from backend.app.detection.lane2_need import evaluate_lane2_need
from backend.app.detection.lane3_reflection import evaluate_lane3_reflection
from backend.app.detection.lane4_physics import evaluate_lane4_physics
from backend.app.detection.exceptions import apply_exception_context
from backend.app.fusion.scoring import compute_investigation_priority_index
from backend.app.explainability.graph_builder import build_case_evidence_graph

def process_and_ingest_esakshi_projects(
    db: Session,
    raw_projects: List[Dict[str, Any]]
) -> Dict[str, int]:
    """
    Full end-to-end processing pipeline for a batch of e-SAKSHI projects:
    1. Asset Normalization via Regex Taxonomy
    2. 7-Stage Entity Resolution against School database
    3. Multi-Lane Anomaly & Physics Evaluation
    4. Orthogonal Max-Pooled Risk Scoring & IPI calculation
    5. In-Memory D3 Provenance Graph generation
    6. Database persistence into `mplads_projects` and `investigation_cases`
    """
    # Fetch all candidate schools in district for resolution
    schools = db.query(School).all()
    candidate_dicts = [
        {
            "udise_code": s.udise_code,
            "name_canonical": s.name_canonical,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "management_category": s.management_category,
            "operational_status": s.operational_status
        }
        for s in schools
    ]

    projects_ingested = 0
    cases_created = 0

    for raw in raw_projects:
        p_id = raw["work_id"]
        desc = raw.get("work_description", "")
        
        # 1. Normalize Asset
        asset_type, target_qty = normalize_asset_description(desc)

        # 2. Entity Resolution
        p_coords = (raw.get("latitude"), raw.get("longitude")) if raw.get("latitude") and raw.get("longitude") else None
        resolution = resolve_project(desc, p_coords, candidate_dicts)

        resolved_udise = resolution.get("udise_code")
        conf = resolution.get("confidence", 0.0)
        status = resolution.get("status", "UNRESOLVED")

        # Create or update project record
        existing_p = db.query(MPLADSProject).filter(MPLADSProject.project_id == p_id).first()
        if not existing_p:
            project_obj = MPLADSProject(
                project_id=p_id,
                mp_id=raw.get("mp_id", "UNKNOWN"),
                district_lgd_code=raw.get("district_lgd_code", 12),
                work_description_raw=desc,
                canonical_asset_type=asset_type.value if hasattr(asset_type, "value") else str(asset_type),
                target_quantity=target_qty,
                sanction_cost=raw.get("sanction_cost", 100000.0),
                recommendation_date=raw.get("recommendation_date"),
                sanction_date=raw.get("sanction_date"),
                completion_date=raw.get("completion_date"),
                latitude=raw.get("latitude"),
                longitude=raw.get("longitude"),
                resolved_udise_code=resolved_udise,
                resolution_confidence=conf,
                resolution_status=status
            )
            db.add(project_obj)
            projects_ingested += 1
        else:
            project_obj = existing_p

        # If matched to a school, evaluate detection lanes and create Investigation Case
        if resolved_udise:
            matched_school = db.query(School).filter(School.udise_code == resolved_udise).first()
            states = db.query(SchoolAnnualState).filter(SchoolAnnualState.udise_code == resolved_udise).order_by(SchoolAnnualState.academic_year.asc()).all()

            states_dicts = [
                {
                    "academic_year": st.academic_year,
                    "total_enrollment": st.total_enrollment,
                    "total_classrooms": st.total_classrooms,
                    "good_condition_classrooms": st.good_condition_classrooms,
                    "classrooms_dilapidated": st.classrooms_dilapidated,
                    "has_electricity": st.has_electricity,
                    "has_drinking_water": st.has_drinking_water,
                    "functional_girls_toilets": st.functional_girls_toilets,
                    "functional_boys_toilets": st.functional_boys_toilets,
                    "has_computer_lab": st.has_computer_lab,
                    "data_freeze_date": st.data_freeze_date
                }
                for st in states
            ]

            pre_state = states_dicts[0] if states_dicts else None
            post_state = states_dicts[-1] if len(states_dicts) >= 2 else None

            # 3. Anomaly Lanes
            lane1 = evaluate_lane1_statutory(
                school_management=matched_school.management_category if matched_school else "GOVERNMENT",
                recommendation_date=project_obj.recommendation_date,
                sanction_date=project_obj.sanction_date,
                sanction_cost=float(project_obj.sanction_cost)
            )
            lane2 = evaluate_lane2_need(states_dicts, target_qty)
            lane3 = evaluate_lane3_reflection(
                canonical_asset_type=project_obj.canonical_asset_type,
                target_quantity=target_qty,
                completion_date=project_obj.completion_date,
                pre_state=pre_state,
                post_state=post_state
            )
            lane4 = evaluate_lane4_physics(
                canonical_asset_type=project_obj.canonical_asset_type,
                sanction_date=project_obj.sanction_date,
                completion_date=project_obj.completion_date
            )

            lane_scores = {
                "STATUTORY": lane1,
                "INSTITUTIONAL_NEED": lane2,
                "ASSET_REFLECTION": lane3,
                "TIMELINE_PHYSICS": lane4
            }

            # 4. Exception Adjustments
            school_dict = {
                "udise_code": matched_school.udise_code,
                "name_canonical": matched_school.name_canonical,
                "management_category": matched_school.management_category,
                "operational_status": matched_school.operational_status,
                "latitude": matched_school.latitude,
                "longitude": matched_school.longitude
            } if matched_school else {}

            exceptions = apply_exception_context(lane_scores, school_dict, states_dicts)

            # 5. Fusion Math & IPI
            fusion = compute_investigation_priority_index(lane_scores, exceptions, mean_confidence=conf)

            # 6. Provenance Graph
            proj_dict = {
                "project_id": project_obj.project_id,
                "sanction_cost": float(project_obj.sanction_cost),
                "target_quantity": project_obj.target_quantity,
                "canonical_asset_type": project_obj.canonical_asset_type,
                "sanction_date": project_obj.sanction_date,
                "completion_date": project_obj.completion_date
            }
            graph = build_case_evidence_graph(
                project=proj_dict,
                school=school_dict,
                lane_scores=lane_scores,
                pre_state=pre_state,
                post_state=post_state,
                confidence=conf
            )

            narrative = (
                f"Project {project_obj.project_id} claimed completion of {target_qty} {project_obj.canonical_asset_type} "
                f"at {matched_school.name_canonical}. Lane scores: Statutory={lane1['score']}, Need={lane2['score']}, "
                f"Reflection={lane3['score']}, Velocity={lane4['score']}. IPI calculated at {fusion['ipi_score']}."
            )

            # Save investigation case
            existing_case = db.query(InvestigationCase).filter(InvestigationCase.project_id == p_id).first()
            if not existing_case:
                inv_case = InvestigationCase(
                    project_id=p_id,
                    ipi_score=fusion["ipi_score"],
                    ipi_lower=fusion["ipi_lower"],
                    ipi_upper=fusion["ipi_upper"],
                    risk_tier=fusion["risk_tier"],
                    primary_category=fusion["primary_category"],
                    evidence_graph=graph,
                    explanation_narrative=narrative,
                    status="PENDING_REVIEW"
                )
                db.add(inv_case)
                cases_created += 1

    db.commit()
    return {"projects_ingested": projects_ingested, "cases_created": cases_created}
