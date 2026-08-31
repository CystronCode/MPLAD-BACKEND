-- PostgreSQL 16 + PostGIS Master DDL for MEEV (MPLADS Education Ecosystem Validator)
-- Frozen Contract: db_schema.sql

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- 1. Master School Directory (UDISE+ Source)
CREATE TABLE IF NOT EXISTS schools (
    udise_code CHAR(11) PRIMARY KEY,
    name_canonical TEXT NOT NULL,
    state_lgd_code INT NOT NULL,
    district_lgd_code INT NOT NULL,
    block_lgd_code INT NOT NULL,
    village_name TEXT,
    location GEOMETRY(Point, 4326),
    management_category TEXT NOT NULL, -- 'GOVERNMENT', 'GOVT_AIDED', 'PRIVATE_UNAIDED'
    operational_status TEXT DEFAULT 'OPERATIONAL', -- 'OPERATIONAL', 'MERGED', 'CLOSED'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Longitudinal Annual School States
CREATE TABLE IF NOT EXISTS school_annual_states (
    state_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    udise_code CHAR(11) REFERENCES schools(udise_code) ON DELETE CASCADE,
    academic_year CHAR(7) NOT NULL, -- e.g., '2022-23'
    total_enrollment INT NOT NULL,
    girls_enrollment INT DEFAULT 0,
    boys_enrollment INT DEFAULT 0,
    total_classrooms INT NOT NULL,
    good_condition_classrooms INT DEFAULT 0,
    classrooms_dilapidated INT DEFAULT 0,
    has_electricity BOOLEAN NOT NULL DEFAULT TRUE,
    has_drinking_water BOOLEAN NOT NULL DEFAULT TRUE,
    functional_girls_toilets INT DEFAULT 0,
    functional_boys_toilets INT DEFAULT 0,
    has_computer_lab BOOLEAN DEFAULT FALSE,
    total_computers INT DEFAULT 0,
    data_freeze_date DATE NOT NULL,
    data_published_date DATE,
    source_sha256 CHAR(64) NOT NULL,
    UNIQUE(udise_code, academic_year)
);

-- 3. MPLADS Project Records (e-SAKSHI Source)
CREATE TABLE IF NOT EXISTS mplads_projects (
    project_id TEXT PRIMARY KEY,
    mp_id TEXT NOT NULL,
    district_lgd_code INT NOT NULL,
    work_description_raw TEXT NOT NULL,
    canonical_asset_type TEXT NOT NULL,
    target_quantity INT DEFAULT 1,
    sanction_cost NUMERIC(14,2) NOT NULL,
    recommendation_date DATE,
    sanction_date DATE,
    completion_date DATE,
    project_location GEOMETRY(Point, 4326),
    resolved_udise_code CHAR(11) REFERENCES schools(udise_code),
    resolution_confidence NUMERIC(4,3),
    resolution_status TEXT DEFAULT 'UNRESOLVED', -- 'AUTO_ACCEPTED', 'AMBIGUOUS', 'UNRESOLVED', 'MANUAL_VERIFIED'
    ingested_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Investigation Cases & Evidence Bundles
CREATE TABLE IF NOT EXISTS investigation_cases (
    case_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id TEXT REFERENCES mplads_projects(project_id) ON DELETE CASCADE,
    ipi_score NUMERIC(4,1) NOT NULL,
    ipi_lower NUMERIC(4,1) NOT NULL,
    ipi_upper NUMERIC(4,1) NOT NULL,
    risk_tier SMALLINT NOT NULL, -- 1, 2, 3
    primary_category TEXT NOT NULL,
    evidence_graph JSONB NOT NULL,
    explanation_narrative TEXT NOT NULL,
    status TEXT DEFAULT 'PENDING_REVIEW', -- 'PENDING_REVIEW', 'ESCALATED', 'DISMISSED', 'VERIFIED'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Immutable Append-Only Audit Log with Hash Chaining
CREATE TABLE IF NOT EXISTS audit_log (
    log_id BIGSERIAL PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    action_performed TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    payload JSONB NOT NULL,
    previous_hash CHAR(64) NOT NULL,
    current_hash CHAR(64) NOT NULL,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Bronze Ingestion Records for Auditable Provenance
CREATE TABLE IF NOT EXISTS bronze_udise (
    id BIGSERIAL PRIMARY KEY,
    source_batch_id TEXT NOT NULL,
    udise_code CHAR(11) NOT NULL,
    academic_year CHAR(7) NOT NULL,
    payload JSONB NOT NULL,
    payload_sha256 CHAR(64) NOT NULL,
    ingested_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bronze_esakshi (
    id BIGSERIAL PRIMARY KEY,
    source_batch_id TEXT NOT NULL,
    work_id TEXT NOT NULL,
    payload JSONB NOT NULL,
    payload_sha256 CHAR(64) NOT NULL,
    ingested_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_schools_spatial ON schools USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_projects_spatial ON mplads_projects USING GIST(project_location);
CREATE INDEX IF NOT EXISTS idx_school_states_lookup ON school_annual_states(udise_code, academic_year);
CREATE INDEX IF NOT EXISTS idx_cases_tier_score ON investigation_cases(risk_tier, ipi_score DESC);
CREATE INDEX IF NOT EXISTS idx_audit_recorded_at ON audit_log(recorded_at);
