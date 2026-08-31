# backend/app/explainability/graph_builder.py
# NetworkX In-Memory Provenance Graph Builder with D3.js Serializer

from typing import Dict, Any, List

def build_case_evidence_graph(
    project: Dict[str, Any],
    school: Dict[str, Any],
    lane_scores: Dict[str, Any],
    pre_state: Dict[str, Any] | None = None,
    post_state: Dict[str, Any] | None = None,
    confidence: float = 0.92
) -> Dict[str, Any]:
    """
    Constructs a directed provenance graph linking project, school, annual states, and contradiction assertions.
    Returns D3-compatible node-link JSON payload.
    """
    nodes: List[Dict[str, Any]] = []
    links: List[Dict[str, Any]] = []

    p_id = f"project:{project.get('project_id', 'UNKNOWN')}"
    s_id = f"school:{school.get('udise_code', 'UNKNOWN')}"

    # 1. Project Root Node
    nodes.append({
        "id": p_id,
        "label": f"MPLADS Project ({project.get('project_id')})",
        "type": "PROJECT",
        "properties": {
            "Cost": f"₹{project.get('sanction_cost', 0):,.2f}",
            "Asset": f"{project.get('target_quantity', 1)} {project.get('canonical_asset_type', '')}",
            "Sanction Date": str(project.get('sanction_date', '')),
            "Completion Date": str(project.get('completion_date', ''))
        }
    })

    # 2. School Node
    nodes.append({
        "id": s_id,
        "label": f"{school.get('name_canonical', 'School')} ({school.get('udise_code')})",
        "type": "SCHOOL",
        "properties": {
            "UDISE Code": school.get("udise_code", ""),
            "Management": school.get("management_category", ""),
            "Status": school.get("operational_status", "")
        }
    })

    links.append({
        "source": p_id,
        "target": s_id,
        "relation": "CLAIMS_TARGET_INSTITUTION",
        "confidence": confidence
    })

    # 3. Pre-Sanction Census Node
    if pre_state:
        pre_id = f"state:{pre_state.get('academic_year', 'PRE')}"
        nodes.append({
            "id": pre_id,
            "label": f"Pre-Sanction Census ({pre_state.get('academic_year')})",
            "type": "STATE",
            "properties": {
                "Classrooms": pre_state.get("total_classrooms", 0),
                "Enrollment": pre_state.get("total_enrollment", 0),
                "Data Freeze Date": str(pre_state.get("data_freeze_date", ""))
            }
        })
        links.append({
            "source": s_id,
            "target": pre_id,
            "relation": "RECORDED_BASELINE"
        })

    # 4. Post-Completion Census Node
    if post_state:
        post_id = f"state:{post_state.get('academic_year', 'POST')}"
        nodes.append({
            "id": post_id,
            "label": f"Post-Comp Census ({post_state.get('academic_year')})",
            "type": "STATE",
            "properties": {
                "Classrooms": post_state.get("total_classrooms", 0),
                "Enrollment": post_state.get("total_enrollment", 0),
                "Data Freeze Date": str(post_state.get("data_freeze_date", ""))
            }
        })
        links.append({
            "source": s_id,
            "target": post_id,
            "relation": "RECORDED_POST_COMP"
        })

    # 5. Contradiction Nodes
    refl = lane_scores.get("ASSET_REFLECTION", {})
    if refl.get("score", 0.0) >= 0.50:
        c_refl_id = "contradiction:reflection_gap"
        nodes.append({
            "id": c_refl_id,
            "label": "Physical Asset Non-Reflection",
            "type": "CONTRADICTION",
            "properties": {
                "Observed Delta": f"{refl.get('observed_delta', 0)} units",
                "Expected Delta": f"+{refl.get('expected_delta', 1)} units",
                "Source": "Ministry of Education UDISE+ Return"
            }
        })
        links.append({
            "source": p_id,
            "target": c_refl_id,
            "relation": "CONTRADICTED_BY"
        })
        if post_state:
            links.append({
                "source": post_id,
                "target": c_refl_id,
                "relation": "EVIDENCE_ANCHOR"
            })

    phys = lane_scores.get("TIMELINE_PHYSICS", {})
    if phys.get("score", 0.0) >= 0.70:
        c_phys_id = "contradiction:velocity"
        nodes.append({
            "id": c_phys_id,
            "label": "Physical Velocity Violation",
            "type": "CONTRADICTION",
            "properties": {
                "Claimed Duration": f"{phys.get('duration_days')} Days",
                "IS 456 Standard": "Min 45 Days Structural RCC Concrete Curing"
            }
        })
        links.append({
            "source": p_id,
            "target": c_phys_id,
            "relation": "VIOLATES_PHYSICS"
        })

    stat = lane_scores.get("STATUTORY", {})
    if stat.get("score", 0.0) >= 0.80:
        c_stat_id = "rule:ch6"
        nodes.append({
            "id": c_stat_id,
            "label": "Statutory Ineligibility",
            "type": "RULE",
            "properties": {
                "Violation": "; ".join(stat.get("violations", []))
            }
        })
        links.append({
            "source": s_id,
            "target": c_stat_id,
            "relation": "VIOLATES_STATUTORY_RULE"
        })

    return {
        "directed": True,
        "multigraph": False,
        "nodes": nodes,
        "links": links
    }
