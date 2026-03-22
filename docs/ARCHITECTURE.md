# System Architecture

## Semantic MRI of Agricultural Education Pipeline

Platform: Apple Silicon (M3 Max)
Version: 2.2
Date: 2026-03-20
Status: Supplemental architecture reference aligned to the stabilized Phase 5 repo state and the active beta pilot epoch protocol

---

# 1. Architectural Overview

The repository implements a modular computational architecture for deterministic semantic analysis of historical agricultural education manuscripts.

The implemented operational phases are:
1. extraction and cleaning
2. segmentation and structured export
3. section embedding generation
4. route-level vector metrics

A future Phase 6 statistical layer is anticipated but not yet implemented.

Acquisition is architecturally adjacent to the active analysis runtime surface, but the next-study intake boundary is now explicitly defined by the beta pilot protocol.

---

# 2. Operational Root and Path Policy

The authoritative working root for this project is:

```text
/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
```

Operational rule:
- work from the NVMe path above
- do not treat a home-directory mirror or anchor path as authoritative unless explicitly verified as the same resolved target

---

# 3. Execution Model

The repository contains a root orchestrator:

```text
main.py
```

Current active phases exposed there are:
- `process`
- `analyze`

Legacy ingest rebuild orchestration is retired from the active surface.

Direct stage-level execution is also used for deterministic validation and closeout where appropriate.

---

# 4. Service Bin Architecture

```text
bins/
│
├── s01_ingest
├── s02_processor
├── s03_analysis
└── s04_utils
```

Roles:
- `s01_ingest` — legacy compatibility helpers only; active ingest rebuild orchestration has been retired/archived
- `s02_processor` — extraction, OCR, cleaning, segmentation
- `s03_analysis` — structured export, embedding generation, metrics
- `s04_utils` — shared schemas, validators, artifact classes, manifest management, year resolution

Architectural note:
- the current operational path is manifest-driven
- the active analysis pipeline does not rely on the retired legacy ledger rebuild orchestrator

---

# 5. Data Architecture

All persisted artifacts are stored under `data/`.

Roles:
- `raw/` — existing validated benchmark / production inputs
- `raw_pdfs/` — active next-study beta pilot raw-manuscript intake organized by `route/year`
- `processed/` — cleaned text intermediates
- `structured/` — canonical structured JSON exports
- `embeddings/` — validated section embedding bundles
- `metrics/` — route-level metrics artifacts
- `manifests/` — execution-tracking metadata and beta pilot control manifests
- `testing/` — isolated non-production validation corpus

Important distinction:
- `raw/` remains part of the validated benchmark and stable analysis spine
- `raw_pdfs/` is the next-study expansion layout for live manuscripts

---

# 6. Current Analysis-Layer Architecture

## Phase 3 — Structured Export
Primary files:
- `bins/s03_analysis/section_export.py`
- `bins/s03_analysis/orchestrator.py`

Contract:
- flattened top-level JSON export
- canonical fields include `A_intro`, `A_methods`, and `A_results`
- nested `sections` payloads are invalid current state
- year resolution is delegated to `bins/s04_utils/year_resolution.py`

## Phase 4 — Embedding Generation
Primary file:
- `bins/s03_analysis/embedder.py`

## Phase 5 — Route-Level Metrics
Primary file:
- `bins/s03_analysis/metrics.py`

Contract:
- consumes validated Phase 4 embedding bundles
- injects `year` through manifest-row join
- writes route-level outputs to `data/metrics/<route_name>/metrics.npz`
- advances `metrics_status` only after successful artifact persistence and validation

---

# 7. Beta Pilot Intake Architecture

The active next-study intake rule is documented in `docs/BETA_PILOT_EPOCH_PROTOCOL.md`.

Required raw-manuscript layout:

```text
data/raw_pdfs/<route>/<year>/<filename>.pdf
```

Required pilot control manifest:
- `data/manifests/beta_sample_manifest_template.csv`

Operational rules:
- one resolved route per manuscript
- one resolved year per manuscript
- unresolved/conflicting items are quarantined, not silently admitted
- epoch assignment is derived later from year during analysis

This is a beta study protocol, not yet a claim that full intake has been executed.

---

# 8. Shared Utility Architecture

```text
bins/s04_utils/
├── artifacts.py
├── manifest_manager.py
├── schemas.py
├── validators.py
└── year_resolution.py
```

Responsibilities:
- `schemas.py` — canonical constants and shared identifiers
- `validators.py` — schema and payload validation helpers
- `artifacts.py` — typed artifact boundaries
- `manifest_manager.py` — stage-state tracking and manifest interactions
- `year_resolution.py` — deterministic year resolution and legacy filename mapping support

---

# 9. Infrastructure Validation

Active scripts include:
- `scripts/startup_check.sh`
- `scripts/doctor.sh`
- `scripts/research_snapshot.sh`

Validation goals:
- verify the NVMe-backed working environment
- validate core filesystem expectations
- prevent execution under invalid infrastructure state
- reduce drift between documentation, artifacts, and runtime assumptions

---

# 10. Current Status

Implemented and complete:
- extraction pipeline
- structured export
- section embedding generation
- Phase 5 route-level metrics execution
- deterministic year-resolution contract
- post-Phase-5 validation hardening

Defined and authorized next:
- beta pilot epoch study using live manuscripts
- corpus intake under canonical `route/year` organization
- rerun of Phases 2–5 on expanded corpus

Not yet implemented:
- Phase 6 statistical inference

# System Architecture

## Semantic MRI of Agricultural Education Pipeline

Platform: Apple Silicon (M3 Max)
Version: 2.2
Date: 2026-03-20
Status: Supplemental architecture reference aligned to the stabilized Phase 5 repo state and the active beta pilot epoch protocol

---

# 1. Architectural Overview

The repository implements a modular computational architecture for deterministic semantic analysis of historical agricultural education manuscripts.

The implemented operational phases are:
1. extraction and cleaning
2. segmentation and structured export
3. section embedding generation
4. route-level vector metrics

A future Phase 6 statistical layer is anticipated but not yet implemented.

Acquisition is architecturally adjacent to the active analysis runtime surface, but the next-study intake boundary is now explicitly defined by the beta pilot protocol.

---

# 2. Operational Root and Path Policy

The authoritative working root for this project is:

```text
/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
```

Operational rule:
- work from the NVMe path above
- do not treat a home-directory mirror or anchor path as authoritative unless explicitly verified as the same resolved target

---

# 3. Execution Model

The repository contains a root orchestrator:

```text
main.py
```

Current active phases exposed there are:
- `process`
- `analyze`

Legacy ingest rebuild orchestration is retired from the active surface.

Direct stage-level execution is also used for deterministic validation and closeout where appropriate.

---

# 4. Service Bin Architecture

```text
bins/
│
├── s01_ingest
├── s02_processor
├── s03_analysis
└── s04_utils
```

Roles:
- `s01_ingest` — legacy compatibility helpers only; active ingest rebuild orchestration has been retired/archived
- `s02_processor` — extraction, OCR, cleaning, segmentation
- `s03_analysis` — structured export, embedding generation, metrics
- `s04_utils` — shared schemas, validators, artifact classes, manifest management, year resolution

Architectural note:
- the current operational path is manifest-driven
- the active analysis pipeline does not rely on the retired legacy ledger rebuild orchestrator

---

# 5. Data Architecture

All persisted artifacts are stored under `data/`.

Roles:
- `raw/` — active validated manuscript corpus and current live intake destination
- `raw_pdfs/` — historical/protocol beta-planning path; not the active executed intake destination in the current live tree
- `processed/` — cleaned text intermediates
- `structured/` — canonical structured JSON exports
- `embeddings/` — validated section embedding bundles
- `metrics/` — route-level metrics artifacts
- `manifests/` — execution-tracking metadata and beta pilot control manifests
- `testing/` — isolated non-production validation corpus

Important distinction:
- `raw/` remains part of the validated benchmark and stable analysis spine
- `raw_pdfs/` is the next-study expansion layout for live manuscripts

---

# 6. Current Analysis-Layer Architecture

## Phase 3 — Structured Export
Primary files:
- `bins/s03_analysis/section_export.py`
- `bins/s03_analysis/orchestrator.py`

Contract:
- flattened top-level JSON export
- canonical fields include `A_intro`, `A_methods`, and `A_results`
- nested `sections` payloads are invalid current state
- year resolution is delegated to `bins/s04_utils/year_resolution.py`

## Phase 4 — Embedding Generation
Primary file:
- `bins/s03_analysis/embedder.py`

## Phase 5 — Route-Level Metrics
Primary file:
- `bins/s03_analysis/metrics.py`

Contract:
- consumes validated Phase 4 embedding bundles
- injects `year` through manifest-row join
- writes route-level outputs to `data/metrics/<route_name>/metrics.npz`
- advances `metrics_status` only after successful artifact persistence and validation

---

# 7. Beta Pilot Intake Architecture

The active next-study intake rule is documented in `docs/BETA_PILOT_EPOCH_PROTOCOL.md`.

Current executed raw-manuscript layout:

```text
data/raw/<route>/<year>/<filename>.pdf
```

Historical note:
- earlier pilot protocol documents referenced `data/raw_pdfs/<route>/<year>/<filename>.pdf`
- the executed 1960–1969 legacy acquisition batch was promoted into `data/raw/`

Required pilot control manifest:
- `data/manifests/beta_sample_manifest_template.csv`

Operational rules:
- one resolved route per manuscript
- one resolved year per manuscript
- unresolved/conflicting items are quarantined, not silently admitted
- epoch assignment is derived later from year during analysis

This beta study protocol has now advanced into executed intake for the 1960–1969 legacy batch.

Current live acquisition code location:

```text
legacy_acquisition/
```

---

# 8. Shared Utility Architecture

```text
bins/s04_utils/
├── artifacts.py
├── manifest_manager.py
├── schemas.py
├── validators.py
└── year_resolution.py
```

Responsibilities:
- `schemas.py` — canonical constants and shared identifiers
- `validators.py` — schema and payload validation helpers
- `artifacts.py` — typed artifact boundaries
- `manifest_manager.py` — stage-state tracking and manifest interactions
- `year_resolution.py` — deterministic year resolution and legacy filename mapping support

---

# 9. Infrastructure Validation

Active scripts include:
- `scripts/startup_check.sh`
- `scripts/doctor.sh`
- `scripts/research_snapshot.sh`

Validation goals:
- verify the NVMe-backed working environment
- validate core filesystem expectations
- prevent execution under invalid infrastructure state
- reduce drift between documentation, artifacts, and runtime assumptions

---

# 10. Current Status

Implemented and complete:
- extraction pipeline
- structured export
- section embedding generation
- Phase 5 route-level metrics execution
- deterministic year-resolution contract
- post-Phase-5 validation hardening

Defined and authorized next:
- beta pilot epoch study using live manuscripts
- corpus intake under canonical `route/year` organization
- rerun of Phases 2–5 on expanded corpus

Not yet implemented:
- Phase 6 statistical inference


---

# 11. Legacy Acquisition Execution Update

Executed and verified:
- 149 legacy PDFs were downloaded and promoted for the 1960–1969 batch
- promoted files now live under `data/raw/Route_B_Legacy/<year>/`
- 149 rows were bridged into `data/manifests/pipeline_manifest.csv`

Architectural implication:
- the acquisition layer is now an active operational front end, not only a planned extension
- the next architectural transition point is downstream processing of the expanded legacy corpus through the stabilized Phases 2–5

---

# HYBRID YEAR RESOLUTION LAYER (TRANSITIONAL)

The system currently implements a temporary hybrid year resolution layer.

Purpose:
- support legacy corpus ingestion without fully normalized metadata

Mechanism:
- `_safe_infer_year(Path) -> int`
- resolves year from:
  - directory structure (legacy)
  - filename (modern)

Limitations:
- relies on path structure rather than manifest authority
- introduces coupling between filesystem layout and semantic metadata

Future target state:
- remove path-based inference entirely
- enforce manifest-only year resolution
- require all ingestion to pass through validated metadata layer

---
