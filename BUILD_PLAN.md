# SIH26102 — MEEV (MPLADS Education Ecosystem Validator)
# Master Parallel Build Plan & Agent Orchestration Specification

> **Document Version:** 1.0.0 — Final Authoritative Build Plan  
> **Problem Statement:** SIH26102 — *Development of an AI-powered system to detect anomalies, fraud, and inefficiencies in MPLAD Scheme implementation.*  
> **Sector:** Education (Primary, Upper Primary, and Secondary Public Infrastructure)  
> **System Name:** **MEEV (MPLADS Education Ecosystem Validator)**  
> **Core Architectural Paradigm:** Inter-System Bitemporal Functional Validation ($e\text{-SAKSHI} \times \text{UDISE+}$ Cross-Silo Data Fusion)  
> **Status:** Single Authoritative Execution Guide for Multi-Agent Parallel Implementation

---

## Table of Contents

1. [Project Objective](#1-project-objective)
2. [Authoritative Documents](#2-authoritative-documents)
3. [Architecture Summary](#3-architecture-summary)
4. [Contract Freeze](#4-contract-freeze)
5. [Dependency Graph](#5-dependency-graph)
6. [Optimal Parallelization Strategy](#6-optimal-parallelization-strategy)
7. [Phase Breakdown](#7-phase-breakdown)
8. [Workstream Ownership](#8-workstream-ownership)
9. [File Ownership](#9-file-ownership)
10. [Interface Contracts](#10-interface-contracts)
11. [Mock Strategy](#11-mock-strategy)
12. [Critical Path](#12-critical-path)
13. [MVP Layers](#13-mvp-layers)
14. [Integration Checkpoints](#14-integration-checkpoints)
15. [Automated Test Gates](#15-automated-test-gates)
16. [Git/Agent Isolation Strategy](#16-gitagent-isolation-strategy)
17. [Merge Order](#17-merge-order)
18. [Agent Task Prompts](#18-agent-task-prompts)
19. [Time Estimates](#19-time-estimates)
20. [Risk Register](#20-risk-register)
21. [AI Failure Safeguards](#21-ai-failure-safeguards)
22. [Demo-First Development Plan](#22-demo-first-development-plan)
23. [Final End-to-End Acceptance Criteria](#23-final-end-to-end-acceptance-criteria)
24. ["STOP BUILDING" Conditions](#24-stop-building-conditions)

---

## 1. Project Objective

The objective of **MEEV (MPLADS Education Ecosystem Validator)** is to construct an offline-capable, high-precision GovTech decision-support system for the Smart India Hackathon 2026. 

Existing government systems (*e-SAKSHI*, *PFMS*, *SNA-SPARSH*) enforce intra-system workflow rules (fund caps, voucher uploads, GPS photo attachments) but cannot verify if the sanctioned physical, functional, or demographic reality ever materialized in the beneficiary school. MEEV bridges **MoSPI's fund sanction tracking** and the **Ministry of Education's annual school census (UDISE+)** to perform **Bitemporal Inter-System Functional Validation**.

### Key Deliverables:
1. **7-Stage Entity Resolution Engine:** Resolves free-text e-SAKSHI project descriptions to 11-digit UDISE+ codes using administrative blocking, phonetic matching, Haversine gating, and Reverse Spatial Fallback.
2. **4-Lane Evidence & Anomaly Engine:** Evaluates Statutory Eligibility (Lane 1), Institutional Need Context (Lane 2), Bitemporal Asset Reflection with Temporal Lag Guardrails (Lane 3), and Physical Construction Velocity (Lane 4).
3. **Orthogonal Fusion & Case Triage:** Synthesizes multi-lane evidence into an Investigation Priority Index ($\text{IPI} \in [0, 100]$) with confidence intervals and routes cases into a 3-tier action hierarchy.
4. **Navigable Provenance Graph:** Constructs an in-memory NetworkX graph serialized to D3.js, providing click-to-evidence provenance with SHA-256 hashes linking back to raw government records.
5. **Statutory Notice Generator:** Pre-fills Form MPLADS-INSP-1 notices under Section 6.4 of the 2023 Guidelines.
6. **Local Docker Environment:** Fully self-contained, offline execution on developer laptops within a 3-container topology (PostgreSQL/PostGIS, FastAPI, React/Tailwind).

---

## 2. Authoritative Documents

The implementation team and all autonomous coding agents must adhere strictly to these authoritative source documents:

1. **`FINAL_ARCHITECTURE.md` (Master Source of Truth):** Defines the canonical bitemporal model, database DDL, API contracts, mathematical scoring formulas, regex taxonomy rules, and D3 node-link schemas.
2. **`RED_TEAM_AUDIT__.md` & `HOSTILE_FEASIBILITY_AUDIT.md` (Corrections & Defensive Rules):**
   - *Rule 1 (Data Accessibility):* Do not implement live scrapers for e-SAKSHI during the hackathon. Use 100% real UDISE+ open data combined with a schema-authentic synthetic e-SAKSHI generator.
   - *Rule 2 (Temporal Guardrail):* Enforce $\text{Date}_{\text{UDISE\_Freeze}} \ge \text{Date}_{\text{Completion}} + 180\text{d}$. Suppress Lane 3 penalty if post-completion census is pending (`PENDING_CENSUS_CYCLE`).
   - *Rule 3 (Entity Resolution):* Include Reverse Spatial Candidate Search ($300\text{m}$ radius) for renamed/merged schools where string similarity $< 0.50$.
   - *Rule 4 (No LLMs / Supervised Fraud ML):* Use the auditable Regex Taxonomy Dictionary and deterministic physics/statistical z-score models. No opaque ML or uncalibrated "94% fraud" claims.
   - *Rule 5 (Max-Pooling Fusion):* Use dimension max-pooling before computing composite IPI to prevent artificial double-counting of correlated demographic signals.
   - *Rule 6 (NetworkX In-Memory):* Discard Neo4j; construct subgraphs in Python memory via NetworkX and export directly to D3.js JSON.

---

## 3. Architecture Summary

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       MEEV SYSTEM ARCHITECTURE                                   │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│  [DATA LAYER]                                                                                    │
│  ├── Real Data: UDISE+ 2021-24 School Master (Sec 1A), Infra (Sec 2), Enrollment (Sec 3) + LGD   │
│  └── Synthetic Generator: Statistically Authentic e-SAKSHI Education Projects (2023 Guidelines) │
│                                                │                                                 │
│                                                ▼                                                 │
│  [INGESTION & BRONZE STORE] (PostgreSQL 16 + PostGIS)                                            │
│  ├── Raw CSV Parsers with SHA-256 Ingestion Hashing -> Bronze Tables (`bronze_udise`, `bronze_es`)│
│  └── Controlled Taxonomy Normalizer (Regex Dictionary) -> Silver Normalized Entities             │
│                                                │                                                 │
│                                                ▼                                                 │
│  [7-STAGE ENTITY RESOLUTION ENGINE]                                                              │
│  ├── LGD District/Block Blocking -> String Clean & Abbrev Expansion -> Jaro-Winkler + Double    │
│  │   Metaphone -> Haversine Spatial Gating -> Reverse Spatial Fallback (300m)                    │
│  └── Confidence Router: >= 0.85 Auto-Accept | 0.60–0.84 Ambiguity Queue | < 0.60 Unresolved     │
│                                                │                                                 │
│                                                ▼                                                 │
│  [CANONICAL BITEMPORAL STORE]                                                                    │
│  ├── `schools` (Master Directory & PostGIS Coordinates)                                          │
│  ├── `school_annual_states` (Multi-Year Panel: Enrollment, Rooms, Dilapidation, Electricity)     │
│  └── `mplads_projects` (Sanction Cost, Target Qty, Dates, Location, Resolution Status)           │
│                                                │                                                 │
│                                                ▼                                                 │
│  [4-LANE DETECTION & REASONING ENGINE]                                                           │
│  ├── Lane 1: Statutory Permissibility & 75-Day Sanction Window                                   │
│  ├── Lane 2: Institutional Need Context (SCR & 3-Year Enrollment Slope)                          │
│  ├── Lane 3: Bitemporal Asset Reflection Diff (with 180-Day DCF Lag Suppression Guardrail)      │
│  ├── Lane 4: Timeline Physics & Velocity (Concrete Curing Bounds: Min 45d / 21d)                 │
│  └── Exception Context: Dilapidated Room Demolition & School Merger Suppressions                 │
│                                                │                                                 │
│                                                ▼                                                 │
│  [ORTHOGONAL FUSION & CASE SYNTHESIS]                                                            │
│  ├── Dimension Max-Pooling: IPI = 30*S_stat + 15*max(S_need) + 35*S_refl + 20*S_phys             │
│  ├── Confidence Margin: ± U = 15 * (1 - mean(C_i)) -> Tiers: Tier 1 (<35), Tier 2, Tier 3 (>=70) │
│  ├── NetworkX Provenance Builder -> Serialized D3.js Node-Link JSON Payload                      │
│  └── Cryptographic Audit Logger (Append-Only Hash Chain: SHA-256)                                │
│                                                │                                                 │
│                                                ▼                                                 │
│  [FASTAPI BACKEND API]                                                                           │
│  └── `/api/v1/cases`, `/api/v1/cases/{id}/evidence-graph`, `/api/v1/cases/{id}/notice/pdf`,     │
│      `/api/v1/cases/{id}/decision`, `/api/v1/ambiguity-queue`, `/api/v1/analytics/district`     │
│                                                │                                                 │
│                                                ▼                                                 │
│  [REACT 18 + TAILWIND CSS FRONTEND]                                                              │
│  ├── District Executive Overview & Map Heatmap                                                   │
│  ├── 3-Tier Case Triage Queue & Desk Review Cards                                                │
│  ├── Split-Pane Case Detail: Fact Narrative + Interactive D3.js Force-Directed Graph             │
│  └── Human Ambiguity Resolution Interface (Side-by-Side Candidate Disambiguation)               │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Contract Freeze

Before launching parallel implementation, the following 8 fundamental contracts **must be frozen**. No agent may alter these contracts without unanimous synchronization.

### Frozen Contracts Register

| Contract | Owner | Why It Must Be Frozen | Consumers |
| :--- | :--- | :--- | :--- |
| **1. Database DDL & Schema** (`contracts/db_schema.sql`) | Tech Lead / DB Architect | Prevents migration collisions and ensures ORM entities align across data pipelines and APIs. | Data Ingestion, Backend ORM, Test Suites |
| **2. Core Data Models & Enums** (`contracts/models.py`, `contracts/types.ts`) | Data / Backend Lead | Defines canonical enums (`CanonicalAssetType`, `RiskTier`, `CaseStatus`, `ResolutionStatus`, `SchoolMgmt`). | Ingestion, Normalization, Detection, API, Frontend |
| **3. REST API OpenAPI Specification** (`contracts/openapi.yaml`) | Backend Lead | Allows frontend developers to build and test UI using typed mock servers before API endpoints exist. | Backend API, Frontend React, Integration Tests |
| **4. Raw Bronze Schemas** (`contracts/bronze_schemas.json`) | Data Engineer | Freezes input expectations for UDISE+ CSVs and synthetic e-SAKSHI generators. | Data Ingestion, Synthetic Generator, Bronze Models |
| **5. Detection Output & Metric Schema** (`contracts/detection_contract.json`) | ML / Detection Lead | Defines the exact structure returned by the 4 detection lanes, exception adjustments, and IPI scoring. | Detection Lanes, Fusion Engine, Provenance Graph |
| **6. D3 Evidence Subgraph JSON Contract** (`contracts/graph_schema.json`) | Graph & Frontend Lead | Freezes the node-link JSON payload structure consumed by D3.js force-directed canvas. | NetworkX Serializer, React Evidence Graph Component |
| **7. Statutory Notice Contract** (`contracts/notice_schema.json`) | GovTech / Legal Lead | Standardizes Form MPLADS-INSP-1 metadata, field directives, and cryptographic sign-off blocks. | Backend Notice Generator, Frontend Case View |
| **8. Audit Hash Chain Specification** (`contracts/audit_contract.json`) | Security Lead | Dictates SHA-256 byte concatenation order for tamper-proof provenance logging. | Ingestion, Case Triage, Decision API |

---

## 5. Dependency Graph

### Visual Dependency DAG

```
                      [PHASE 0: Contract Freeze & Repository Scaffolding]
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
         [TRACK A: Data Pipeline]                        [TRACK B: Core Algorithms]
         • DB DDL & Migrations                           • Regex Asset Taxonomy
         • UDISE+ Real Data Clean                        • 7-Stage Entity Resolution
         • Synthetic e-SAKSHI Gen                        • Reverse Spatial Fallback
                      │                                               │
                      └───────────────────────┬───────────────────────┘
                                              ▼
                             [TRACK C: Detection & Reasoning]
                             • Lane 1: Statutory Rules
                             • Lane 2: Institutional Need
                             • Lane 3: Asset Diff + Lag Guard
                             • Lane 4: Timeline Physics
                             • Exception Context Engine
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
       [TRACK D: Fusion & Graph]                        [TRACK E: Frontend UI (Mocked)]
       • Orthogonal Fusion & IPI                        • React Shell & Tailwind Setup
       • NetworkX Provenance Serializer                 • 3-Tier Case Queue UI
       • Hash-Chained Audit Engine                      • D3.js Force-Directed Graph
       • PDF Notice Generator                           • Ambiguity Queue Interface
                      │                                               │
                      └───────────────────────┬───────────────────────┘
                                              ▼
                             [TRACK F: FastAPI Integration]
                             • Connect Endpoints to DB
                             • Wire Graph & PDF Endpoints
                             • Human Decision Endpoints
                                              │
                                              ▼
                             [PHASE 4: Full System Verification]
                             • End-to-End Integration Tests
                             • Docker Compose Multi-Container Build
                             • 15 Adversarial Test Fixtures
                             • 4-Minute Demo Script Rehearsal
```

### Dependency Classification (Blocking vs. Soft)

- **`Phase 0` $\rightarrow$ `Tracks A, B, E`:** **BLOCKING**. Contracts and directory structure must exist before coding starts.
- **`Track A` (Data) $\rightarrow$ `Track C` (Detection):** **SOFT**. Detection algorithms can be developed and unit-tested against in-memory Python fixture models (`contracts/models.py`) before database ingestion runs.
- **`Track B` (Resolution) $\rightarrow$ `Track C` (Detection):** **SOFT**. Detection takes canonical school states and project objects; it does not depend on matcher internals.
- **`Track C` (Detection) $\rightarrow$ `Track D` (Fusion/Graph):** **BLOCKING**. Fusion and Graph require lane output dictionaries.
- **`Track D` + `Track E` $\rightarrow$ `Track F` (FastAPI Wiring):** **BLOCKING**. Real backend endpoints bind business logic to the API contracts.
- **`Track F` $\rightarrow$ `Phase 4` (System Verification):** **BLOCKING**. Full integration requires Docker and all services active.

---

## 6. Optimal Parallelization Strategy

### Empirical Assessment: Why 4 Parallel Tracks is Optimal

We have evaluated parallel track counts between 2 and 10:
- **2 Tracks (Sequential):** Too slow for a 36-hour hackathon timeframe.
- **6–10 Tracks:** Creates excessive merge conflicts, interface drift, and coordination overhead for AI agents.
- **Optimal: 4 Parallel Tracks in Phase 1 $\rightarrow$ 2 Tracks in Phase 2 $\rightarrow$ 1 Unified Integration in Phase 3.**

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 PARALLEL TRACK EXECUTION                                │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  PHASE 0: Freeze Shared Contracts & Scaffold Repository (Single Lead Agent)            │
│                                                                                         │
│  PHASE 1: 4 Independent Workstreams (Zero Shared Files)                                │
│  ├── Track A (Data Ingestion & Postgres DB)       [Agent: Data-Engineer]                │
│  ├── Track B (Entity Resolution & Taxonomy)       [Agent: Algorithm-Engineer]           │
│  ├── Track C (4-Lane Detection & Lag Guardrail)   [Agent: Detection-Engineer]           │
│  └── Track D (Frontend UI with Typed Mocks)       [Agent: Frontend-Engineer]            │
│                                                                                         │
│  PHASE 2: 2 Integrated Workstreams                                                      │
│  ├── Track E (Backend API, Graph & PDF Notice)    [Agent: Backend-Engineer]             │
│  └── Track F (Frontend Real API & D3 Binding)     [Agent: UI-Integration-Engineer]      │
│                                                                                         │
│  PHASE 3: End-to-End Integration & Docker Verification [Agent: QA-DevOps-Lead]          │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Phase Breakdown

### Phase 0: System Foundation & Contract Freezing
- **Goal:** Establish directory layout, generate DDL, TypeScript definitions, Pydantic schemas, and mock fixtures.
- **Responsible Agent:** `Lead-Architect`
- **Inputs:** `FINAL_ARCHITECTURE.md`, `RED_TEAM_AUDIT__.md`
- **Outputs:** Frozen schema files in `contracts/`, base repo scaffolding.
- **Files Owned:** `contracts/**`, `docker-compose.yml`, `README.md`
- **Forbidden Modifications:** None (initialization).
- **Tests Required:** Schema validation checks, Pydantic model serialization tests.
- **Definition of Done:** `pytest tests/contracts` passes; all schema files are committed and read-only.
- **Can run in parallel with:** Nothing (Foundational).
- **Must wait for:** Nothing.

---

### Phase 1A: Database & Data Ingestion (Track A)
- **Goal:** Deploy PostgreSQL/PostGIS container, apply DDL migrations, clean real UDISE+ CSVs for target district (e.g., Kangra / 2,000 schools), and generate synthetic e-SAKSHI records.
- **Responsible Agent:** `Data-Engineer`
- **Inputs:** `contracts/db_schema.sql`, `contracts/bronze_schemas.json`, raw UDISE+ open data CSVs.
- **Outputs:** Hydrated PostgreSQL database, bronze ingestion pipelines with SHA-256 hashing.
- **Files Owned:** `backend/app/db/**`, `backend/app/ingestion/**`, `backend/scripts/generate_synthetic_esakshi.py`, `backend/scripts/load_udise_data.py`
- **Files Allowed to Modify:** Owned files only.
- **Files Forbidden to Modify:** `backend/app/resolution/**`, `backend/app/detection/**`, `frontend/**`, `contracts/**`
- **Interfaces Consumed:** `contracts/bronze_schemas.json`
- **Interfaces Produced:** Live PostgreSQL tables populated with ~2,000 schools and 250 projects.
- **Tests Required:** `tests/test_ingestion.py` (verifies row count, foreign keys, SHA-256 generation).
- **Definition of Done:** Database loads completely with 0 errors; all tables have valid spatial coordinates.
- **Can run in parallel with:** Phase 1B, Phase 1C, Phase 1D.
- **Must wait for:** Phase 0.

---

### Phase 1B: Entity Resolution & Taxonomy (Track B)
- **Goal:** Implement the controlled regex taxonomy normalizer and the 7-stage entity resolution pipeline with Reverse Spatial Fallback.
- **Responsible Agent:** `Algorithm-Engineer`
- **Inputs:** `contracts/models.py`, `contracts/types.ts`
- **Outputs:** Pure-Python resolution modules with sub-millisecond execution and spatial fallback.
- **Files Owned:** `backend/app/normalization/**`, `backend/app/resolution/**`, `tests/test_resolution.py`
- **Files Allowed to Modify:** Owned files only.
- **Files Forbidden to Modify:** `backend/app/db/**`, `backend/app/detection/**`, `frontend/**`, `contracts/**`
- **Interfaces Consumed:** `contracts/models.py`
- **Interfaces Produced:** `resolve_project_to_school(project_text, project_coords, candidates) -> (udise_code, confidence, status)`
- **Tests Required:** `tests/test_resolution.py` (passes 10 adversarial edge cases from Red-Team audit).
- **Definition of Done:** String match achieves $>85\%$ precision on sample; renamed schools resolved via reverse spatial search.
- **Can run in parallel with:** Phase 1A, Phase 1C, Phase 1D.
- **Must wait for:** Phase 0.

---

### Phase 1C: Multi-Lane Detection & Temporal Guardrail (Track C)
- **Goal:** Implement the 4 detection lanes (Statutory, Need, Asset Reflection, Timeline Physics), the 180-day census lag guardrail, and exception adjustments.
- **Responsible Agent:** `Detection-Engineer`
- **Inputs:** `contracts/models.py`, `contracts/detection_contract.json`
- **Outputs:** Stateless detection and reasoning modules.
- **Files Owned:** `backend/app/detection/**`, `tests/test_detection.py`
- **Files Allowed to Modify:** Owned files only.
- **Files Forbidden to Modify:** `backend/app/db/**`, `backend/app/resolution/**`, `frontend/**`, `contracts/**`
- **Interfaces Consumed:** `contracts/models.py`
- **Interfaces Produced:** `evaluate_project_anomalies(project, pre_state, post_state, school) -> DetectionCaseResult`
- **Tests Required:** `tests/test_detection.py` (verifies lag suppression, concrete curing bounds, statutory private-school flag).
- **Definition of Done:** Zero false-positive reflection flags on lagging census; all 4 lanes return calibrated scores $\in [0, 1]$.
- **Can run in parallel with:** Phase 1A, Phase 1B, Phase 1D.
- **Must wait for:** Phase 0.

---

### Phase 1D: Frontend UI with Mock Contracts (Track D)
- **Goal:** Build the React 18 + Tailwind CSS frontend shell, including 3-tier queue view, case detail layout, D3.js force-directed canvas, and ambiguity queue using frozen mock payloads.
- **Responsible Agent:** `Frontend-Engineer`
- **Inputs:** `contracts/openapi.yaml`, `contracts/graph_schema.json`, `contracts/mock_data.json`
- **Outputs:** Fully functional, interactive SPA rendered with realistic mock cases.
- **Files Owned:** `frontend/**`
- **Files Allowed to Modify:** Owned files only.
- **Files Forbidden to Modify:** `backend/**`, `contracts/**`
- **Interfaces Consumed:** `contracts/mock_data.json`, `contracts/openapi.yaml`
- **Interfaces Produced:** Complete React UI components with mock API adapters.
- **Tests Required:** `npm test` (Jest / React Testing Library component tests).
- **Definition of Done:** D3.js graph renders with zoom/pan and node click inspection; tier filtering works smoothly.
- **Can run in parallel with:** Phase 1A, Phase 1B, Phase 1C.
- **Must wait for:** Phase 0.

---

### Phase 2A: Fusion Math, Provenance Graph & Backend API (Track E)
- **Goal:** Implement orthogonal max-pooling fusion, NetworkX D3 graph serializer, PDF notice generator (ReportLab), cryptographic audit logger, and FastAPI REST routes.
- **Responsible Agent:** `Backend-Engineer`
- **Inputs:** Live outputs from Phase 1A, 1B, 1C and `contracts/openapi.yaml`.
- **Outputs:** Complete FastAPI backend service serving live data.
- **Files Owned:** `backend/app/fusion/**`, `backend/app/explainability/**`, `backend/app/notices/**`, `backend/app/audit/**`, `backend/app/api/**`, `backend/app/main.py`
- **Files Allowed to Modify:** Owned files only.
- **Files Forbidden to Modify:** `frontend/**`, `contracts/**`
- **Interfaces Consumed:** Ingestion, Resolution, Detection, Database ORM.
- **Interfaces Produced:** Live REST API on `http://localhost:8000/api/v1`.
- **Tests Required:** `tests/test_api.py` (FastAPI TestClient integration tests).
- **Definition of Done:** All OpenAPI routes return 200 OK with live database entities and valid D3 JSON graphs.
- **Can run in parallel with:** Phase 2B.
- **Must wait for:** Phase 1A, Phase 1B, Phase 1C.

---

### Phase 2B: Frontend API Integration & Real D3 Binding (Track F)
- **Goal:** Switch frontend API clients from mock data to live FastAPI backend; wire interactive case decision actions and notice downloads.
- **Responsible Agent:** `UI-Integration-Engineer`
- **Inputs:** Live FastAPI API (`http://localhost:8000`), `contracts/openapi.yaml`.
- **Outputs:** End-to-end connected React web application.
- **Files Owned:** `frontend/src/api/**`, `frontend/src/pages/**`, `frontend/src/components/**`
- **Files Allowed to Modify:** Owned files only.
- **Files Forbidden to Modify:** `backend/**`, `contracts/**`
- **Interfaces Consumed:** Live FastAPI endpoints.
- **Interfaces Produced:** Fully interactive production UI.
- **Tests Required:** Frontend E2E browser tests (Cypress/Playwright or manual integration checklist).
- **Definition of Done:** Selecting a case in the queue fetches live evidence graph and downloads pre-filled PDF notice.
- **Can run in parallel with:** Phase 2A (as endpoints complete).
- **Must wait for:** Phase 1D, Phase 2A (initial routes).

---

### Phase 3: Dockerization, System Verification & Demo Hardening
- **Goal:** Assemble full Docker Compose multi-container deployment, execute 15 adversarial test fixtures, verify 100% offline startup, and validate the 4-minute demo flow.
- **Responsible Agent:** `QA-DevOps-Lead`
- **Inputs:** Complete `backend/` and `frontend/` codebases.
- **Outputs:** Single-command `docker compose up --build` environment with zero external runtime dependencies.
- **Files Owned:** `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`, `tests/e2e/**`, `scripts/**`
- **Files Allowed to Modify:** Any file for bug fixing with regression test protection.
- **Interfaces Consumed:** Complete system stack.
- **Interfaces Produced:** Verified, demo-ready containerized package.
- **Tests Required:** `tests/e2e/test_adversarial_suite.py` (15 test scenarios pass).
- **Definition of Done:** Entire stack starts on a cold machine with no internet connection in $< 45$ seconds.
- **Can run in parallel with:** Nothing (Final convergence).
- **Must wait for:** Phase 2A, Phase 2B.

---

## 8. Workstream Ownership

```
┌─────────────────────────┬─────────────────────────┬────────────────────────────────────────────────────────┐
│ Workstream              │ Assigned AI Agent       │ Core Responsibilities                                 │
├─────────────────────────┼─────────────────────────┼────────────────────────────────────────────────────────┤
│ **Track A (Data/DB)**   │ `Agent-DataEngine`      │ PostgreSQL schema, CSV data cleaning, synthetic gen   │
│ **Track B (Algorithms)**│ `Agent-AlgoEngine`      │ Taxonomy dictionary, 7-stage entity resolution matcher │
│ **Track C (Detection)** │ `Agent-DetectionEngine` │ 4 anomaly lanes, temporal lag guardrail, exceptions    │
│ **Track D (Frontend)**  │ `Agent-FrontendEngine`  │ React UI, Tailwind styles, D3.js force-directed canvas │
│ **Track E (Backend)**   │ `Agent-BackendEngine`   │ FastAPI endpoints, NetworkX graph, PDF notice, audit   │
│ **Track F (QA/DevOps)** │ `Agent-DevOpsLead`      │ Docker compose, E2E validation, demo rehearsal check   │
└─────────────────────────┴─────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 9. File Ownership

To ensure multiple agents can write code simultaneously without git merge collisions or file stomping, file ownership is strictly segregated by directory boundaries:

```
repository-root/
│
├── contracts/                        [OWNER: Lead-Architect | READ-ONLY for all agents]
│   ├── db_schema.sql
│   ├── models.py
│   ├── types.ts
│   ├── openapi.yaml
│   ├── bronze_schemas.json
│   ├── detection_contract.json
│   ├── graph_schema.json
│   ├── notice_schema.json
│   ├── audit_contract.json
│   └── mock_data.json
│
├── backend/
│   ├── Dockerfile                    [OWNER: Agent-DevOpsLead]
│   ├── requirements.txt              [OWNER: Lead-Architect]
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py                 [OWNER: Lead-Architect]
│   │   ├── main.py                   [OWNER: Agent-BackendEngine]
│   │   │
│   │   ├── db/                       [OWNER: Agent-DataEngine]
│   │   │   ├── session.py
│   │   │   └── models.py
│   │   │
│   │   ├── ingestion/                [OWNER: Agent-DataEngine]
│   │   │   ├── udise_loader.py
│   │   │   ├── esakshi_loader.py
│   │   │   └── hasher.py
│   │   │
│   │   ├── normalization/            [OWNER: Agent-AlgoEngine]
│   │   │   ├── taxonomy.py
│   │   │   └── lgd_mapper.py
│   │   │
│   │   ├── resolution/               [OWNER: Agent-AlgoEngine]
│   │   │   ├── cleaner.py
│   │   │   ├── matcher.py
│   │   │   └── spatial_fallback.py
│   │   │
│   │   ├── detection/                [OWNER: Agent-DetectionEngine]
│   │   │   ├── lane1_statutory.py
│   │   │   ├── lane2_need.py
│   │   │   ├── lane3_reflection.py
│   │   │   ├── lane4_physics.py
│   │   │   ├── temporal_guard.py
│   │   │   └── exceptions.py
│   │   │
│   │   ├── fusion/                   [OWNER: Agent-BackendEngine]
│   │   │   ├── scoring.py
│   │   │   └── tiers.py
│   │   │
│   │   ├── explainability/           [OWNER: Agent-BackendEngine]
│   │   │   ├── graph_builder.py
│   │   │   └── narrative_builder.py
│   │   │
│   │   ├── notices/                  [OWNER: Agent-BackendEngine]
│   │   │   └── generator.py
│   │   │
│   │   ├── audit/                    [OWNER: Agent-BackendEngine]
│   │   │   └── hash_chain.py
│   │   │
│   │   └── api/                      [OWNER: Agent-BackendEngine]
│   │       ├── router.py
│   │       ├── cases.py
│   │       ├── ambiguity.py
│   │       └── analytics.py
│   │
│   └── scripts/                      [OWNER: Agent-DataEngine]
│       ├── generate_synthetic_esakshi.py
│       └── load_udise_data.py
│
├── frontend/                         [OWNER: Agent-FrontendEngine & Agent-UIIntegration]
│   ├── Dockerfile
│   ├── package.json
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   │   ├── CaseQueue.tsx
│   │   │   ├── CaseDetail.tsx
│   │   │   ├── EvidenceGraph.tsx
│   │   │   ├── AmbiguityQueue.tsx
│   │   │   └── DistrictOverview.tsx
│   │   ├── types/
│   │   └── App.tsx
│
├── tests/
│   ├── contracts/                    [OWNER: Lead-Architect]
│   ├── ingestion/                    [OWNER: Agent-DataEngine]
│   ├── resolution/                   [OWNER: Agent-AlgoEngine]
│   ├── detection/                    [OWNER: Agent-DetectionEngine]
│   ├── backend/                      [OWNER: Agent-BackendEngine]
│   └── e2e/                          [OWNER: Agent-DevOpsLead]
│
└── docker-compose.yml                [OWNER: Agent-DevOpsLead]
```

---

## 10. Interface Contracts

Below are the canonical, production-ready schema and code contracts that govern all parallel modules.

### 10.1 Canonical Enums & Data Classes (`contracts/models.py`)

```python
# contracts/models.py
from enum import Enum
from datetime import date, datetime
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

class SchoolMasterSchema(BaseModel):
    udise_code: str = Field(min_length=11, max_length=11)
    name_canonical: str
    state_lgd_code: int
    district_lgd_code: int
    block_lgd_code: int
    village_name: str | None = None
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
    has_electricity: bool
    has_drinking_water: bool
    functional_girls_toilets: int = 0
    functional_boys_toilets: int = 0
    has_computer_lab: bool = False
    data_freeze_date: date
    data_published_date: date | None = None
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
    completion_date: date | None = None
    latitude: float | None = None
    longitude: float | None = None
    resolved_udise_code: str | None = None
    resolution_confidence: float | None = None
    resolution_status: ResolutionStatus = ResolutionStatus.UNRESOLVED
```

### 10.2 Detection Output Contract (`contracts/detection_contract.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "DetectionCaseResult",
  "type": "object",
  "properties": {
    "project_id": { "type": "string" },
    "udise_code": { "type": "string" },
    "lane_results": {
      "type": "object",
      "properties": {
        "STATUTORY": {
          "type": "object",
          "properties": {
            "score": { "type": "number", "minimum": 0, "maximum": 1 },
            "violations": { "type": "array", "items": { "type": "string" } }
          },
          "required": ["score", "violations"]
        },
        "INSTITUTIONAL_NEED": {
          "type": "object",
          "properties": {
            "score": { "type": "number", "minimum": 0, "maximum": 1 },
            "metrics": {
              "type": "object",
              "properties": {
                "latest_scr": { "type": "number" },
                "3yr_enrollment_growth": { "type": "number" }
              }
            }
          },
          "required": ["score"]
        },
        "ASSET_REFLECTION": {
          "type": "object",
          "properties": {
            "score": { "type": "number", "minimum": 0, "maximum": 1 },
            "status": { "type": "string" },
            "observed_delta": { "type": "integer" },
            "expected_delta": { "type": "integer" }
          },
          "required": ["score", "status"]
        },
        "TIMELINE_PHYSICS": {
          "type": "object",
          "properties": {
            "score": { "type": "number", "minimum": 0, "maximum": 1 },
            "violation": { "type": ["string", "null"] },
            "duration_days": { "type": "integer" }
          },
          "required": ["score"]
        }
      },
      "required": ["STATUTORY", "INSTITUTIONAL_NEED", "ASSET_REFLECTION", "TIMELINE_PHYSICS"]
    },
    "ipi_score": { "type": "number", "minimum": 0, "maximum": 100 },
    "ipi_lower": { "type": "number", "minimum": 0, "maximum": 100 },
    "ipi_upper": { "type": "number", "minimum": 0, "maximum": 100 },
    "risk_tier": { "type": "integer", "enum": [1, 2, 3] },
    "primary_category": { "type": "string" },
    "exception_adjustments": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": { "type": "string" },
          "reduction": { "type": "number" },
          "reason": { "type": "string" }
        }
      }
    }
  },
  "required": ["project_id", "udise_code", "lane_results", "ipi_score", "risk_tier", "primary_category"]
}
```

### 10.3 D3 Evidence Subgraph Contract (`contracts/graph_schema.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "D3GraphPayload",
  "type": "object",
  "properties": {
    "directed": { "type": "boolean" },
    "multigraph": { "type": "boolean" },
    "nodes": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "label": { "type": "string" },
          "type": { "type": "string", "enum": ["PROJECT", "SCHOOL", "STATE", "CONTRADICTION", "RULE"] },
          "properties": { "type": "object" }
        },
        "required": ["id", "label", "type"]
      }
    },
    "links": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "source": { "type": "string" },
          "target": { "type": "string" },
          "relation": { "type": "string" },
          "confidence": { "type": "number" }
        },
        "required": ["source", "target", "relation"]
      }
    }
  },
  "required": ["nodes", "links"]
}
```

---

## 11. Mock Strategy

To guarantee that the Frontend (`Track D`) and Integration tests can proceed simultaneously with Database and Algorithm work, a comprehensive mock dataset is created in Phase 0.

### Mock Server & Fixtures Setup

1. **Location:** `contracts/mock_data.json`
2. **Frontend Mock Service Worker (MSW) / Mock Adapter:** The React frontend includes a toggle `REACT_APP_USE_MOCKS=true` that returns static responses conforming exactly to `contracts/openapi.yaml`.
3. **Representative Mock Case (The Demo Case):**

```json
{
  "case_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "project_id": "PRJ-2023-04567",
  "mp_id": "MP-LS-HP-02",
  "school_name": "Government High School Rampur",
  "udise_code": "02120100402",
  "sanction_cost": 1240000.00,
  "canonical_asset_type": "ADDITIONAL_CLASSROOM",
  "target_quantity": 2,
  "recommendation_date": "2023-04-01",
  "sanction_date": "2023-04-15",
  "completion_date": "2023-05-08",
  "ipi_score": 82.0,
  "ipi_lower": 74.0,
  "ipi_upper": 90.0,
  "risk_tier": 3,
  "primary_category": "COMPOUND_REFLECTION_AND_VELOCITY_GAP",
  "status": "PENDING_REVIEW",
  "evidence_graph": {
    "nodes": [
      { "id": "project:PRJ-2023-04567", "label": "MPLADS Project", "type": "PROJECT", "properties": { "cost": "₹12.4 Lakh", "asset": "2 Classrooms" } },
      { "id": "school:02120100402", "label": "GHS Rampur", "type": "SCHOOL", "properties": { "code": "02120100402", "mgmt": "GOVERNMENT" } },
      { "id": "state:2022-23", "label": "Pre-Sanction (2022-23)", "type": "STATE", "properties": { "rooms": 7, "enr": 43 } },
      { "id": "state:2024-25", "label": "Post-Comp (2024-25)", "type": "STATE", "properties": { "rooms": 7, "enr": 31 } },
      { "id": "contradiction:refl_gap", "label": "Zero Room Delta", "type": "CONTRADICTION", "properties": { "expected": 2, "observed": 0 } },
      { "id": "contradiction:velocity", "label": "Velocity Violation (23 Days)", "type": "CONTRADICTION", "properties": { "min_bound": 45, "actual": 23 } }
    ],
    "links": [
      { "source": "project:PRJ-2023-04567", "target": "school:02120100402", "relation": "CLAIMS_TARGET_INSTITUTION", "confidence": 0.92 },
      { "source": "school:02120100402", "target": "state:2022-23", "relation": "RECORDED_BASELINE" },
      { "source": "school:02120100402", "target": "state:2024-25", "relation": "RECORDED_POST_COMP" },
      { "source": "project:PRJ-2023-04567", "target": "contradiction:refl_gap", "relation": "CONTRADICTED_BY" },
      { "source": "state:2024-25", "target": "contradiction:refl_gap", "relation": "EVIDENCE_ANCHOR" },
      { "source": "project:PRJ-2023-04567", "target": "contradiction:velocity", "relation": "VIOLATES_PHYSICS" }
    ]
  },
  "explanation_narrative": "Project PRJ-2023-04567 claimed completion of 2 Additional Classrooms in 23 days at GHS Rampur. Independent UDISE+ return (2024-25) records exactly 7 classrooms, identical to the pre-sanction baseline (2022-23). Construction velocity violates IS 456 concrete curing limits."
}
```

---

## 12. Critical Path

The **Critical Path** represents the absolute shortest dependency chain needed to achieve a working end-to-end demonstration:

```
[Phase 0: Frozen Schemas]
           │
           ▼
[Clean UDISE+ CSVs + Synthetic e-SAKSHI Case]
           │
           ▼
[7-Stage Entity Matcher Resolves Demo School]
           │
           ▼
[Lane 3 Reflection + Lane 4 Velocity Flags Anomaly]
           │
           ▼
[Max-Pooled Fusion Computes IPI = 82]
           │
           ▼
[NetworkX Generates D3 Evidence Subgraph]
           │
           ▼
[FastAPI Returns Case JSON & PDF Notice]
           │
           ▼
[React UI Visualizes Evidence Graph on Screen]
```

Any delay on this chain directly delays the first working end-to-end vertical slice. All auxiliary features (such as bulk analytics heatmaps, multi-user authentication, and advanced search filters) are non-critical path.

---

## 13. MVP Layers

To guarantee maximum speed and focus during the hackathon, system features are categorized into strict priority layers:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                SYSTEM MATURITY LAYERS                                   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  LAYER 1: MUST-HAVE FOR FIRST END-TO-END VERTICAL SLICE (Target: Hour 8)                │
│  • 1 Target District (Kangra) loaded into PostgreSQL with real UDISE+ data (~2,000 sch) │
│  • 1 Synthetic e-SAKSHI project mapped via 7-stage entity resolution                    │
│  • 4 detection lanes evaluated + Census Lag Guardrail active                            │
│  • IPI scored via orthogonal max-pooling formula                                        │
│  • NetworkX serializes D3 graph; FastAPI serves GET /api/v1/cases                       │
│  • React UI displays case queue and renders interactive D3 graph on screen              │
│                                                                                         │
│  LAYER 2: MUST-HAVE FOR FINAL SIH DEMO (Target: Hour 24)                                │
│  • Full batch processing of 250 synthetic projects across Kangra District               │
│  • Human Ambiguity Queue ($0.60–0.84$ confidence) with split-pane manual disambiguation │
│  • Form MPLADS-INSP-1 PDF Notice generation via ReportLab                               │
│  • Cryptographic SHA-256 append-only audit log chain for investigator actions            │
│  • Complete 3-container Docker Compose deployment running 100% offline                  │
│                                                                                         │
│  LAYER 3: SHOULD-HAVE (Target: Hour 30)                                                 │
│  • Geospatial Leaflet/Mapbox district allocation heatmap                                │
│  • Exception Context Engine (dilapidated room demolition & school merger handling)      │
│  • Exportable CSV case audit reports                                                    │
│                                                                                         │
│  LAYER 4: OPTIONAL / POLISH (Target: Hour 34)                                           │
│  • Dark mode UI theme toggle                                                            │
│  • Sub-district aggregate spend charts                                                  │
│                                                                                         │
│  LAYER 5: FUTURE / DEFERRED (Post-Hackathon Production)                                 │
│  • Live CPPP / GeM tender bidding contractor network graph                              │
│  • Satellite Earth Observation (Sentinel-2) roof construction diffing                    │
│  • Direct MeitY API Gateway & SNA-SPARSH payment hold integration                       │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 14. Integration Checkpoints

```
┌──────────────┬──────────────────────────────────┬────────────────────────────────────────────────────────┐
│ Checkpoint   │ Target Milestone                 │ Verification Command / Success Criteria                │
├──────────────┼──────────────────────────────────┼────────────────────────────────────────────────────────┤
│ **CP 1**     │ Database + Real Data Loaded      │ `pytest tests/ingestion/test_udise_load.py` (2,000 sch)│
│ **CP 2**     │ Entity Resolution Match          │ `pytest tests/resolution/test_matcher.py` (>=85% prec) │
│ **CP 3**     │ 4 Anomaly Lanes Execute          │ `pytest tests/detection/test_lanes.py` (Score calibrated)│
│ **CP 4**     │ Temporal Guardrail Active        │ `pytest tests/detection/test_lag_guard.py` (0 false +) │
│ **CP 5**     │ Provenance Graph Built           │ `pytest tests/backend/test_graph.py` (D3 JSON valid)   │
│ **CP 6**     │ FastAPI Serves Case Queue        │ `curl http://localhost:8000/api/v1/cases` -> 200 OK    │
│ **CP 7**     │ React Renders D3 Graph           │ Browser renders force-directed graph on localhost:3000 │
│ **CP 8**     │ PDF Notice Downloads             │ `curl http://localhost:8000/api/v1/cases/{id}/pdf`     │
│ **CP 9**     │ Full Docker Compose Runs Offline │ `docker compose up --build` succeeds without internet  │
│ **CP 10**    │ 15 Adversarial Fixtures Pass     │ `pytest tests/e2e/test_adversarial_suite.py` (100% OK) │
└──────────────┴──────────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 15. Automated Test Gates

Every phase must satisfy an automated test gate before merge. No agent may mark its work complete without passing its corresponding gate.

```
Phase Complete ONLY IF:
1. All unit tests in the workstream directory pass with 0 failures.
2. Code strictly conforms to frozen contracts in contracts/.
3. No files outside the agent's owned directory were modified.
4. Flake8 / Ruff linting and Mypy type-checking pass with 0 errors.
5. All JSON/API outputs match frozen Pydantic schemas.
```

### Test Gate Scripts

- **Track A Gate:** `pytest tests/ingestion/ -v --tb=short`
- **Track B Gate:** `pytest tests/resolution/ -v --tb=short`
- **Track C Gate:** `pytest tests/detection/ -v --tb=short`
- **Track D Gate:** `cd frontend && npm test -- --watchAll=false`
- **Track E Gate:** `pytest tests/backend/ -v --tb=short`
- **System Gate:** `pytest tests/e2e/ -v && docker compose build`

---

## 16. Git/Agent Isolation Strategy

### Recommended Model: Worktree Isolation with Strict File Ownership

To prevent merge chaos, race conditions, or accidental overwrites among autonomous agents, we adopt **Git Worktrees with Directory Boundary Isolation**:

```
[Main Repository: d:\MPLAD-watch] (Master Branch)
      │
      ├── worktrees/agent-data/        (Branch: feature/track-a-data)
      ├── worktrees/agent-algo/        (Branch: feature/track-b-algo)
      ├── worktrees/agent-detection/   (Branch: feature/track-c-detection)
      ├── worktrees/agent-frontend/    (Branch: feature/track-d-frontend)
      └── worktrees/agent-backend/     (Branch: feature/track-e-backend)
```

### Safety Rules:
1. **No Shared Code Files:** Agents in Phase 1 touch 100% disjoint directories (`backend/app/db/` vs `backend/app/resolution/` vs `backend/app/detection/` vs `frontend/`).
2. **Read-Only Contracts:** The `contracts/` directory is immutable. Agents only read from it.
3. **Atomic Merges:** Agents merge their completed branches into `master` strictly following the predefined merge order after test gate verification.

---

## 17. Merge Order

```
┌─────────────────────────────────────────────────────────┐
│                   STEP-BY-STEP MERGE ORDER              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  STEP 1: Merge Phase 0 (Contracts & Scaffolding)        │
│          └── Validates schemas and sets base master     │
│                                                         │
│  STEP 2: Merge Track A (Database & Ingestion)           │
│          └── Establishes live PostgreSQL tables         │
│                                                         │
│  STEP 3: Merge Track B (Entity Resolution)              │
│          └── Adds normalization and matcher modules     │
│                                                         │
│  STEP 4: Merge Track C (Detection & Lag Guardrail)      │
│          └── Adds anomaly lanes & exception logic       │
│                                                         │
│  STEP 5: Merge Track E (Backend API, Graph & Notices)   │
│          └── Wires all backend algorithms to FastAPI    │
│                                                         │
│  STEP 6: Merge Track D + F (Frontend UI & API Binding)  │
│          └── Connects React UI to live backend          │
│                                                         │
│  STEP 7: Merge Phase 3 (Docker Compose & E2E Tests)     │
│          └── Finalizes full production build            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 18. Agent Task Prompts

These standardized, copy-paste prompts are designed for autonomous Antigravity agents to execute each workstream with zero ambiguity.

---

### Agent Prompt: Track A (Data Ingestion & Database)

```text
ROLE: Senior Data Engineer
TASK: Implement PostgreSQL/PostGIS schema and data ingestion pipelines for real UDISE+ and synthetic e-SAKSHI records.

READ THESE FILES FIRST:
- FINAL_ARCHITECTURE.md (Sections 8, 20)
- contracts/db_schema.sql
- contracts/bronze_schemas.json
- contracts/models.py

OWNED FILES:
- backend/app/db/**
- backend/app/ingestion/**
- backend/scripts/load_udise_data.py
- backend/scripts/generate_synthetic_esakshi.py
- tests/ingestion/**

FORBIDDEN CHANGES:
- Do NOT touch backend/app/resolution/**
- Do NOT touch backend/app/detection/**
- Do NOT touch frontend/**
- Do NOT alter contracts/**

IMPLEMENTATION REQUIREMENTS:
1. Implement SQLAlchemy models in backend/app/db/models.py exactly matching contracts/db_schema.sql.
2. Implement load_udise_data.py to ingest real UDISE+ open data CSVs for Kangra district (~2,000 schools across Sec 1A, 2, 3) into `schools` and `school_annual_states`. Compute SHA-256 hashes for every ingested state.
3. Implement generate_synthetic_esakshi.py to generate 250 realistic MPLADS projects adhering strictly to MoSPI 2023 Guidelines, including the canonical demo case PRJ-2023-04567.
4. Support PostGIS geometry points for school and project coordinates.

TEST REQUIREMENTS:
- Create tests/ingestion/test_ingestion.py verifying:
  * Table row counts (>1,500 schools loaded)
  * Foreign key integrity between schools and annual states
  * PostGIS spatial coordinates correctly parsed
  * SHA-256 digests generated for bronze records

DEFINITION OF DONE:
`pytest tests/ingestion` passes with 100% success.
```

---

### Agent Prompt: Track B (Entity Resolution & Taxonomy)

```text
ROLE: Senior Algorithm & NLP Engineer
TASK: Implement the controlled vocabulary asset taxonomy and the 7-stage entity resolution matcher with reverse spatial fallback.

READ THESE FILES FIRST:
- FINAL_ARCHITECTURE.md (Sections 9, 10)
- RED_TEAM_AUDIT__.md (Section 4)
- contracts/models.py

OWNED FILES:
- backend/app/normalization/**
- backend/app/resolution/**
- tests/resolution/**

FORBIDDEN CHANGES:
- Do NOT touch backend/app/db/**
- Do NOT touch backend/app/detection/**
- Do NOT touch frontend/**
- Do NOT alter contracts/**

IMPLEMENTATION REQUIREMENTS:
1. Implement backend/app/normalization/taxonomy.py: Regex dictionary mapping unstructured text to CanonicalAssetType and quantity.
2. Implement backend/app/resolution/cleaner.py: Text cleaner expanding abbreviations (GHS -> Government High School, etc.).
3. Implement backend/app/resolution/matcher.py: 7-stage matcher combining LGD district blocking, Jaro-Winkler (0.65 weight), Double Metaphone (0.35 weight), and Haversine spatial gating.
4. Implement Reverse Spatial Fallback: If string similarity < 0.50 but GPS distance <= 300m, search historical aliases and auto-accept with 0.86 confidence.
5. Confidence routing: >= 0.85 (AUTO_ACCEPTED), 0.60–0.84 (AMBIGUOUS), < 0.60 (UNRESOLVED).

TEST REQUIREMENTS:
- Create tests/resolution/test_matcher.py testing all 10 adversarial edge cases from RED_TEAM_AUDIT__.md Section 4, including renamed schools and multi-school campuses.

DEFINITION OF DONE:
`pytest tests/resolution` passes with 100% success; sub-millisecond execution per match.
```

---

### Agent Prompt: Track C (Multi-Lane Detection & Lag Guardrail)

```text
ROLE: Senior Fraud Detection & Data Science Engineer
TASK: Implement the 4-lane anomaly detection engine, temporal lag compensation guardrail, and exception context engine.

READ THESE FILES FIRST:
- FINAL_ARCHITECTURE.md (Sections 12, 13, 14, 15)
- RED_TEAM_AUDIT__.md (Sections 5, 6)
- contracts/detection_contract.json
- contracts/models.py

OWNED FILES:
- backend/app/detection/**
- tests/detection/**

FORBIDDEN CHANGES:
- Do NOT touch backend/app/db/**
- Do NOT touch backend/app/resolution/**
- Do NOT touch frontend/**
- Do NOT alter contracts/**

IMPLEMENTATION REQUIREMENTS:
1. Lane 1 (Statutory): Check private school eligibility and 75-day sanction window.
2. Lane 2 (Need): Calculate student-to-classroom ratio (SCR) and 3-year enrollment trend slope.
3. Lane 3 (Asset Reflection): Compare post-completion vs. pre-sanction room counts.
4. Temporal Lag Guardrail: If Date_UDISE_Freeze < Date_Completion + 180 days, suppress Lane 3 and return PENDING_CENSUS_CYCLE with zero penalty.
5. Lane 4 (Timeline Physics): Validate construction duration against IS 456 concrete curing limits (min 45 days for classrooms, 21 days for general civil).
6. Exception Context Engine: Demolished dilapidated classroom and school merger adjustments.

TEST REQUIREMENTS:
- Create tests/detection/test_lanes.py testing:
  * Complete asset reflection gap (0 delta -> score 0.90)
  * Physics velocity violation (23 days -> score 0.95)
  * Temporal lag suppression (October project vs September census -> score 0.0)
  * Statutory private school rule violation (score 1.0)

DEFINITION OF DONE:
`pytest tests/detection` passes with 100% success; zero false positives under census lag scenarios.
```

---

### Agent Prompt: Track D (Frontend React & D3 UI)

```text
ROLE: Senior Frontend & Data Visualization Engineer
TASK: Build the React 18 + Tailwind CSS single-page application with 3-tier queue, split-pane case detail, D3.js force-directed evidence graph, and ambiguity resolution interface.

READ THESE FILES FIRST:
- FINAL_ARCHITECTURE.md (Sections 16, 17, 19)
- contracts/openapi.yaml
- contracts/graph_schema.json
- contracts/mock_data.json

OWNED FILES:
- frontend/**

FORBIDDEN CHANGES:
- Do NOT touch backend/**
- Do NOT alter contracts/**

IMPLEMENTATION REQUIREMENTS:
1. Setup React 18 + TypeScript + Tailwind CSS application structure.
2. Implement District Overview Dashboard with summary metric cards (Total Outlay, Tiers 1/2/3 count).
3. Implement Case Queue Table filterable by Risk Tier, Asset Type, and Confidence Band.
4. Implement Case Detail Split-Pane: Left pane shows structured fact narrative and lane scores; Right pane renders interactive D3.js force-directed evidence graph with zoom, pan, and node click inspection.
5. Implement Human Ambiguity Queue: Side-by-side school card comparison for manual confirmation.
6. Support mock mode (`REACT_APP_USE_MOCKS=true`) using contracts/mock_data.json.

TEST REQUIREMENTS:
- Unit tests for component rendering and D3 canvas initialization (`npm test`).

DEFINITION OF DONE:
React app compiles cleanly with 0 linter warnings; D3 graph renders smoothly with force simulation.
```

---

### Agent Prompt: Track E (Backend API, Graph Builder & PDF Notice)

```text
ROLE: Senior Backend & Systems Integration Engineer
TASK: Implement FastAPI REST routes, NetworkX provenance graph serializer, Form MPLADS-INSP-1 PDF notice generator, and SHA-256 audit hash chain.

READ THESE FILES FIRST:
- FINAL_ARCHITECTURE.md (Sections 15, 16, 18, 20, 21, 22)
- contracts/openapi.yaml
- contracts/notice_schema.json
- contracts/audit_contract.json

OWNED FILES:
- backend/app/fusion/**
- backend/app/explainability/**
- backend/app/notices/**
- backend/app/audit/**
- backend/app/api/**
- backend/app/main.py
- tests/backend/**

FORBIDDEN CHANGES:
- Do NOT touch frontend/**
- Do NOT alter contracts/**

IMPLEMENTATION REQUIREMENTS:
1. Implement orthogonal max-pooled fusion scoring in backend/app/fusion/scoring.py:
   IPI = 30*S_stat + 15*max(S_need) + 35*S_refl + 20*S_phys.
2. Implement NetworkX DiGraph builder in backend/app/explainability/graph_builder.py, serializing nodes and edges to D3 format.
3. Implement PDF Notice generator in backend/app/notices/generator.py (ReportLab) outputting Form MPLADS-INSP-1.
4. Implement SHA-256 audit logger in backend/app/audit/hash_chain.py chaining all triage decisions.
5. Implement FastAPI endpoints in backend/app/api/ matching contracts/openapi.yaml.

TEST REQUIREMENTS:
- Create tests/backend/test_api.py testing:
  * GET /api/v1/cases (returns case list with correct tiers)
  * GET /api/v1/cases/{id}/evidence-graph (returns valid D3 JSON)
  * GET /api/v1/cases/{id}/notice/pdf (returns valid PDF bytes)
  * POST /api/v1/cases/{id}/decision (appends to audit hash chain)

DEFINITION OF DONE:
`pytest tests/backend` passes with 100% success; OpenAPI docs available at /docs.
```

---

## 19. Time Estimates

Estimated effort across human engineering time and AI active generation time:

| Phase / Track | Human-Hours | AI Active Time (Optimistic) | AI Active Time (Realistic) | AI Active Time (Pessimistic) | Primary Bottleneck |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Phase 0: Scaffolding & Contracts** | 2.0 hrs | 15 mins | 25 mins | 40 mins | Schema precision & alignment |
| **Track A: Data Ingestion & DB** | 3.5 hrs | 25 mins | 45 mins | 80 mins | UDISE+ CSV column mapping variations |
| **Track B: Entity Resolution** | 3.0 hrs | 20 mins | 35 mins | 60 mins | Spatial edge cases & reverse lookup |
| **Track C: Detection & Lag Guard** | 3.0 hrs | 20 mins | 35 mins | 60 mins | Invariant validation & physics bounds |
| **Track D: Frontend Shell & D3** | 4.0 hrs | 30 mins | 50 mins | 90 mins | D3 force simulation layout tuning |
| **Track E: Backend API & PDF** | 3.5 hrs | 25 mins | 45 mins | 75 mins | ReportLab PDF layout formatting |
| **Track F: UI/API Integration** | 2.5 hrs | 20 mins | 35 mins | 55 mins | CORS & state synchronization |
| **Phase 3: Docker & System QA** | 3.0 hrs | 20 mins | 40 mins | 70 mins | Multi-container networking & startup |
| **TOTAL (Cumulative)** | **24.5 hrs** | **2.9 hrs** | **5.2 hrs** | **8.8 hrs** | **Integration & Real Data Nuances** |

---

## 20. Risk Register

```
┌──────────────────────────────────────┬──────────┬───────────┬────────────────────────────────────────────────────────┐
│ Identified Risk                      │ Impact   │ Severity  │ Mitigation Strategy Hardcoded in Build Plan            │
├──────────────────────────────────────┼──────────┼───────────┼────────────────────────────────────────────────────────┤
│ **UDISE+ Annual Census Lag Trap**    │ Critical │ CRITICAL  │ Hardcode Temporal Lag Guardrail: suppress Lane 3 if    │
│                                      │          │           │ Date_Freeze < Date_Completion + 180 days.              │
├──────────────────────────────────────┼──────────┼───────────┼────────────────────────────────────────────────────────┤
│ **e-SAKSHI Inaccessibility**         │ Critical │ CRITICAL  │ Do not scrape live; use 100% real UDISE+ data +        │
│                                      │          │           │ schema-authentic synthetic generator.                  │
├──────────────────────────────────────┼──────────┼───────────┼────────────────────────────────────────────────────────┤
│ **Renamed School Match Failure**     │ High     │ HIGH      │ Reverse Spatial Candidate Fallback anchors on GPS      │
│                                      │          │           │ coordinates within 300m to look up alias records.      │
├──────────────────────────────────────┼──────────┼───────────┼────────────────────────────────────────────────────────┤
│ **Double-Counting Demographic Risk** │ High     │ HIGH      │ Orthogonal Max-Pooling math prevents correlated        │
│                                      │          │           │ enrollment drop and SCR flags from compounding.        │
├──────────────────────────────────────┼──────────┼───────────┼────────────────────────────────────────────────────────┤
│ **Jury Accusation of "Fake AI"**     │ Critical │ CRITICAL  │ Never claim neural net fraud classification; state:    │
│                                      │          │           │ "Deterministic multi-lane constraint & physics engine."│
├──────────────────────────────────────┼──────────┼───────────┼────────────────────────────────────────────────────────┤
│ **Venue Internet Failure at Demo**   │ Critical │ HIGH      │ 100% offline Docker Compose setup on localhost.        │
├──────────────────────────────────────┼──────────┼───────────┼────────────────────────────────────────────────────────┤
│ **Neo4j / Java JVM Memory Exhaust**  │ Medium   │ MEDIUM    │ Discard Neo4j; use in-memory NetworkX serializing      │
│                                      │          │           │ directly to D3.js node-link JSON.                      │
└──────────────────────────────────────┴──────────┴───────────┴────────────────────────────────────────────────────────┘
```

---

## 21. AI Failure Safeguards

To safeguard against common AI code generation failures during parallel execution:

1. **Anti-Hallucination Rule:** Agents are forbidden from creating ad-hoc API routes or altering database column names. All schemas must import from `contracts/models.py`.
2. **Directory Confinement:** Each agent is strictly confined to its owned directory. Any modification to a foreign directory fails the automated gate.
3. **No External API Dependencies:** Agents must not inject third-party cloud services (OpenAI, Google Maps, AWS S3). All geospatial math uses pure-Python Haversine/PostGIS and all graphs use NetworkX.
4. **Deterministic Reproducibility:** All synthetic generators must use a fixed random seed (`seed=42`) to produce identical, reproducible datasets across runs.
5. **No Silent Refactoring:** If an agent encounters a bug in another module, it must report it rather than unilaterally refactoring shared code.

---

## 22. Demo-First Development Plan

The entire prototype converges toward the **4-Minute SIH Jury Demo Flow**:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              THE 4-MINUTE WINNING DEMO FLOW                             │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  [0:00 - 0:45] THE HOOK: The Blind Spot of Existing Systems                             │
│  • Present e-SAKSHI Work ID PRJ-2023-04567: ₹12.4 Lakh disbursed, marked 100% Complete. │
│  • Show that intra-system checks give it a green checkmark.                             │
│                                                                                         │
│  [0:45 - 1:30] THE INTER-SYSTEM PIVOT                                                   │
│  • Demonstrate MEEV 7-stage entity resolution matching free-text description to         │
│    UDISE+ School Code 02120100402 (GHS Rampur) with 92% confidence.                     │
│                                                                                         │
│  [1:30 - 2:45] THE EVIDENCE ENGINE & THE D3 PROVENANCE GRAPH                            │
│  • Lane 1 (Statutory): Eligible.                                                        │
│  • Lane 2 (Need): Enrollment collapsed 52%; school has 7 rooms for 31 pupils.          │
│  • Lane 3 (Reflection): UDISE+ post-completion census records 0 classroom increase.    │
│  • Lane 4 (Velocity): Claimed completed in 23 days (violating concrete curing physics). │
│  • Interact with the D3 Evidence Graph: click nodes to view raw SHA-256 hashes.         │
│                                                                                         │
│  [2:45 - 3:30] STATUTORY ACTION GENERATION                                              │
│  • Show Investigation Priority Index (IPI = 82, Tier 3).                                │
│  • Click "Generate Statutory Notice" -> Download Form MPLADS-INSP-1 PDF pre-filled       │
│    under Section 6.4 for the District Collector.                                        │
│                                                                                         │
│  [3:30 - 4:00] THE CLINCHER                                                             │
│  • "The money moved. The paperwork was signed. But the school's own independent census │
│    proves the asset never appeared. That is Inter-System Validation."                   │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 23. Final End-to-End Acceptance Criteria

The system is declared production-ready and hackathon-compliant if and only if:

1. **Offline Execution:** Full stack boots up cleanly via `docker compose up --build` on a machine with no internet connection.
2. **Real Data Loading:** Database successfully loads $\ge 1,500$ real schools for Kangra district from UDISE+ open data CSVs.
3. **High-Precision Matching:** 7-stage entity resolution matches $>80\%$ of synthetic e-SAKSHI records to valid UDISE+ codes, with renamed schools resolved via Reverse Spatial Search.
4. **Zero Lag False Positives:** The 180-day Census Lag Guardrail prevents false-positive reflection flags on projects completed after the annual DCF freeze.
5. **Interactive Visualization:** The React frontend renders the D3.js evidence graph with responsive node-link physics and inspectable evidence cards.
6. **Statutory Notice Creation:** Clicking "Download Notice" generates a valid, formatted Form MPLADS-INSP-1 PDF with intact cryptographic hashes.
7. **Audit Trail Defensibility:** Every triage action is appended to the SHA-256 cryptographic audit chain.
8. **Test Suite Green:** All automated test gates (`pytest`, `npm test`, adversarial suite) pass with 100% success.

---

## 24. "STOP BUILDING" Conditions

To prevent scope creep, overengineering, or breaking working components during the hackathon, developers and AI agents must **STOP BUILDING** when:

1. The 4-minute demo scenario (PRJ-2023-04567) executes end-to-end without errors.
2. All 15 adversarial test cases pass.
3. The Docker Compose stack starts reliably in $< 45$ seconds.

### Strictly Prohibited Additions Once Criteria Are Met:
- Do NOT attempt live web scraping of e-SAKSHI.
- Do NOT integrate external cloud LLM APIs.
- Do NOT install Neo4j or separate graph databases.
- Do NOT attempt to build a CPPP procurement scraper.
- Do NOT redesign UI themes or navigation menus.

---
*End of Master Implementation Plan — SIH26102 (MEEV)*
