# SEMANTIC MRI PIPELINE — PROJECT STATE AUDIT

Version: 3.3
Date: 2026-03-20
Status: Canonical current-state handoff for continuation sessions

This document is the authoritative operational snapshot for the current repository state.

Authority rules:
- This file controls current-state interpretation.
- `RESEARCH_LOG.md` is the canonical chronological session log.
- `audit.md` is supplemental historical workflow and infrastructure history only.
- `docs/BETA_PILOT_EPOCH_PROTOCOL.md` is the active beta pilot methodology for live-manuscript engine testing.
- If any conflict exists between this file and any supplemental document, this file controls unless this file explicitly delegates to the beta pilot protocol for next-study operations.
- All repo-relative paths are assumed to resolve under:

```text
/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
```

- Do not assume a home-directory anchor path is authoritative unless it has been explicitly resolved to the same target.

---

# PROJECT IDENTITY

Project Name  
Semantic MRI of Agricultural Education

Full Title  
A Semantic MRI of Agricultural Education:  
A Longitudinal Audit of Evolutionary Maturation, Methodological Friction, and Innovation Velocity (1960–2026) via High-Dimensional Vector Embeddings

Research Objective  
Measure the semantic evolution of agricultural education research using high-dimensional vector embeddings applied to journal manuscript sections.

Primary Measurements
- semantic dispersion
- innovation velocity
- epoch centroid drift

Corpus
- Journal of Agricultural Education manuscripts

Temporal Scope
- 1960–2026

Epoch Structure
- deterministic 5-year epochs

---

# INGESTION AND YEAR RESOLUTION (POST-DEBUG STABILIZATION)

The system currently operates under a hybrid ingestion model with two canonical routes:

## Route_A_Modern
- file pattern: `data/raw/Route_A_Modern/<YEAR>.pdf`
- year resolution: filename-derived
- example: `2026.pdf → 2026`

## Route_B_Legacy
- file pattern: `data/raw/Route_B_Legacy/<YEAR>/<file>.pdf`
- year resolution: directory-derived
- example: `1960/<file>.pdf → 1960`

## Non-Temporal Artifacts

Some legacy artifacts do not resolve to a valid year (e.g., `Vol1_1.pdf`).

Operational rule:
- such files are **excluded from manifest seeding and downstream processing**
- they are not assigned a sentinel year in persisted artifacts
- exclusion is explicit and logged during pipeline execution

## Current Constraint

Manifest seeding (`seed_manifest_from_raw_pdfs`) still requires a callable year resolver.

A temporary bridge function (`_safe_infer_year`) is used to:
- support both ingestion schemas
- enforce exclusion of non-temporal artifacts

This is a **transitional architecture** and will be removed when manifest-only year resolution is implemented upstream.
---

# COMPUTATIONAL PHILOSOPHY

The pipeline is designed for:
- deterministic computation
- full reproducibility
- transparent mathematics
- auditability
- hardware-aware acceleration
- fail-fast validation at shared contract boundaries

The system intentionally avoids:
- black-box ML pipelines
- opaque vector frameworks
- undocumented tensor math
- silent fallback for route/year/schema drift

Approved scientific libraries for vector math:
- `numpy`
- `scipy.spatial.distance`

---

# HARDWARE ENVIRONMENT

Primary Compute System
- Apple Silicon M3 Max
- 64 GB unified memory

Acceleration

```python
DEVICE = "mps"
```

Embedding Model

```python
MODEL_ID = "nomic-ai/nomic-embed-text-v1.5"
```

Model Properties
- 768-dimensional embeddings
- 8192-token context window
- suitable for long scientific text

Worker Configuration

```python
MAX_WORKERS = 8
```

---

# CURRENT REPOSITORY ARCHITECTURE

```text
JAE_Legacy_Audit
│
├── bins
│   ├── s01_ingest
│   ├── s02_processor
│   ├── s03_analysis
│   └── s04_utils
│
├── data
│   ├── raw
│   ├── raw_pdfs
│   ├── processed
│   ├── structured
│   ├── embeddings
│   ├── metrics
│   ├── manifests
│   └── testing
│
├── docs
├── logs
├── manuscript
├── scripts
├── tests
│
├── config.py
├── main.py
├── pyproject.toml
├── requirements-lock.txt
└── REPO_KEEP_ARCHIVE_MAP.md
```

Utility layer:

```text
bins/s04_utils/
├── artifacts.py
├── manifest_manager.py
├── schemas.py
├── validators.py
└── year_resolution.py
```

Load-bearing utility surfaces:
- `bins/s04_utils/artifacts.py`
- `bins/s04_utils/manifest_manager.py`
- `bins/s04_utils/schemas.py`
- `bins/s04_utils/validators.py`
- `bins/s04_utils/year_resolution.py`

---

# CURRENT IMPLEMENTED STATE

## Phase 1 — Infrastructure
Status: COMPLETE

## Phase 2 — Extraction Pipeline
Status: COMPLETE

Core modules:
- `digital_extract.py`
- `ocr_engine.py`
- `smart_extract.py`
- `cleaning.py`
- `segmenter.py`

## Phase 3 — Structured Export
Status: COMPLETE

Core modules:
- `section_export.py`
- `orchestrator.py`

Implemented behavior:
- canonical top-level section export
- no nested `sections` payloads
- deterministic year resolution delegated to `bins/s04_utils/year_resolution.py`

## Phase 4 — Embedding Engine
Status: COMPLETE

Primary file:
- `bins/s03_analysis/embedder.py`

Embedding bundle contract:
- `doc_id`
- `route`
- `section_labels`
- `embeddings`
- `source_path`

## Phase 5 — Vector Metrics
Status: COMPLETE AND VALIDATED

Primary file:
- `bins/s03_analysis/metrics.py`

Implemented current-state behavior:
- consumes real Phase 4 embedding bundles
- injects `year` via manifest-row join
- does **not** read `year` from embedding bundles
- writes route-level metrics artifacts to:

```text
data/metrics/<route_name>/metrics.npz
```

- marks `metrics_status=success` only after successful artifact persistence and validation

### Post-Phase-5 validation status
Status: IMPLEMENTED AND VERIFIED

Verified build outcomes:
- baseline contract drift repaired in:
  - `bins/s04_utils/artifacts.py`
  - `bins/s04_utils/manifest_manager.py`
  - `bins/s04_utils/schemas.py`
- post-Phase-5 validation functions restored and activated in `bins/s03_analysis/metrics.py`
- regression and validation gates passed for:
  - `tests/test_benchmarks.py`
  - `tests/test_section_exports.py`
  - `tests/test_metrics_contracts.py`
  - `tests/test_metrics_math.py`
  - `tests/test_year_resolution.py`
  - `scripts/startup_check.sh`
  - `scripts/doctor.sh`

### Current verified metrics artifact state
`Route_A_Modern`
- `epoch_count=1`
- `first_epoch=2025-2029`
- `last_epoch=2025-2029`
- `total_section_embeddings=2`
- `source_embedding_file_count=1`
- `innovation_velocity_count=0`
- valid singleton-epoch route artifact

`Route_B_Legacy`
- `epoch_count=1`
- `first_epoch=1960-1964`
- `last_epoch=1960-1964`
- `total_section_embeddings=2`
- `source_embedding_file_count=1`
- `innovation_velocity_count=0`
- valid singleton-epoch route artifact

Manifest state after validation closeout:
- `metrics_success=2`
- `metrics_failed=0`
- `metrics_pending=0`

Interpretation:
- the engine is functioning correctly at the current artifact boundary
- both routes are valid singleton-epoch routes
- empty `innovation_velocity` is currently expected, not erroneous

## Phase 6 — Statistical Inference
Status: NOT STARTED

Expected future location:
- `bins/s03_analysis/statistics.py`

---

# ACTIVE DOCUMENTATION / OPERATIONAL CONTROL STATE

Canonical continuity files:
- `AUDIT_CONTEXT.md` — authoritative current-state handoff
- `RESEARCH_LOG.md` — canonical chronological log
- `audit.md` — historical workflow/infrastructure supplement only

Active beta protocol file:
- `docs/BETA_PILOT_EPOCH_PROTOCOL.md`

---

# CURRENT NEXT STUDY

## Beta Pilot Epoch Study
Status: AUTHORIZED NEXT WORK

This next study is a beta operational validation study, not an inferential historical analysis.

Primary beta objective:
- verify that the live-manuscript engine operates correctly end-to-end on a controlled pilot corpus

Pilot focus:
- manuscript intake under canonical route/year corpus layout
- deterministic year resolution
- manifest integrity
- extraction through Phase 5 execution on live manuscripts
- route-level metrics artifact generation and validation
- epoch realization tracking during larger corpus ingestion

Pilot corpus organization rule:

```text
data/raw_pdfs/<route>/<year>/<filename>.pdf
```

Operational rule:
- manuscripts are grouped by `route` and single resolved `year`
- epochs are derived later from year using fixed 5-year bins
- do not store the active raw corpus by epoch folder
- this beta pilot raw-manuscript layout is a next-study intake rule and does not retroactively alter the already validated benchmark corpus layout used for the existing Phase 2–5 proofs

Allowed route names:
- `Route_A_Modern`
- `Route_B_Legacy`

Project year bounds:
- `1960` through `2026`

---

# MANIFEST-DRIVEN EXECUTION MODEL

Production manifest path:

```text
data/manifests/pipeline_manifest.csv
```

Tracked stage statuses:
- `extract_status`
- `structured_status`
- `embedding_status`
- `metrics_status`

Allowed status values:
- `pending`
- `success`
- `failed`
- `skipped`

Manifest semantics:
- one document row per document under the active study corpus
- stage state is advanced only after successful stage completion
- Phase 5 uses manifest metadata as the authoritative temporal join source

Beta pilot control file:

```text
data/manifests/beta_sample_manifest_template.csv
```

This template governs beta sample selection, intake audit, and promotion decisions for live-manuscript pilot work.

---

# ENGINEERING CORRECTIONS THAT MUST NOT REGRESS

## Section schema normalization
Canonical exported section fields are:
- `A_intro`
- `A_methods`
- `A_results`

Do not reintroduce:
- `A_Intro`
- `A_Methods`
- `A_Results`
- nested `sections` dict payloads

## Legacy compatibility residue
- `data/manifests/pipeline_manifest.csv` remains the authoritative execution table
- any remaining `MASTER_LEDGER` constant is compatibility-only and not the active execution contract
- `bins/s01_ingest/ledger.py` remains helper-only for stable `doc_id` and route derivation
- legacy ingest rebuild orchestration is retired from the active workflow

## Year resolution contract
Resolution precedence:
1. `manifest_row["year"]` when available
2. explicit legacy filename mapping from `data/manifests/legacy_filename_year_map.csv`
3. supported filename parsing from `bins/s04_utils/year_resolution.py`
4. fail fast if unresolved

Operational rules:
- unsupported filenames must not silently guess a year
- manifest year remains authoritative when available

## Beta pilot contract
Operational rules:
- pilot manuscripts must live under `data/raw_pdfs/<route>/<year>/`
- each manuscript must resolve to exactly one route and one year
- unresolved or conflicting items must be quarantined, not silently admitted
- beta pilot execution is correctness- and integrity-focused, not inferential
- full-scale claims remain disallowed until epoch coverage expands beyond singleton-route realization

---

# PHASE 6 FRAMING

## What is currently supported
- descriptive reporting
- route/year/epoch coverage reporting
- intake audit summaries
- route-level metrics artifact summaries
- validation-driven engine correctness reporting
- beta pilot execution on live manuscripts

## What is not yet substantively supported
- inferential statistics about temporal change
- cross-epoch innovation trajectory claims
- strong historical semantic trend interpretation

Phase 6 decision rule:
- if larger live-manuscript ingestion yields multi-epoch coverage within one or both routes, Phase 6 can expand beyond descriptive readiness work
- if routes remain singleton-epoch after pilot ingestion, Phase 6 should remain descriptive/readiness-oriented

---

# SESSION-CLOSE RESUME POINT

Next work should begin from:
- beta pilot epoch study execution using live manuscripts
- corpus staging under canonical `route/year` organization
- intake audit of newly captured manuscripts
- rerun of Phases 2–5 on the expanded corpus
- revalidation of route-level metrics artifacts after corpus expansion
- decision on whether expanded epoch coverage justifies broader Phase 6 analysis

# SEMANTIC MRI PIPELINE — PROJECT STATE AUDIT

Version: 3.2
Date: 2026-03-20
Status: Canonical current-state handoff for continuation sessions

This document is the authoritative operational snapshot for the current repository state.

Authority rules:
- This file controls current-state interpretation.
- `audit.md` is supplemental historical workflow and infrastructure history only.
- If any conflict exists between this file and `audit.md`, this file controls.
- All repo-relative paths are assumed to resolve under:

```text
/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
```

- Do not assume a home-directory anchor path is authoritative unless it has been explicitly resolved to the same target.

---

# CURRENT IMPLEMENTED STATE

## Phases 1–5
Status: COMPLETE

Phase 5 remains complete and validated. Post-Phase-5 validation remains implemented and active.

Current route-level metrics artifact state:
- `Route_A_Modern` is valid and currently singleton-epoch
- `Route_B_Legacy` is valid and currently singleton-epoch

Phase 6 is still not a full inferential workstream under the current realized epoch coverage.

---

# BETA ACQUISITION STATUS

## Modern acquisition
Status: WORKING

Observed beta result:
- 9/9 confirmed modern sample rows succeeded
- `LEGACY_CUTOFF=2000` route boundary behaved correctly
- no modern runner crashes or download failures occurred in the validated beta sample

## Legacy acquisition
Status: PARTIALLY WORKING

Observed beta result:
- 2/2 confirmed legacy rows with resolvable OJS article IDs succeeded
- the unresolved JAATEA-era failures were upstream prefill/discovery failures, not runner failures

Current blocker:
- legacy discovery/prefill remains the narrow bottleneck
- the validated runner can only process rows that already have a resolvable article page or PDF target

Operational interpretation:
- the download engine is not the primary failure surface
- the remaining bottleneck is upstream metadata/prefill completion for legacy rows

---

# ACQUISITION STRATEGY

The active acquisition strategy is now hybrid and batch-oriented.

## Acquisition front end
A dedicated legacy acquisition layer now exists conceptually as a standalone front end to the stabilized engine.

Its purpose is to:
1. harvest candidate metadata by year range
2. write a structured prefill queue
3. support manual confirmation of unresolved rows
4. download confirmed rows into staging
5. promote approved rows into canonical raw manuscript storage
6. bridge promoted files into `data/manifests/pipeline_manifest.csv`

This acquisition layer is intentionally separate from the load-bearing pipeline utility layer.

## Active acquisition boundaries
- metadata harvesting and prefill are upstream of the core engine
- downloader/promotion/manifest-bridge tasks are operational intake tasks
- Phases 2–5 remain the validated downstream engine

## Canonical manuscript storage remains
```text
data/raw_pdfs/<route>/<year>/<filename>.pdf
```

Route/year organization remains authoritative. Epoch folders are not valid manuscript storage.

---

# CURRENT NEXT WORK

The active next workstream is not a core-engine rebuild.

The active next workstream is:

1. batch legacy metadata prefill
2. controlled legacy PDF acquisition
3. staged-to-canonical promotion
4. manifest integration
5. rerun of Phases 2–5 on the expanded corpus
6. post-Phase-5 validation of regenerated route-level metrics artifacts

Phase 6 remains downstream of successful legacy corpus expansion.

---

# RECOVERY / WORKLOAD CONTROL

The core engine is now treated as frozen except for blocker fixes.

Delegated or semi-delegated work:
- manuscript identification
- raw PDF acquisition
- intake queue confirmation
- staging and batch QC

Owner-controlled work:
- final QC
- manifest integration
- pipeline execution
- artifact validation
- documentation closeout
- Phase 6 readiness decisions

This remains the official recovery model for preventing the project from expanding into an unbounded simultaneous scraper/engine/study workload.

# SEMANTIC MRI PIPELINE — PROJECT STATE AUDIT

Version: 3.4
Date: 2026-03-21
Status: Canonical current-state handoff for continuation sessions

This document is the authoritative operational snapshot for the current repository state.

Authority rules:
- This file controls current-state interpretation.
- `RESEARCH_LOG.md` is the canonical chronological session log.
- `audit.md` is supplemental historical workflow and infrastructure history only.
- `docs/BETA_PILOT_EPOCH_PROTOCOL.md` is the active beta pilot methodology for live-manuscript engine testing.
- If any conflict exists between this file and any supplemental document, this file controls unless this file explicitly delegates to the beta pilot protocol for next-study operations.
- All repo-relative paths are assumed to resolve under:

```text
/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
```

- Do not assume a home-directory anchor path is authoritative unless it has been explicitly resolved to the same target.

---

# PROJECT IDENTITY

Project Name  
Semantic MRI of Agricultural Education

Full Title  
A Semantic MRI of Agricultural Education:  
A Longitudinal Audit of Evolutionary Maturation, Methodological Friction, and Innovation Velocity (1960–2026) via High-Dimensional Vector Embeddings

Research Objective  
Measure the semantic evolution of agricultural education research using high-dimensional vector embeddings applied to journal manuscript sections.

Primary Measurements
- semantic dispersion
- innovation velocity
- epoch centroid drift

Corpus
- Journal of Agricultural Education manuscripts

Temporal Scope
- 1960–2026

Epoch Structure
- deterministic 5-year epochs

---

# COMPUTATIONAL PHILOSOPHY

The pipeline is designed for:
- deterministic computation
- full reproducibility
- transparent mathematics
- auditability
- hardware-aware acceleration
- fail-fast validation at shared contract boundaries

The system intentionally avoids:
- black-box ML pipelines
- opaque vector frameworks
- undocumented tensor math
- silent fallback for route/year/schema drift

Approved scientific libraries for vector math:
- `numpy`
- `scipy.spatial.distance`

---

# HARDWARE ENVIRONMENT

Primary Compute System
- Apple Silicon M3 Max
- 64 GB unified memory

Acceleration

```python
DEVICE = "mps"
```

Embedding Model

```python
MODEL_ID = "nomic-ai/nomic-embed-text-v1.5"
```

Model Properties
- 768-dimensional embeddings
- 8192-token context window
- suitable for long scientific text

Worker Configuration

```python
MAX_WORKERS = 8
```

---

# CURRENT REPOSITORY ARCHITECTURE

```text
JAE_Legacy_Audit
│
├── bins
│   ├── s01_ingest
│   ├── s02_processor
│   ├── s03_analysis
│   └── s04_utils
│
├── data
│   ├── raw
│   ├── raw_pdfs
│   ├── processed
│   ├── structured
│   ├── embeddings
│   ├── metrics
│   ├── manifests
│   └── testing
│
├── docs
├── logs
├── manuscript
├── scripts
├── tests
│
├── config.py
├── main.py
├── pyproject.toml
├── requirements-lock.txt
└── REPO_KEEP_ARCHIVE_MAP.md
```

Utility layer:

```text
bins/s04_utils/
├── artifacts.py
├── manifest_manager.py
├── schemas.py
├── validators.py
└── year_resolution.py
```

Load-bearing utility surfaces:
- `bins/s04_utils/artifacts.py`
- `bins/s04_utils/manifest_manager.py`
- `bins/s04_utils/schemas.py`
- `bins/s04_utils/validators.py`
- `bins/s04_utils/year_resolution.py`

---

# CURRENT IMPLEMENTED STATE

## Phase 1 — Infrastructure
Status: COMPLETE

## Phase 2 — Extraction Pipeline
Status: COMPLETE

Core modules:
- `digital_extract.py`
- `ocr_engine.py`
- `smart_extract.py`
- `cleaning.py`
- `segmenter.py`

## Phase 3 — Structured Export
Status: COMPLETE

Core modules:
- `section_export.py`
- `orchestrator.py`

Implemented behavior:
- canonical top-level section export
- no nested `sections` payloads
- deterministic year resolution delegated to `bins/s04_utils/year_resolution.py`

## Phase 4 — Embedding Engine
Status: COMPLETE

Primary file:
- `bins/s03_analysis/embedder.py`

Embedding bundle contract:
- `doc_id`
- `route`
- `section_labels`
- `embeddings`
- `source_path`

## Phase 5 — Vector Metrics
Status: COMPLETE AND VALIDATED

Primary file:
- `bins/s03_analysis/metrics.py`

Implemented current-state behavior:
- consumes real Phase 4 embedding bundles
- injects `year` via manifest-row join
- does **not** read `year` from embedding bundles
- writes route-level metrics artifacts to:

```text
data/metrics/<route_name>/metrics.npz
```

- marks `metrics_status=success` only after successful artifact persistence and validation

### Post-Phase-5 validation status
Status: IMPLEMENTED AND VERIFIED

Verified build outcomes:
- baseline contract drift repaired in:
  - `bins/s04_utils/artifacts.py`
  - `bins/s04_utils/manifest_manager.py`
  - `bins/s04_utils/schemas.py`
- post-Phase-5 validation functions restored and activated in `bins/s03_analysis/metrics.py`
- regression and validation gates passed for:
  - `tests/test_benchmarks.py`
  - `tests/test_section_exports.py`
  - `tests/test_metrics_contracts.py`
  - `tests/test_metrics_math.py`
  - `tests/test_year_resolution.py`
  - `scripts/startup_check.sh`
  - `scripts/doctor.sh`

### Current verified metrics artifact state
`Route_A_Modern`
- `epoch_count=1`
- `first_epoch=2025-2029`
- `last_epoch=2025-2029`
- `total_section_embeddings=2`
- `source_embedding_file_count=1`
- `innovation_velocity_count=0`
- valid singleton-epoch route artifact

`Route_B_Legacy`
- `epoch_count=1`
- `first_epoch=1960-1964`
- `last_epoch=1960-1964`
- `total_section_embeddings=2`
- `source_embedding_file_count=1`
- `innovation_velocity_count=0`
- valid singleton-epoch route artifact

Manifest state after validation closeout:
- `metrics_success=2`
- `metrics_failed=0`
- `metrics_pending=0`

Interpretation:
- the engine is functioning correctly at the current artifact boundary
- both routes are valid singleton-epoch routes
- empty `innovation_velocity` is currently expected, not erroneous

## Phase 6 — Statistical Inference
Status: NOT STARTED

Expected future location:
- `bins/s03_analysis/statistics.py`

---

# ACTIVE DOCUMENTATION / OPERATIONAL CONTROL STATE

Canonical continuity files:
- `AUDIT_CONTEXT.md` — authoritative current-state handoff
- `RESEARCH_LOG.md` — canonical chronological log
- `audit.md` — historical workflow/infrastructure supplement only

Active beta protocol file:
- `docs/BETA_PILOT_EPOCH_PROTOCOL.md`

---

# CURRENT NEXT STUDY

## Beta Pilot Epoch Study
Status: AUTHORIZED NEXT WORK

This next study is a beta operational validation study, not an inferential historical analysis.

Primary beta objective:
- verify that the live-manuscript engine operates correctly end-to-end on a controlled pilot corpus

Pilot focus:
- manuscript intake under canonical route/year corpus layout
- deterministic year resolution
- manifest integrity
- extraction through Phase 5 execution on live manuscripts
- route-level metrics artifact generation and validation
- epoch realization tracking during larger corpus ingestion

Pilot corpus organization rule:

```text
data/raw_pdfs/<route>/<year>/<filename>.pdf
```

Operational rule:
- manuscripts are grouped by `route` and single resolved `year`
- epochs are derived later from year using fixed 5-year bins
- do not store the active raw corpus by epoch folder
- this beta pilot raw-manuscript layout is a next-study intake rule and does not retroactively alter the already validated benchmark corpus layout used for the existing Phase 2–5 proofs

Allowed route names:
- `Route_A_Modern`
- `Route_B_Legacy`

Project year bounds:
- `1960` through `2026`

---

# MANIFEST-DRIVEN EXECUTION MODEL

Production manifest path:

```text
data/manifests/pipeline_manifest.csv
```

Tracked stage statuses:
- `extract_status`
- `structured_status`
- `embedding_status`
- `metrics_status`

Allowed status values:
- `pending`
- `success`
- `failed`
- `skipped`

Manifest semantics:
- one document row per document under the active study corpus
- stage state is advanced only after successful stage completion
- Phase 5 uses manifest metadata as the authoritative temporal join source

Beta pilot control file:

```text
data/manifests/beta_sample_manifest_template.csv
```

This template governs beta sample selection, intake audit, and promotion decisions for live-manuscript pilot work.

---

# ENGINEERING CORRECTIONS THAT MUST NOT REGRESS

## Section schema normalization
Canonical exported section fields are:
- `A_intro`
- `A_methods`
- `A_results`

Do not reintroduce:
- `A_Intro`
- `A_Methods`
- `A_Results`
- nested `sections` dict payloads

## Legacy compatibility residue
- `data/manifests/pipeline_manifest.csv` remains the authoritative execution table
- any remaining `MASTER_LEDGER` constant is compatibility-only and not the active execution contract
- `bins/s01_ingest/ledger.py` remains helper-only for stable `doc_id` and route derivation
- legacy ingest rebuild orchestration is retired from the active workflow

## Year resolution contract
Resolution precedence:
1. `manifest_row["year"]` when available
2. explicit legacy filename mapping from `data/manifests/legacy_filename_year_map.csv`
3. supported filename parsing from `bins/s04_utils/year_resolution.py`
4. fail fast if unresolved

Operational rules:
- unsupported filenames must not silently guess a year
- manifest year remains authoritative when available

## Beta pilot contract
Operational rules:
- pilot manuscripts must live under `data/raw_pdfs/<route>/<year>/`
- each manuscript must resolve to exactly one route and one year
- unresolved or conflicting items must be quarantined, not silently admitted
- beta pilot execution is correctness- and integrity-focused, not inferential
- full-scale claims remain disallowed until epoch coverage expands beyond singleton-route realization

---

# PHASE 6 FRAMING

## What is currently supported
- descriptive reporting
- route/year/epoch coverage reporting
- intake audit summaries
- route-level metrics artifact summaries
- validation-driven engine correctness reporting
- beta pilot execution on live manuscripts

## What is not yet substantively supported
- inferential statistics about temporal change
- cross-epoch innovation trajectory claims
- strong historical semantic trend interpretation

Phase 6 decision rule:
- if larger live-manuscript ingestion yields multi-epoch coverage within one or both routes, Phase 6 can expand beyond descriptive readiness work
- if routes remain singleton-epoch after pilot ingestion, Phase 6 should remain descriptive/readiness-oriented

---

# LEGACY ACQUISITION EXECUTION STATUS

## Current live acquisition layer
Status: WORKING FOR THE 1960–1969 LEGACY BATCH

Active code location:

```text
legacy_acquisition/
```

Current executed acquisition workflow:
1. metadata prefill queue generation
2. row-level confirmation
3. controlled downloader
4. staged PDF promotion
5. manifest bridge into `data/manifests/pipeline_manifest.csv`

## Executed 1960–1969 batch result
Verified completed batch:
- 149 legacy PDFs downloaded into staging
- 149 legacy PDFs promoted into the live raw corpus under:
  - `data/raw/Route_B_Legacy/<year>/...`
- 149 manifest rows added to:
  - `data/manifests/pipeline_manifest.csv`

Operational result:
- legacy acquisition is no longer the blocker for the 1960–1969 decade batch
- this batch is now ready for downstream processing through the stabilized Phase 2–5 engine

## Current storage/path interpretation
The executed legacy batch is now operating through the live corpus path:

```text
data/raw/<route>/<year>/<filename>.pdf
```

Historical note:
- earlier beta-protocol and acquisition-build docs referenced `data/raw_pdfs/<route>/<year>/...`
- that path should now be treated as historical/protocol planning residue unless explicitly reactivated
- the actual successful 1960–1969 batch was promoted into `data/raw/`

## Current blocker status
The previous narrow blocker in legacy acquisition was repaired:
- OJS `/article/download/...` URLs are now handled as direct download targets rather than as landing pages requiring PDF-link discovery

## Immediate next work
The next active workstream is now:
1. run extraction on the new 1960–1969 legacy rows
2. run structured section export
3. run section embeddings
4. regenerate Phase 5 route-level metrics artifacts
5. rerun post-Phase-5 validation
6. reassess legacy epoch realization and Phase 6 readiness


---

# SESSION-CLOSE RESUME POINT

Next work should begin from:
- beta pilot epoch study execution using live manuscripts
- corpus staging under canonical `route/year` organization
- intake audit of newly captured manuscripts
- rerun of Phases 2–5 on the expanded corpus
- revalidation of route-level metrics artifacts after corpus expansion
- decision on whether expanded epoch coverage justifies broader Phase 6 analysis

# SEMANTIC MRI PIPELINE — PROJECT STATE AUDIT

Version: 3.2
Date: 2026-03-20
Status: Canonical current-state handoff for continuation sessions

This document is the authoritative operational snapshot for the current repository state.

Authority rules:
- This file controls current-state interpretation.
- `audit.md` is supplemental historical workflow and infrastructure history only.
- If any conflict exists between this file and `audit.md`, this file controls.
- All repo-relative paths are assumed to resolve under:

```text
/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
```

- Do not assume a home-directory anchor path is authoritative unless it has been explicitly resolved to the same target.

---

# CURRENT IMPLEMENTED STATE

## Phases 1–5
Status: COMPLETE

Phase 5 remains complete and validated. Post-Phase-5 validation remains implemented and active.

Current route-level metrics artifact state:
- `Route_A_Modern` is valid and currently singleton-epoch
- `Route_B_Legacy` is valid and currently singleton-epoch

Phase 6 is still not a full inferential workstream under the current realized epoch coverage.

---

# BETA ACQUISITION STATUS

## Modern acquisition
Status: WORKING

Observed beta result:
- 9/9 confirmed modern sample rows succeeded
- `LEGACY_CUTOFF=2000` route boundary behaved correctly
- no modern runner crashes or download failures occurred in the validated beta sample

## Legacy acquisition
Status: PARTIALLY WORKING

Observed beta result:
- 2/2 confirmed legacy rows with resolvable OJS article IDs succeeded
- the unresolved JAATEA-era failures were upstream prefill/discovery failures, not runner failures

Current blocker:
- legacy discovery/prefill remains the narrow bottleneck
- the validated runner can only process rows that already have a resolvable article page or PDF target

Operational interpretation:
- the download engine is not the primary failure surface
- the remaining bottleneck is upstream metadata/prefill completion for legacy rows

---

# ACQUISITION STRATEGY

The active acquisition strategy is now hybrid and batch-oriented.

## Acquisition front end
A dedicated legacy acquisition layer now exists conceptually as a standalone front end to the stabilized engine.

Its purpose is to:
1. harvest candidate metadata by year range
2. write a structured prefill queue
3. support manual confirmation of unresolved rows
4. download confirmed rows into staging
5. promote approved rows into canonical raw manuscript storage
6. bridge promoted files into `data/manifests/pipeline_manifest.csv`

This acquisition layer is intentionally separate from the load-bearing pipeline utility layer.

## Active acquisition boundaries
- metadata harvesting and prefill are upstream of the core engine
- downloader/promotion/manifest-bridge tasks are operational intake tasks
- Phases 2–5 remain the validated downstream engine

## Canonical manuscript storage remains
```text
data/raw_pdfs/<route>/<year>/<filename>.pdf
```

Route/year organization remains authoritative. Epoch folders are not valid manuscript storage.

---

# CURRENT NEXT WORK

The active next workstream is not a core-engine rebuild.

The active next workstream is:

1. batch legacy metadata prefill
2. controlled legacy PDF acquisition
3. staged-to-canonical promotion
4. manifest integration
5. rerun of Phases 2–5 on the expanded corpus
6. post-Phase-5 validation of regenerated route-level metrics artifacts

Phase 6 remains downstream of successful legacy corpus expansion.

---

# RECOVERY / WORKLOAD CONTROL

The core engine is now treated as frozen except for blocker fixes.

Delegated or semi-delegated work:
- manuscript identification
- raw PDF acquisition
- intake queue confirmation
- staging and batch QC

Owner-controlled work:
- final QC
- manifest integration
- pipeline execution
- artifact validation
- documentation closeout
- Phase 6 readiness decisions

This remains the official recovery model for preventing the project from expanding into an unbounded simultaneous scraper/engine/study workload.

## 2026-03-22 — Pipeline Stabilization Audit Reference

The Bin 02 → Bin 05 pipeline has been stabilized and validated for the
1960–1969 legacy corpus.

Key outcomes:
- Structured export, embeddings, and metrics are fully operational
- Embedding schema aligned with metrics contract
- Metrics aggregation validated across two epochs (1960–1964, 1965–1969)
- Cardinality invariant satisfied (149 structured / 149 embeddings)
- Non-temporal artifacts excluded from pipeline

A complete engineering record of the debugging process, root causes, file-level
changes, and validation evidence is documented in:

→ `DEBUGGING_AUDIT_2026-03-22.md`

This file is the authoritative record of pipeline stabilization and should be
consulted for any future refactoring, extension, or audit review.