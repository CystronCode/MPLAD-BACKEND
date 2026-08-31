# TRACK D: FRONTEND UI & DATA VISUALIZATION SPECIFICATION
## SIH26102 — MEEV (MPLADS Education Ecosystem Validator)

> **Document Type:** Track Execution & Build Specification  
> **Track:** Track D — React 18 Single-Page Application & D3.js Force-Directed Evidence Graph  
> **Role / Assigned Engineer:** Senior Frontend & Data Visualization Engineer (`Agent-FrontendEngine`)  
> **System Layer:** Presentation Layer, 3-Tier Queue, D3 Force Simulation, Ambiguity Reconciliation UI  
> **Master Reference:** `FINAL_ARCHITECTURE.md` (Sections 16, 17, 19) reconciled with `RED_TEAM_AUDIT__.md` (Section 8)  
> **Autonomous Scope:** This document is 100% self-contained. You do NOT need to consult external build plans.

---

## 1. Track Objective & Architectural Boundaries

Track D builds the user interface for District Magistrates, Planning Officers, and SIH Hackathon evaluators.
The interface must present complex bitemporal contradictions cleanly, avoid black-box AI claims, and provide navigable **click-to-evidence provenance**.

You will build:
1. **The React 18 + TypeScript + Tailwind CSS Application Shell:** Modern, high-performance GovTech design system with zero external UI bloat.
2. **The District Overview Dashboard:** Key performance metrics (Total Sanctioned Outlay, Tier 1/2/3 breakdown, Average IPI, Anomaly breakdown chart).
3. **The 3-Tier Investigation Queue (`CaseQueue.tsx`):** Filterable table by Risk Tier (Tier 3 Field Action, Tier 2 Desk Review, Tier 1 Auto-Archive), Asset Type, and Status.
4. **The Split-Pane Case Explorer (`CaseDetail.tsx`):**
   - *Left Pane:* Structured fact narrative, lane score cards, baseline vs post-completion metrics, and "Download Statutory Notice (PDF)" button.
   - *Right Pane:* Interactive **D3.js Force-Directed Evidence Graph** (`EvidenceGraph.tsx`).
5. **The Interactive D3.js Evidence Graph Canvas:**
   - Visualizes nodes (`PROJECT`, `SCHOOL`, `STATE`, `CONTRADICTION`, `RULE`) with distinct colors and SVG icons.
   - Supports zoom, pan, node dragging, and node click to inspect raw properties and cryptographic SHA-256 hashes.
6. **The Human Ambiguity Queue (`AmbiguityQueue.tsx`):** Side-by-side card comparison for manual reconciliation of $0.60–0.84$ confidence school matches.
7. **Mock Adapter Mode (`REACT_APP_USE_MOCKS=true`):** Allows frontend development and testing against `contracts/mock_data.json` without requiring a live backend.

---

## 2. File Ownership Boundaries

### ✅ Files You Own & Must Modify:
```
frontend/package.json
frontend/tailwind.config.js
frontend/tsconfig.json
frontend/src/App.tsx
frontend/src/types/index.ts (Mirror of contracts/types.ts)
frontend/src/api/client.ts
frontend/src/api/mockData.ts
frontend/src/components/DistrictOverview.tsx
frontend/src/components/CaseQueue.tsx
frontend/src/components/CaseDetail.tsx
frontend/src/components/EvidenceGraph.tsx
frontend/src/components/AmbiguityQueue.tsx
frontend/src/components/Navbar.tsx
```

### 🚫 Forbidden Files (Must NOT touch):
- `backend/**` (Owned by Tracks A, B, C, E)
- `contracts/**` (Read-only reference)

---

## 3. UI Component Architecture & Layouts

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                   MEEV APP NAVIGATION                                   │
│  [Logo] MEEV Education Validator | [Overview] | [Case Queue (Tier 3: 22)] | [Ambiguity]│
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  [SPLIT-PANE CASE DETAIL VIEW: Case PRJ-2023-04567]                                     │
│  ┌──────────────────────────────────────────┬────────────────────────────────────────┐  │
│  │ LEFT PANE: FACT NARRATIVE & METRICS      │ RIGHT PANE: D3.js EVIDENCE GRAPH       │  │
│  ├──────────────────────────────────────────┼────────────────────────────────────────┤  │
│  │ • Project: PRJ-2023-04567 (₹12.4 Lakh)   │                                        │  │
│  │ • School: GHS Rampur (02120100402)       │       [Project Node]                   │  │
│  │ • IPI Score: 82.0/100 (Tier 3 Alert)     │             │                          │  │
│  │                                          │             ▼                          │  │
│  │ [LANE SCORES]                            │      [School Node]                     │  │
│  │ • Lane 1 Statutory: 0.0 (Eligible)       │       /          \                     │  │
│  │ • Lane 2 Need: 0.45 (SCR: 4.4, -52% Enr) │      ▼            ▼                    │  │
│  │ • Lane 3 Reflection: 0.90 (0 Room Delta) │ [Pre Census]   [Post Census]           │  │
│  │ • Lane 4 Velocity: 0.95 (23 Days vs 45d) │      │            │                    │  │
│  │                                          │      └─────► [Zero Delta Contradict]   │  │
│  │ [INVESTIGATOR ACTION BLOCK]              │                                        │  │
│  │ [Escalate to Field Notice] [Dismiss]     │ (Interactive: Drag / Zoom / Click)     │  │
│  │                                          │                                        │  │
│  │ [DOWNLOAD FORM MPLADS-INSP-1 PDF]        │                                        │  │
│  └──────────────────────────────────────────┴────────────────────────────────────────┘  │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. D3.js Node-Link Visualization Design

### Node Visual Hierarchy:

| Node Type | Fill Color | Border Color | Label Display | Icon / Shape |
| :--- | :--- | :--- | :--- | :--- |
| **`PROJECT`** | `#1e40af` (Navy Blue) | `#1e3a8a` | MPLADS Work ID & Cost | Document Icon / Large Circle ($r=22$) |
| **`SCHOOL`** | `#047857` (Emerald Green) | `#065f46` | School Name & Code | School Building Icon ($r=20$) |
| **`STATE`** | `#0284c7` (Sky Blue) | `#0369a1` | Academic Year Snapshot | Calendar Icon ($r=16$) |
| **`CONTRADICTION`** | `#b91c1c` (Crimson Red) | `#991b1b` | Anomaly Finding | Alert Triangle Icon ($r=20$, Pulsing) |
| **`RULE`** | `#d97706` (Amber Yellow) | `#b45309` | Statutory Guideline | Gavel / Scale Icon ($r=16$) |

### Force Simulation Physics:
- `d3.forceLink().distance(90)`
- `d3.forceManyBody().strength(-300)`
- `d3.forceCenter(width / 2, height / 2)`
- Support `d3.zoom()` with scale extent $[0.3, 3.0]$.

---

## 5. Mock & Live API Integration (`frontend/src/api/client.ts`)

```typescript
import axios from 'axios';
import { InvestigationCaseSummary, InvestigationCaseDetail, D3GraphPayload, DistrictAnalytics } from '../types';
import mockData from '../../../contracts/mock_data.json';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
const USE_MOCKS = process.env.REACT_APP_USE_MOCKS === 'true';

export const apiClient = {
  getCases: async (tier?: number): Promise<InvestigationCaseSummary[]> => {
    if (USE_MOCKS) {
      let cases = mockData.cases as any[];
      if (tier) cases = cases.filter(c => c.risk_tier === tier);
      return cases;
    }
    const res = await axios.get(`${API_BASE}/cases`, { params: { tier } });
    return res.data;
  },

  getCaseDetail: async (caseId: string): Promise<InvestigationCaseDetail> => {
    if (USE_MOCKS) {
      const c = mockData.cases.find(x => x.case_id === caseId) || mockData.cases[0];
      return c as any;
    }
    const res = await axios.get(`${API_BASE}/cases/${caseId}`);
    return res.data;
  },

  getEvidenceGraph: async (caseId: string): Promise<D3GraphPayload> => {
    if (USE_MOCKS) {
      const c = mockData.cases.find(x => x.case_id === caseId) || mockData.cases[0];
      return c.evidence_graph as any;
    }
    const res = await axios.get(`${API_BASE}/cases/${caseId}/evidence-graph`);
    return res.data;
  },

  getDistrictAnalytics: async (): Promise<DistrictAnalytics> => {
    if (USE_MOCKS) {
      return mockData.district_analytics as any;
    }
    const res = await axios.get(`${API_BASE}/analytics/district`);
    return res.data;
  }
};
```

---

## 6. Definition of Done for Track D

- [x] React application compiles cleanly (`npm run build` succeeds).
- [x] 3-tier case queue filters correctly across Tiers 1, 2, and 3.
- [x] D3.js evidence graph renders with zoom/pan and node click inspect modals.
- [x] Ambiguity queue renders side-by-side reconciliation cards.
- [x] Single toggle `REACT_APP_USE_MOCKS=true` allows full offline demo without backend.
- [x] Zero modifications to backend directories.
