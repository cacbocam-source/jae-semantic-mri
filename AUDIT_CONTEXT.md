# SEMANTIC MRI PIPELINE — PROJECT STATE AUDIT

Version: 3.5  
Date: 2026-03-23  
Status: Canonical current-state handoff for continuation sessions

This document is the authoritative operational snapshot for the current repository state.

## Authority rules

- This file controls current-state interpretation.
- `RESEARCH_LOG.md` is the canonical chronological session log.
- `DEBUGGING_AUDIT_2026-03-22.md` is the authoritative engineering record for the stabilization cycle completed on 2026-03-22.
- `audit.md` is supplemental historical workflow and infrastructure history only.
- `METHODS_PIPELINE.md` is the current methods summary.
- `DATA_SCHEMA.md` and `SCHEMA_CONTRACT.json` are the current schema/contract summaries.
- If any conflict exists between this file and any supplemental document, this file controls unless this file explicitly delegates to a narrower authoritative contract.
- All repo-relative paths are assumed to resolve under:

```text
/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
```

- Do not assume a home-directory anchor path is authoritative unless it has been explicitly resolved to the same target.

---

## Project identity

**Project name**  
Semantic MRI of Agricultural Education

**Full title**  
*A Semantic MRI of Agricultural Education: A Longitudinal Audit of Evolutionary Maturation, Methodological Friction, and Innovation Velocity (1960–2026) via High-Dimensional Vector Embeddings*

**Research objective**  
Measure the semantic evolution of agricultural education research using high-dimensional vector embeddings applied to journal manuscript sections.

**Primary measurements**
- semantic dispersion
- innovation velocity
- epoch centroid drift

**Corpus**
- Journal of Agricultural Education manuscripts

**Temporal scope**
- 1960–2026

**Epoch structure**
- deterministic 5-year epochs

---

## Current repository architecture

```text
JAE_Legacy_Audit
│
├── bins
│   ├── s01_ingest
│   ├── s02_processor
│   ├── s03_analysis
│   ├── s04_utils
│   └── s06_analysis
│
├── data
│   ├── raw
│   ├── processed
│   ├── structured
│   ├── embeddings
│   ├── metrics
│   ├── manifests
│   ├── staging
│   └── testing
│
├── analysis_outputs
│   ├── summaries
│   ├── tables
│   └── figures
│
├── docs
├── legacy_acquisition
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

### Utility layer

```text
bins/s04_utils/
├── artifacts.py
├── manifest_manager.py
├── schemas.py
├── validators.py
└── year_resolution.py
```

### Phase 6 layer

```text
bins/s06_analysis/
├── loaders.py
├── interpret.py
├── report_builder.py
├── figure_builder.py
├── apa_table_builder.py
└── apa_figure_builder.py
```

### Load-bearing utility surfaces
- `bins/s04_utils/artifacts.py`
- `bins/s04_utils/manifest_manager.py`
- `bins/s04_utils/schemas.py`
- `bins/s04_utils/validators.py`
- `bins/s04_utils/year_resolution.py`

---

## Ingestion and year resolution

The live corpus currently operates under two validated route layouts.

### Route_A_Modern
- file pattern: `data/raw/Route_A_Modern/<YEAR>.pdf`
- year resolution: filename-derived
- example: `2026.pdf → 2026`

### Route_B_Legacy
- file pattern: `data/raw/Route_B_Legacy/<YEAR>/<file>.pdf`
- year resolution: directory-derived
- example: `1960/<file>.pdf → 1960`

### Non-temporal artifacts

Some legacy artifacts do not resolve to a valid year (e.g., `Vol1_1.pdf`).

Operational rule:
- such files are excluded from manifest seeding and downstream processing
- they are not assigned a persisted sentinel year
- exclusion is explicit and logged during pipeline execution

### Year-resolution contract

Resolution precedence:
1. `manifest_row["year"]` when available
2. explicit legacy filename mapping from `data/manifests/legacy_filename_year_map.csv`
3. supported filename parsing from `bins/s04_utils/year_resolution.py`
4. fail fast if unresolved

Operational rules:
- unsupported filenames must not silently guess a year
- manifest year remains authoritative when available

---

## Computational philosophy

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

## Hardware environment

**Primary compute system**
- Apple Silicon M3 Max
- 64 GB unified memory

**Acceleration**

```python
DEVICE = "mps"
```

**Embedding model**

```python
MODEL_ID = "nomic-ai/nomic-embed-text-v1.5"
```

**Model properties**
- 768-dimensional embeddings
- 8192-token context window
- suitable for long scientific text

**Worker configuration**

```python
MAX_WORKERS = 8
```

---

## Current implemented state

### Phase 1 — Infrastructure
**Status:** COMPLETE

### Phase 2 — Extraction pipeline
**Status:** COMPLETE

Core modules:
- `digital_extract.py`
- `ocr_engine.py`
- `smart_extract.py`
- `cleaning.py`
- `segmenter.py`

### Phase 3 — Structured export
**Status:** COMPLETE

Core modules:
- `section_export.py`
- `orchestrator.py`

Implemented behavior:
- canonical top-level section export
- no nested `sections` payloads
- deterministic year resolution delegated to `bins/s04_utils/year_resolution.py`

### Phase 4 — Embedding generation
**Status:** COMPLETE

Implemented behavior:
- one schema-compliant embedding bundle per structured document
- stable `doc_id` derived from source PDF path
- storage mirrored under route/year hierarchy
- embedding bundle contract aligned to metrics loader

### Phase 5 — Route-level metrics
**Status:** COMPLETE AND VALIDATED

Implemented behavior:
- metrics generated from manifest-backed document years
- recursive embedding discovery supports flat and nested route structures
- route-level metrics persisted at:

```text
data/metrics/Route_A_Modern/metrics.npz
data/metrics/Route_B_Legacy/metrics.npz
```

### Current validated temporal state

#### Route_A_Modern

- `epoch_count = 6`
- `epoch_labels = ['2000-2004', '2005-2009', '2010-2014', '2015-2019', '2020-2024', '2025-2029']`
- `innovation_velocity_count = 5`
- `source_embedding_file_count = 10`

#### Route_B_Legacy

- `epoch_count = 2`
- `epoch_labels = ['1960-1964', '1965-1969']`
- `innovation_velocity_count = 1`

### Current validated output state

- `Route_A_Modern = multi-epoch route artifact`
- `Route_B_Legacy = two-epoch route artifact`

#### Current cardinality validation
- structured legacy artifacts: `149`
- embedding legacy artifacts: `149`

### Phase 6 — Interpretive analysis and reporting
**Status:** EXTENDED, VALIDATED, AND EXECUTING

Implemented surfaces:
- `bins/s06_analysis/loaders.py`
- `bins/s06_analysis/interpret.py`
- `bins/s06_analysis/report_builder.py`
- `bins/s06_analysis/figure_builder.py`
- `bins/s06_analysis/apa_table_builder.py`
- `bins/s06_analysis/apa_figure_builder.py`

#### Phase 6 output classes

**1. Descriptive summary outputs**

Generated under:
- `analysis_outputs/summaries/`

Current validated outputs:
- `Route_A_Modern_summary.md`
- `Route_B_Legacy_summary.md`

**2. Machine-readable table exports**

Generated under:
- `analysis_outputs/tables/`

Current validated outputs:
- `Route_A_Modern_epoch_summary.csv`
- `Route_A_Modern_innovation_velocity.csv`
- `Route_B_Legacy_epoch_summary.csv`
- `Route_B_Legacy_innovation_velocity.csv`

### Phase 6 — Interpretive Analysis

Status: EXTENDED AND EXECUTING

Implemented surfaces:

- `bins/s06_analysis/loaders.py`
- `bins/s06_analysis/interpret.py`
- `bins/s06_analysis/report_builder.py`
- `bins/s06_analysis/figure_builder.py`
- `bins/s06_analysis/apa_table_builder.py`
- `bins/s06_analysis/apa_figure_builder.py`

Generated outputs:

#### Backend outputs
- `analysis_outputs/summaries/Route_A_Modern_summary.md`
- `analysis_outputs/summaries/Route_B_Legacy_summary.md`
- `analysis_outputs/tables/Route_A_Modern_epoch_summary.csv`
- `analysis_outputs/tables/Route_A_Modern_innovation_velocity.csv`
- `analysis_outputs/tables/Route_B_Legacy_epoch_summary.csv`
- `analysis_outputs/tables/Route_B_Legacy_innovation_velocity.csv`
- `analysis_outputs/figures/Route_A_Modern_epoch_dispersion.png`
- `analysis_outputs/figures/Route_A_Modern_innovation_velocity.png`
- `analysis_outputs/figures/Route_B_Legacy_epoch_dispersion.png`
- `analysis_outputs/figures/Route_B_Legacy_innovation_velocity.png`

#### APA manuscript outputs
- `manuscript/paper/tables/Table_1_epoch_summary.md`
- `manuscript/paper/tables/Table_2_innovation_velocity.md`
- `manuscript/paper/figures/Figure_1_epoch_dispersion.png`
- `manuscript/paper/figures/Figure_1_epoch_dispersion.md`
- `manuscript/paper/figures/Figure_2_innovation_velocity.png`
- `manuscript/paper/figures/Figure_2_innovation_velocity.md`

Operational meaning:

- `Route_A_Modern` is no longer a singleton route and now supports bounded within-route temporal description.
- `Route_B_Legacy` remains the validated two-epoch legacy route.
- Phase 6 now supports backend summaries, machine-readable tables, backend figures, APA manuscript tables, and APA manuscript figures.

Reporting rule:

- all data analysis reporting artifacts must conform to APA 7 without exception.

**3. Backend figure exports**

Generated under:
- `analysis_outputs/figures/`

Current validated outputs:
- `Route_A_Modern_epoch_dispersion.png`
- `Route_B_Legacy_epoch_dispersion.png`
- `Route_B_Legacy_innovation_velocity.png`

No Route A innovation-velocity backend figure is produced because `Route_A_Modern` contains only one validated epoch and therefore has no adjacent transition.

**4. APA manuscript reporting outputs**

Generated under:
- `manuscript/paper/tables/`
- `manuscript/paper/figures/`

Current validated APA table outputs:
- `Table_1_epoch_summary.md`
- `Table_2_innovation_velocity.md`

Current validated APA figure outputs:
- `Figure_1_epoch_dispersion.png`
- `Figure_1_epoch_dispersion.md`
- `Figure_2_innovation_velocity.png`
- `Figure_2_innovation_velocity.md`

#### Reporting rule

All data analysis reporting artifacts are governed by an embedded rule of **APA 7 compliance without exception**. This applies to manuscript-facing tables, manuscript-facing figures, and any future presentation-oriented Phase 6 reporting outputs.

---

## Current analytic interpretation boundary

Interpretation remains bounded by current corpus structure.

### Allowed
- route-internal epoch summaries
- route-internal dispersion comparison
- route-internal innovation-velocity inspection
- descriptive comparison of route structure
- manuscript-facing descriptive reporting under APA 7 constraints

### Not yet justified
- strong inferential claims about long-run trajectory
- strong cross-route causal claims
- publication-grade substantive interpretation beyond descriptive, scaffolded reporting

### Reason
- `Route_A_Modern` remains singleton
- `Route_B_Legacy` currently resolves into two epochs only
- current Phase 6 is a validated descriptive/reporting layer, not a full inferential layer

---

## Recovery / workload control

The core engine is now treated as frozen except for blocker fixes.

### Delegated or semi-delegated work
- manuscript identification
- raw PDF acquisition
- intake queue confirmation
- staging and batch QC

### Owner-controlled work
- final QC
- manifest integration
- pipeline execution
- artifact validation
- documentation closeout
- Phase 6 interpretation/readiness decisions

This remains the official workload-control model for preventing the project from expanding into an unbounded simultaneous scraper/engine/study workload.

---

## Operational next step

The next correct work surface remains **Phase 6 documentation and interpretation refinement**, not further pipeline repair, unless a new contradiction appears in validated artifacts.

Priority order:
1. synchronize authoritative and supplementary documentation
2. keep methods/schema docs aligned to the validated Phase 6 reporting stack
3. preserve APA 7 compliance across all manuscript-facing outputs
4. extend restrained interpretive analysis only within the validated descriptive boundary
5. avoid reopening infrastructure debugging without new evidence

---

## Control references

### Canonical current state
- `AUDIT_CONTEXT.md`

### Canonical chronology
- `RESEARCH_LOG.md`

### Engineering stabilization audit
- `DEBUGGING_AUDIT_2026-03-22.md`

### Historical infrastructure supplement
- `audit.md`

### Methods / schema
- `METHODS_PIPELINE.md`
- `DATA_SCHEMA.md`
- `SCHEMA_CONTRACT.json`


Project identity

Project name
Semantic MRI of Agricultural Education

Full title
A Semantic MRI of Agricultural Education: A Longitudinal Audit of Evolutionary Maturation, Methodological Friction, and Innovation Velocity (1960–2026) via High-Dimensional Vector Embeddings

Research objective
Measure the semantic evolution of agricultural education research using high-dimensional vector embeddings applied to journal manuscript sections.

Primary measurements

semantic dispersion
innovation velocity
epoch centroid drift

Corpus

Journal of Agricultural Education manuscripts

Temporal scope

1960–2026

Epoch structure

deterministic 5-year epochs
Current repository architecture
JAE_Legacy_Audit
│
├── bins
│   ├── s01_ingest
│   ├── s02_processor
│   ├── s03_analysis
│   ├── s04_utils
│   └── s06_analysis
│
├── data
│   ├── raw
│   ├── processed
│   ├── structured
│   ├── embeddings
│   ├── metrics
│   ├── manifests
│   ├── staging
│   └── testing
│
├── analysis_outputs
│   ├── summaries
│   ├── tables
│   └── figures
│
├── docs
├── legacy_acquisition
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
Utility layer
bins/s04_utils/
├── artifacts.py
├── manifest_manager.py
├── schemas.py
├── validators.py
└── year_resolution.py
Phase 6 layer
bins/s06_analysis/
├── loaders.py
├── interpret.py
├── report_builder.py
├── figure_builder.py
├── apa_table_builder.py
└── apa_figure_builder.py
Load-bearing utility surfaces
bins/s04_utils/artifacts.py
bins/s04_utils/manifest_manager.py
bins/s04_utils/schemas.py
bins/s04_utils/validators.py
bins/s04_utils/year_resolution.py
Ingestion and year resolution

The live corpus currently operates under validated mixed route layouts.

Route_A_Modern

Accepted live raw layouts:

flat file pattern: data/raw/Route_A_Modern/<YEAR>.pdf
year-bucket pattern: data/raw/Route_A_Modern/<YEAR>/<file>.pdf

Examples:

2026.pdf → 2026
2024/10.5032_jae.v65i4.2828.pdf → 2024

Operational meaning:

Route A now includes the original flat-file 2026 artifact and the admitted modern year-bucket batch
year resolution must therefore support both filename-derived and parent-directory-derived resolution for modern files
Route_B_Legacy
file pattern: data/raw/Route_B_Legacy/<YEAR>/<file>.pdf
year resolution: directory-derived
example: 1960/<file>.pdf → 1960
Non-temporal artifacts

Some legacy artifacts do not resolve to a valid year (e.g., Vol1_1.pdf).

Operational rule:

such files are excluded from manifest seeding and downstream processing
they are not assigned a persisted sentinel year
exclusion is explicit and logged during pipeline execution
Year-resolution contract

Resolution precedence:

manifest_row["year"] when available
explicit legacy filename mapping from data/manifests/legacy_filename_year_map.csv
supported filename parsing from bins/s04_utils/year_resolution.py
supported parent-directory parsing from bins/s04_utils/year_resolution.py
fail fast if unresolved

Operational rules:

unsupported filenames must not silently guess a year
manifest year remains authoritative when available
parent-directory parsing is now an intentionally supported fallback for admitted year-bucket modern files whose filenames do not themselves contain a 4-digit year
Computational philosophy

The pipeline is designed for:

deterministic computation
full reproducibility
transparent mathematics
auditability
hardware-aware acceleration
fail-fast validation at shared contract boundaries

The system intentionally avoids:

black-box ML pipelines
opaque vector frameworks
undocumented tensor math
silent fallback for route/year/schema drift

Approved scientific libraries for vector math:

numpy
scipy.spatial.distance
Hardware environment

Primary compute system

Apple Silicon M3 Max
64 GB unified memory

Acceleration

DEVICE = "mps"

Embedding model

MODEL_ID = "nomic-ai/nomic-embed-text-v1.5"

Model properties

768-dimensional embeddings
8192-token context window
suitable for long scientific text

Worker configuration

MAX_WORKERS = 8
Current implemented state
Phase 1 — Infrastructure

Status: COMPLETE

Phase 2 — Extraction pipeline

Status: COMPLETE

Core modules:

digital_extract.py
ocr_engine.py
smart_extract.py
cleaning.py
segmenter.py
Phase 3 — Structured export

Status: COMPLETE

Core modules:

section_export.py
orchestrator.py

Implemented behavior:

canonical top-level section export
no nested sections payloads
deterministic year resolution delegated to bins/s04_utils/year_resolution.py
Phase 4 — Embedding generation

Status: COMPLETE

Implemented behavior:

one schema-compliant embedding bundle per structured document
stable doc_id derived from source PDF path
storage mirrored under route/year hierarchy
embedding bundle contract aligned to metrics loader
Phase 5 — Route-level metrics

Status: COMPLETE AND VALIDATED

Implemented behavior:

metrics generated from manifest-backed document years
recursive embedding discovery supports flat and nested route structures
route-level metrics persisted at:
data/metrics/Route_A_Modern/metrics.npz
data/metrics/Route_B_Legacy/metrics.npz
Current validated temporal state
Route_A_Modern
epoch_count = 6
epoch_labels = ['2000-2004', '2005-2009', '2010-2014', '2015-2019', '2020-2024', '2025-2029']
innovation_velocity_count = 5
source_embedding_file_count = 10
Route_B_Legacy
epoch_count = 2
epoch_labels = ['1960-1964', '1965-1969']
innovation_velocity_count = 1
Current validated output state
Route_A_Modern = multi-epoch route artifact
Route_B_Legacy = two-epoch route artifact
Current cardinality validation
structured legacy artifacts: 149
embedding legacy artifacts: 149
Phase 6 — Interpretive analysis and reporting

Status: EXTENDED, VALIDATED, AND EXECUTING

Implemented surfaces:

bins/s06_analysis/loaders.py
bins/s06_analysis/interpret.py
bins/s06_analysis/report_builder.py
bins/s06_analysis/figure_builder.py
bins/s06_analysis/apa_table_builder.py
bins/s06_analysis/apa_figure_builder.py
Phase 6 output classes
1. Descriptive summary outputs

Generated under:

analysis_outputs/summaries/

Current validated outputs:

Route_A_Modern_summary.md
Route_B_Legacy_summary.md
2. Machine-readable table exports

Generated under:

analysis_outputs/tables/

Current validated outputs:

Route_A_Modern_epoch_summary.csv
Route_A_Modern_innovation_velocity.csv
Route_B_Legacy_epoch_summary.csv
Route_B_Legacy_innovation_velocity.csv
3. Backend figure exports

Generated under:

analysis_outputs/figures/

Current validated outputs:

Route_A_Modern_epoch_dispersion.png
Route_A_Modern_innovation_velocity.png
Route_B_Legacy_epoch_dispersion.png
Route_B_Legacy_innovation_velocity.png
4. APA manuscript reporting outputs

Generated under:

manuscript/paper/tables/
manuscript/paper/figures/

Current validated APA table outputs:

Table_1_epoch_summary.md
Table_2_innovation_velocity.md

Current validated APA figure outputs:

Figure_1_epoch_dispersion.png
Figure_1_epoch_dispersion.md
Figure_2_innovation_velocity.png
Figure_2_innovation_velocity.md
Operational meaning
Route_A_Modern is no longer a singleton route and now supports bounded within-route temporal description.
Route_B_Legacy remains the validated two-epoch legacy route.
Phase 6 now supports backend summaries, machine-readable tables, backend figures, APA manuscript tables, and APA manuscript figures.
Reporting rule

All data analysis reporting artifacts are governed by an embedded rule of APA 7 compliance without exception. This applies to manuscript-facing tables, manuscript-facing figures, and any future presentation-oriented Phase 6 reporting outputs.

Current analytic interpretation boundary

Interpretation remains bounded by current corpus structure.

Allowed
route-internal epoch summaries
route-internal dispersion comparison
route-internal innovation-velocity inspection
descriptive comparison of route structure
manuscript-facing descriptive reporting under APA 7 constraints
Not yet justified
strong inferential claims about long-run trajectory
strong cross-route causal claims
publication-grade substantive interpretation beyond descriptive, scaffolded reporting
Reason
Route_A_Modern now resolves into six epochs and five adjacent innovation-velocity transitions
Route_B_Legacy currently resolves into two epochs and one adjacent innovation-velocity transition
corpus coverage remains uneven across the full 1960–2026 window
legacy decade expansion beyond the currently admitted 1960s still remains incomplete
Recovery / workload control

The core engine is now treated as frozen except for blocker fixes.

Delegated or semi-delegated work
manuscript identification
raw PDF acquisition
intake queue confirmation
staging and batch QC
Owner-controlled work
final QC
manifest integration
pipeline execution
artifact validation
documentation closeout
Phase 6 interpretation/readiness decisions

This remains the official workload-control model for preventing the project from expanding into an unbounded simultaneous scraper/engine/study workload.

Operational next step

The next correct work surface is Phase 6 output/documentation synchronization and restrained interpretive refinement, alongside continued corpus expansion where needed.

Priority order:

synchronize authoritative and supplementary documentation with the new validated Route A state
update APA manuscript note text and any stale reporting language that still assumes singleton Route A behavior
keep methods/schema docs aligned to the validated Phase 6 reporting stack
extend restrained interpretive analysis only within the validated descriptive boundary
continue modern-year and legacy-decade corpus expansion without reopening infrastructure debugging unless new contradictory evidence appears
Control references
Canonical current state
AUDIT_CONTEXT.md
Canonical chronology
RESEARCH_LOG.md
Engineering stabilization audit
DEBUGGING_AUDIT_2026-03-22.md
Historical infrastructure supplement
audit.md
Methods / schema
METHODS_PIPELINE.md
DATA_SCHEMA.md
SCHEMA_CONTRACT.json

The highest-value corrections in this rebuild were:
- consolidating the duplicated Phase 6 sections
- removing the false singleton Route A language
- correcting the false claim that no Route A innovation-velocity backend figure exists
- updating the interpretation boundary reason so it reflects the current