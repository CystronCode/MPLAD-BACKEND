import uuid
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    Date,
    Numeric,
    Boolean,
    BigInteger,
    JSON,
    Uuid,
    UniqueConstraint,
    func
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import UserDefinedType
from sqlalchemy.ext.compiler import compiles

from backend.app.db.session import Base

# Dialect-agnostic spatial type representing POINT geometries
class GeometryColumn(UserDefinedType):
    def __init__(self, srid=4326):
        self.srid = srid

    def get_col_spec(self, **kw):
        return f"GEOMETRY(Point, {self.srid})"

@compiles(GeometryColumn, 'postgresql')
def compile_geometry_postgresql(type_, compiler, **kw):
    return f"GEOMETRY(Point, {type_.srid})"

@compiles(GeometryColumn, 'sqlite')
def compile_geometry_sqlite(type_, compiler, **kw):
    return "TEXT"

@compiles(GeometryColumn)
def compile_geometry_default(type_, compiler, **kw):
    return f"GEOMETRY(Point, {type_.srid})"


class School(Base):
    __tablename__ = "schools"

    udise_code = Column(String(11), primary_key=True)
    name_canonical = Column(String, nullable=False)
    state_lgd_code = Column(Integer, nullable=False)
    district_lgd_code = Column(Integer, nullable=False)
    block_lgd_code = Column(Integer, nullable=False)
    village_name = Column(String, nullable=True)
    location = Column(GeometryColumn(srid=4326), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    management_category = Column(String, nullable=False)  # 'GOVERNMENT', 'GOVT_AIDED', 'PRIVATE_UNAIDED'
    operational_status = Column(String, default="OPERATIONAL")  # 'OPERATIONAL', 'MERGED', 'CLOSED'
    created_at = Column(DateTime(timezone=True), default=func.now())

    # Relationships
    annual_states = relationship(
        "SchoolAnnualState",
        back_populates="school",
        cascade="all, delete-orphan"
    )
    projects = relationship(
        "MPLADSProject",
        back_populates="resolved_school"
    )


class SchoolAnnualState(Base):
    __tablename__ = "school_annual_states"

    state_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    udise_code = Column(String(11), ForeignKey("schools.udise_code", ondelete="CASCADE"), nullable=False)
    academic_year = Column(String(7), nullable=False)  # e.g. '2022-23'
    total_enrollment = Column(Integer, nullable=False)
    girls_enrollment = Column(Integer, default=0)
    boys_enrollment = Column(Integer, default=0)
    total_classrooms = Column(Integer, nullable=False)
    good_condition_classrooms = Column(Integer, default=0)
    classrooms_dilapidated = Column(Integer, default=0)
    has_electricity = Column(Boolean, nullable=False, default=True)
    has_drinking_water = Column(Boolean, nullable=False, default=True)
    functional_girls_toilets = Column(Integer, default=0)
    functional_boys_toilets = Column(Integer, default=0)
    has_computer_lab = Column(Boolean, default=False)
    total_computers = Column(Integer, default=0)
    data_freeze_date = Column(Date, nullable=False)
    data_published_date = Column(Date, nullable=True)
    source_sha256 = Column(String(64), nullable=False)

    __table_args__ = (
        UniqueConstraint("udise_code", "academic_year", name="uq_school_annual_state_year"),
    )

    # Relationships
    school = relationship("School", back_populates="annual_states")


class MPLADSProject(Base):
    __tablename__ = "mplads_projects"

    project_id = Column(String, primary_key=True)
    mp_id = Column(String, nullable=False)
    district_lgd_code = Column(Integer, nullable=False)
    work_description_raw = Column(String, nullable=False)
    canonical_asset_type = Column(String, nullable=False)
    target_quantity = Column(Integer, default=1)
    sanction_cost = Column(Numeric(14, 2), nullable=False)
    recommendation_date = Column(Date, nullable=True)
    sanction_date = Column(Date, nullable=True)
    completion_date = Column(Date, nullable=True)
    project_location = Column(GeometryColumn(srid=4326), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    resolved_udise_code = Column(String(11), ForeignKey("schools.udise_code"), nullable=True)
    resolution_confidence = Column(Numeric(4, 3), nullable=True)
    resolution_status = Column(String, default="UNRESOLVED")  # 'AUTO_ACCEPTED', 'AMBIGUOUS', 'UNRESOLVED', 'MANUAL_VERIFIED'
    ingested_at = Column(DateTime(timezone=True), default=func.now())

    # Relationships
    resolved_school = relationship("School", back_populates="projects")
    investigation_case = relationship(
        "InvestigationCase",
        uselist=False,
        back_populates="project",
        cascade="all, delete-orphan"
    )


class InvestigationCase(Base):
    __tablename__ = "investigation_cases"

    case_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    project_id = Column(String, ForeignKey("mplads_projects.project_id", ondelete="CASCADE"), nullable=False)
    ipi_score = Column(Numeric(4, 1), nullable=False)
    ipi_lower = Column(Numeric(4, 1), nullable=False)
    ipi_upper = Column(Numeric(4, 1), nullable=False)  # Wait: typo in prompt might exist but let's keep name matching the DB schema 'ipi_upper'
    risk_tier = Column(Integer, nullable=False)  # 1, 2, 3
    primary_category = Column(String, nullable=False)
    evidence_graph = Column(JSON, nullable=False)
    explanation_narrative = Column(String, nullable=False)
    status = Column(String, default="PENDING_REVIEW")  # 'PENDING_REVIEW', 'ESCALATED', 'DISMISSED', 'VERIFIED'
    created_at = Column(DateTime(timezone=True), default=func.now())

    # Relationships
    project = relationship("MPLADSProject", back_populates="investigation_case")


class AuditLog(Base):
    __tablename__ = "audit_log"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    action_performed = Column(String, nullable=False)
    actor_id = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    previous_hash = Column(String(64), nullable=False)
    current_hash = Column(String(64), nullable=False)
    recorded_at = Column(DateTime(timezone=True), default=func.now())

# Aliases
LongitudinalState = SchoolAnnualState

