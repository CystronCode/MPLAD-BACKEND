# TRACK E: BACKEND API & PROVENANCE ENGINE SPECIFICATION
## SIH26102 — MEEV (MPLADS Education Ecosystem Validator)

> **Document Type:** Track Execution & Build Specification  
> **Track:** Track E — FastAPI REST API, Fusion Math, NetworkX Graph Builder, PDF Notices & Audit Chain  
> **Role / Assigned Engineer:** Senior Backend & Systems Integration Engineer (`Agent-BackendEngine`)  
> **System Layer:** Business Logic Synthesis, REST API Endpoints, Cryptographic Hash Chain, PDF Notice Engine  
> **Master Reference:** `FINAL_ARCHITECTURE.md` (Sections 15, 16, 18, 20, 21, 22) reconciled with `RED_TEAM_AUDIT__.md` (Sections 8, 9)  
> **Autonomous Scope:** This document is 100% self-contained. You do NOT need to consult external build plans.

---

## 1. Track Objective & Architectural Boundaries

Track E is the central nervous system of MEEV. It unites the data layer (Track A), entity matcher (Track B), and detection lanes (Track C) into actionable REST API services for the frontend.

You will build:
1. **Orthogonal Max-Pooled Fusion Engine (`backend/app/fusion/scoring.py`):** Computes composite Investigation Priority Index (IPI) scores without double-counting correlated signals.
2. **NetworkX In-Memory Provenance Graph Serializer (`backend/app/explainability/graph_builder.py`):** Constructs directed subgraphs and serializes them to D3 node-link JSON without heavyweight JVM/Neo4j overhead.
3. **Statutory Notice PDF Generator (`backend/app/notices/generator.py`):** Compiles pre-filled Form MPLADS-INSP-1 legal inspection notices under Section 6.4 of the 2023 Guidelines via ReportLab.
4. **Append-Only Cryptographic Audit Hash Chain (`backend/app/audit/hash_chain.py`):** Guarantees tamper-proof logging of all human triage actions using SHA-256 hash chaining.
5. **FastAPI REST Endpoints (`backend/app/api/**`, `backend/app/main.py`):** Implements all OpenAPI 3.1.0 routes with CORS support.

---

## 2. File Ownership Boundaries

### ✅ Files You Own & Must Modify:
```
backend/app/fusion/scoring.py
backend/app/explainability/graph_builder.py
backend/app/explainability/narrative_builder.py
backend/app/notices/generator.py
backend/app/audit/hash_chain.py
backend/app/api/router.py
backend/app/api/cases.py
backend/app/api/ambiguity.py
backend/app/api/analytics.py
backend/app/main.py
tests/backend/test_api.py
```

### 🚫 Forbidden Files (Must NOT touch):
- `backend/app/db/models.py` (Owned by Track A)
- `backend/app/resolution/**` (Owned by Track B)
- `backend/app/detection/**` (Owned by Track C)
- `frontend/**` (Owned by Track D)
- `contracts/**` (Read-only reference)

---

## 3. Mathematical & Algorithmic Formulations

### 3.1 Orthogonal Dimension Max-Pooling Fusion Formula
To prevent double-counting collinear signals (e.g. enrollment drop and student-to-classroom ratio), MEEV applies max-pooling over the need dimension:

$$\text{IPI} = 100 \times \Big( 0.30 \cdot S_{\text{stat}} + 0.15 \cdot \max(S_{\text{ratio}}, S_{\text{trend}}) + 0.35 \cdot S_{\text{refl}} + 0.20 \cdot S_{\text{phys}} \Big) - \sum \text{Reductions}_{\text{Exceptions}}$$

$$\text{Uncertainty Band: } \pm U = 15 \times (1 - \text{Confidence}_{\text{Resolution}})$$
$$\text{IPI}_{\text{lower}} = \max(0, \text{IPI} - U), \quad \text{IPI}_{\text{upper}} = \min(100, \text{IPI} + U)$$

### 3.2 Action Tier Allocation:
- **Tier 1 (Auto-Archive):** $\text{IPI} < 35.0$
- **Tier 2 (Desk Review Required):** $35.0 \le \text{IPI} < 70.0$
- **Tier 3 (Mandatory Field Inspection):** $\text{IPI} \ge 70.0$

---

### 3.3 Cryptographic Hash Chain Math

$$\text{CurrentHash}_T = \text{SHA-256}\Big(\text{CanonicalJSON}(\text{Payload}_T) \parallel \text{ActorID}_T \parallel \text{Timestamp}_T \parallel \text{PreviousHash}_{T-1}\Big)$$
$$\text{GenesisHash} = \text{"0000000000000000000000000000000000000000000000000000000000000000"}$$

---

## 4. REST API Endpoint Specifications

All endpoints are prefixed with `/api/v1`:

```
┌────────────────────────────────────────┬────────┬────────────────────────────────────────────────────────┐
│ Endpoint                               │ Method │ Description & Response                                 │
├────────────────────────────────────────┼────────┼────────────────────────────────────────────────────────┤
│ `/cases`                               │ GET    │ Query cases filtered by `tier`, `min_ipi`, `status`.   │
│ `/cases/{case_id}`                     │ GET    │ Retrieve full case detail with metrics and narrative.  │
│ `/cases/{case_id}/evidence-graph`      │ GET    │ Fetch D3.js node-link JSON subgraph.                   │
│ `/cases/{case_id}/notice/pdf`          │ GET    │ Download generated Form MPLADS-INSP-1 PDF notice.      │
│ `/cases/{case_id}/decision`            │ POST   │ Record triage decision and append to SHA-256 chain.    │
│ `/ambiguity-queue`                     │ GET    │ Retrieve ambiguous school match tasks (0.60–0.84 band).│
│ `/ambiguity-queue/{project_id}/resolve`│ POST   │ Manually confirm target UDISE code assignment.         │
│ `/analytics/district`                  │ GET    │ Get district aggregate outlay and risk distribution.   │
│ `/health`                              │ GET    │ Service health status (`{"status": "HEALTHY"}`).       │
└────────────────────────────────────────┴────────┴────────────────────────────────────────────────────────┘
```

---

## 5. Automated Test Suite (`tests/backend/test_api.py`)

You must verify:
1. **Case Queue Retrieval:** `GET /api/v1/cases` returns 200 OK with populated cases.
2. **Demo Case Integrity:** Case `PRJ-2023-04567` returns $\text{IPI} \ge 70$ (Tier 3).
3. **D3 Graph Payload:** `GET /api/v1/cases/{id}/evidence-graph` returns valid `nodes` and `links`.
4. **PDF Notice Byte Stream:** `GET /api/v1/cases/{id}/notice/pdf` returns `application/pdf` with $> 100$ bytes.
5. **Decision Hash Chain:** `POST /api/v1/cases/{id}/decision` returns valid 64-char SHA-256 audit hash.
6. **District Analytics:** `GET /api/v1/analytics/district` returns aggregate statistics.

---

## 6. Definition of Done for Track E

- [x] All FastAPI routes implemented matching `contracts/openapi.yaml`.
- [x] Max-pooled IPI math calibrated and tested.
- [x] In-memory NetworkX serializer generates clean D3 payloads.
- [x] PDF Notice Generator creates valid Form MPLADS-INSP-1 documents.
- [x] `pytest tests/backend/ -v` passes with 100% success.
- [x] Zero modifications to Track A, B, C, or D files.
