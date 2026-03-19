# SEMANTIC MRI PIPELINE — PROJECT STATE AUDIT

Version: 3.1
Date: 2026-03-19
Status: Canonical current-state handoff for continuation sessions

This document is the authoritative operational snapshot for the current repository state.

Authority rules:
- This file controls current-state interpretation.
- `RESEARCH_LOG.md` is the canonical chronological session log.
- `audit.md` is supplemental historical workflow and infrastructure history only.
- If any conflict exists between this file and any supplemental document, this file controls.
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

The system intentionally avoids:
- black-box ML pipelines
- opaque vector frameworks
- undocumented tensor math

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
└── pyproject.toml
```

Utility layer:

```text
bins/s04_utils/
├── __init__.py
├── artifacts.py
├── manifest_manager.py
├── schemas.py
├── validators.py
└── year_resolution.py
```

---

# CURRENT IMPLEMENTED STATE

## Phase 1 — Infrastructure
Status: COMPLETE

Includes:
- repository architecture
- root configuration
- startup validation
- deterministic directory layout
- NVMe-backed project storage

## Phase 2 — Extraction Pipeline
Status: COMPLETE

Location

```text
bins/s02_processor/
```

Core modules
- `digital_extract.py`
- `ocr_engine.py`
- `smart_extract.py`
- `cleaning.py`
- `segmenter.py`

Capabilities
- digital text extraction
- OCR fallback
- reference truncation
- era-aware segmentation

Reference truncation stops at:
- References
- Literature Cited
- Acknowledgements
- Funding

## Phase 3 — Structured Export
Status: COMPLETE

Location

```text
bins/s03_analysis/
```

Core modules
- `section_export.py`
- `orchestrator.py`

Purpose
- convert manuscripts into structured JSON artifacts
- export canonical top-level section fields
- prevent nested `sections` payload drift

Current year-resolution behavior
- `section_export.py` no longer uses benchmark-only hardcoded filename special cases
- year resolution is delegated to `bins/s04_utils/year_resolution.py`

## Phase 4 — Embedding Engine
Status: COMPLETE

Location

```text
bins/s03_analysis/embedder.py
```

Purpose
- load structured JSON artifacts
- embed real manuscript sections
- write validated embedding bundles to route-specific `.npz` outputs

## Phase 5 — Vector Metrics
Status: COMPLETE

Location

```text
bins/s03_analysis/metrics.py
```

Implemented current-state behavior
- consumes real Phase 4 embedding bundles with keys:
  - `doc_id`
  - `route`
  - `section_labels`
  - `embeddings`
  - `source_path`
- injects `year` via manifest-row join
- does **not** read `year` from embedding bundles
- writes route-level metrics artifacts to:

```text
data/metrics/<route_name>/metrics.npz
```

- marks `metrics_status=success` only after successful artifact write

Verified successful routes
- `Route_A_Modern`
- `Route_B_Legacy`

Manifest summary after full Phase 5 run
- `metrics_success=2`
- `metrics_failed=0`
- `metrics_pending=0`

## Phase 6 — Statistical Inference
Status: NOT STARTED

Expected future location

```text
bins/s03_analysis/statistics.py
```

---

# CANONICAL DATA CONTRACTS

## Structured JSON contract

Structured export uses flattened top-level fields.

Required exported fields:
- `doc_id`
- `source_filename`
- `source_pdf_path`
- `route`
- `year`
- `extraction_method`
- `page_count`
- `raw_text_length`
- `clean_text_length`
- `segmentation_strategy`
- `A_intro`
- `A_methods`
- `A_results`

Obsolete forms that must not reappear:
- nested `sections` payloads
- mixed-case legacy keys such as `A_Intro`, `A_Methods`, `A_Results`

`A_TAK` remains a segmentation-stage internal artifact and is not part of the structured export contract.

## Embedding bundle contract

Each Phase 4 embedding bundle stores:
- `doc_id`
- `route`
- `section_labels`
- `embeddings`
- `source_path`

Important constraints:
- embeddings are section embeddings, not manuscript-level vectors
- the metrics stage reads `year` from the manifest, not from the bundle
- section labels correspond to real exported section content, not scaffold placeholders

## Metrics artifact contract

Phase 5 metrics outputs are:
- route-level artifacts
- not document-level artifacts

Output location:

```text
data/metrics/<route_name>/metrics.npz
```

Current semantic contract:
- each artifact summarizes route-level epoch metrics
- epoch grouping uses manifest year
- artifact persistence must succeed before manifest success writeback

---

# MANIFEST-DRIVEN EXECUTION MODEL

Manifest path:

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
- one document row per corpus item
- stage state is advanced only after successful stage completion
- Phase 5 uses manifest metadata as the authoritative temporal join source

---

# CURRENT VERIFIED PIPELINE FLOW

```text
RAW PDF
  ↓
smart_extract_pdf()
  ↓
clean extracted text (.txt)
  ↓
UniversalSegmenter
  ↓
StructuredSectionArtifact
  ↓
structured JSON
  ↓
embedder.py
  ↓
EmbeddingArtifact (.npz)
  ↓
manifest-tracked embedding completion
  ↓
metrics.py
  ↓
manifest-row year join
  ↓
route-level MetricsArtifact (.npz)
  ↓
manifest-tracked metrics completion
```

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

## Shared schema layer
Canonical constants live in:

```text
bins/s04_utils/schemas.py
```

## Validation layer
Validation helpers live in:

```text
bins/s04_utils/validators.py
```

## Artifact boundary
Typed artifacts live in:

```text
bins/s04_utils/artifacts.py
```

Key artifacts:
- `StructuredSectionArtifact`
- `EmbeddingArtifact`
- `MetricsArtifact`

## Manifest layer
Execution tracking lives in:

```text
bins/s04_utils/manifest_manager.py
```

## Legacy compatibility residue
- `data/manifests/pipeline_manifest.csv` remains the authoritative execution table
- any remaining `MASTER_LEDGER` constant is compatibility-only and not the active execution contract
- `bins/s01_ingest/ledger.py` remains helper-only for stable `doc_id` and route derivation
- legacy ingest rebuild orchestration is retired from the active workflow

## Year resolution contract
Year resolution is deterministic and must not regress.

Resolution precedence:
1. `manifest_row["year"]` when available
2. explicit legacy filename mapping from:

```text
data/manifests/legacy_filename_year_map.csv
```

3. supported filename parsing from `bins/s04_utils/year_resolution.py`
4. fail fast if unresolved

Operational rules:
- unsupported filenames must not silently guess a year
- benchmark-only hardcoded filename special cases must not reappear in active export code
- manifest year remains authoritative when available

---

# TEST CORPUS ISOLATION

Validation dataset location:

```text
data/testing/doi_abstracts_2021_2026
```

The testing corpus must remain isolated from the production manuscript corpus.

Do not:
- mix testing inputs into production routes
- use testing artifacts as production metrics inputs
- treat testing outputs as canonical production state

---

# MATHEMATICAL FRAMEWORK

These remain fixed and must not drift.

Epoch centroid

```python
epoch_centroid = np.mean(epoch_vectors, axis=0)
```

Cosine distance

```python
distance.cosine(vector_A, vector_B)
```

Semantic dispersion
- computed with vectorized cosine-distance operations from section vectors to the epoch centroid
- loop-based per-vector implementations remain disallowed where vectorized operations are available

Innovation velocity

```python
distance.cosine(centroid_T, centroid_T_plus_1)
```

---

# HISTORICAL NOTES RELEVANT TO CURRENT STATE

The major schema bug corrected before successful Phase 4/5 execution was:
- structured export drift between mixed-case keys and canonical keys
- nested section payload assumptions
- resulting empty embeddable section content during early Phase 4 runs

That failure mode has been corrected and protected by tests and validation layers.

Earlier same-day Phase 5 “contract-lock” notes are historical only. They are superseded by the completed real-artifact execution state recorded in this document.

---

# SESSION-CLOSE RESUME POINT

Phase 5 no longer resumes at scaffold integration or executor wiring.

The next session should begin from one of:
- downstream validation and interpretation of route-level metrics artifacts
- Phase 6 statistical inference
- reporting/manuscript integration tasks explicitly requested by the user

This file is the canonical handoff for continuation sessions.
