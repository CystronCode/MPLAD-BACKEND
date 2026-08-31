# contracts/models.py
# Frozen Canonical Pydantic Data Models & Enums for MEEV

from enum import Enum
from datetime import date, datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field

class CanonicalAssetType(str, Enum):
    ADDITIONAL_CLASSROOM = "ADDITIONAL_CLASSROOM"
    TOILET_BLOCK = "TOILET_BLOCK"
    DRINKING_WATER = "DRINKING_WATER"
    COMPUTER_LAB = "COMPUTER_LAB"
    SCIENCE_LAB = "SCIENCE_LAB"
    LIBRARY_ROOM = "LIBRARY_ROOM"
    BOUNDARY_WALL = "BOUNDARY_WALL"
    GENERIC_CIVIL_REPAIR = "GENERIC_CIVIL_REPAIR"

class SchoolManagement(str, Enum):
    GOVERNMENT = "GOVERNMENT"
    GOVT_AIDED = "GOVT_AIDED"
    PRIVATE_UNAIDED = "PRIVATE_UNAIDED"

class OperationalStatus(str, Enum):
    OPERATIONAL = "OPERATIONAL"
    MERGED = "MERGED"
    CLOSED = "CLOSED"

class ResolutionStatus(str, Enum):
    AUTO_ACCEPTED = "AUTO_ACCEPTED"
    AMBIGUOUS = "AMBIGUOUS"
    UNRESOLVED = "UNRESOLVED"
    MANUAL_VERIFIED = "MANUAL_VERIFIED"

class RiskTier(int, Enum):
    TIER_1_AUTO_ARCHIVE = 1
    TIER_2_DESK_REVIEW = 2
    TIER_3_FIELD_INSPECTION = 3

class CaseStatus(str, Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    ESCALATED = "ESCALATED"
    DISMISSED = "DISMISSED"
    VERIFIED = "VERIFIED"

class TriageDecision(str, Enum):
    ESCALATE_FIELD_INSPECTION = "ESCALATE_FIELD_INSPECTION"
    DISMISS_BENIGN_CONTEXT = "DISMISS_BENIGN_CONTEXT"
    REQUEST_HEADMASTER_INFO = "REQUEST_HEADMASTER_INFO"

# --- Entities ---

class SchoolMasterSchema(BaseModel):
    udise_code: str = Field(min_length=11, max_length=11)
    name_canonical: str
    state_lgd_code: int
    district_lgd_code: int
    block_lgd_code: int
    village_name: Optional[str] = None
    latitude: float
    longitude: float
    management_category: SchoolManagement
    operational_status: OperationalStatus = OperationalStatus.OPERATIONAL

class SchoolAnnualStateSchema(BaseModel):
    udise_code: str = Field(min_length=11, max_length=11)
    academic_year: str  # e.g., '2022-23'
    total_enrollment: int
    girls_enrollment: int = 0
    boys_enrollment: int = 0
    total_classrooms: int
    good_condition_classrooms: int = 0
    classrooms_dilapidated: int = 0
    has_electricity: bool = True
    has_drinking_water: bool = True
    functional_girls_toilets: int = 0
    functional_boys_toilets: int = 0
    has_computer_lab: bool = False
    total_computers: int = 0
    data_freeze_date: date
    data_published_date: Optional[date] = None
    source_sha256: str

class MPLADSProjectSchema(BaseModel):
    project_id: str
    mp_id: str
    district_lgd_code: int
    work_description_raw: str
    canonical_asset_type: CanonicalAssetType
    target_quantity: int = 1
    sanction_cost: float = Field(gt=0)
    recommendation_date: date
    sanction_date: date
    completion_date: Optional[date] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    resolved_udise_code: Optional[str] = None
    resolution_confidence: Optional[float] = None
    resolution_status: ResolutionStatus = ResolutionStatus.UNRESOLVED

# --- Graph Models ---

class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # PROJECT, SCHOOL, STATE, CONTRADICTION, RULE
    properties: dict[str, Any] = Field(default_factory=dict)

class GraphLink(BaseModel):
    source: str
    target: str
    relation: str
    confidence: Optional[float] = None

class D3GraphPayload(BaseModel):
    directed: bool = True
    multigraph: bool = False
    nodes: List[GraphNode]
    links: List[GraphLink]

# --- Investigation Case Models ---

class InvestigationCaseSummary(BaseModel):
    case_id: str
    project_id: str
    school_name: str
    udise_code: str
    sanction_cost: float
    canonical_asset_type: CanonicalAssetType
    ipi_score: float
    ipi_lower: float
    ipi_upper: float
    risk_tier: RiskTier
    primary_category: str
    status: CaseStatus = CaseStatus.PENDING_REVIEW
    created_at: Optional[datetime] = None

class InvestigationCaseDetail(InvestigationCaseSummary):
    evidence_graph: D3GraphPayload
    explanation_narrative: str
    lane_scores: dict[str, Any]
    exception_adjustments: List[dict[str, Any]] = Field(default_factory=list)
    project_details: MPLADSProjectSchema
    school_details: SchoolMasterSchema
    baseline_state: Optional[SchoolAnnualStateSchema] = None
    post_completion_state: Optional[SchoolAnnualStateSchema] = None

# --- Decision and Audit ---

class CaseDecisionRequest(BaseModel):
    decision: TriageDecision
    notes: Optional[str] = None
    investigator_id: str

class CaseDecisionResponse(BaseModel):
    case_id: str
    status: CaseStatus
    audit_hash: str
    recorded_at: datetime
