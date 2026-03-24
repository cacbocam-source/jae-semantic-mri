# Computational Methods Pipeline

## Semantic MRI of Agricultural Education

Version: 2.5  
Date: 2026-03-23  
Status: Current validated methods summary aligned to Route_A expansion and Phase 6 reporting execution

> This document reflects the current validated pipeline and reporting state following stabilization, Route_A_Modern expansion, targeted repair of year-resolution and manifest identity behavior, and successful regeneration of Phase 5 and Phase 6 outputs.  
> See `DEBUGGING_AUDIT_2026-03-22.md` for the stabilization audit and `AUDIT_CONTEXT.md` for the controlling current-state snapshot.

---

## 1. Computational environment

All analyses were conducted on an Apple Silicon workstation equipped with an M3 Max processor and 64 GB of unified memory.

Embedding computation used Apple Metal Performance Shaders:

```python
DEVICE = "mps"

Primary data storage:

/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit

Embedding model:

nomic-ai/nomic-embed-text-v1.5

Key runtime characteristics:

768-dimensional embeddings
8192-token context window
worker pool constrained to MAX_WORKERS = 8

Environment reproducibility artifacts:

pyproject.toml
requirements-lock.txt
2. Corpus processing architecture

The operational workflow is organized into five effective stages:

extraction and cleaning (Bin 02)
segmentation and structured export (Bin 03)
embedding generation (Bin 03)
route-level metrics aggregation (Phase 5)
interpretive/reporting outputs (Phase 6)
Dual ingestion schema

The system operates across two canonical ingestion routes.

Route_A_Modern

accepted live raw layouts:
flat-file modern form: data/raw/Route_A_Modern/<YEAR>.pdf
year-bucket modern form: data/raw/Route_A_Modern/<YEAR>/<file>.pdf
year resolved from:
manifest year when available
filename parsing when the filename carries a valid year
parent-directory parsing when the file is stored under a year-bucket directory

Route_B_Legacy

canonical layout: data/raw/Route_B_Legacy/<YEAR>/<file>.pdf
year resolved from:
manifest year when available
explicit legacy filename map where required
directory structure
supported filename parsing when applicable

This dual schema is resolved through deterministic year inference during processing.

Phase 3 execution behavior

During analysis execution:

manifest seeding from raw corpus state
deterministic year inference
exclusion of non-temporal artifacts
structured JSON export
embedding generation
metrics eligibility propagation

Implementation note:

write_section_export() may re-access raw PDFs and re-trigger extraction logic
the pipeline is therefore not strictly single-pass
this redundancy affects compute cost but not correctness under the current validated contract

Non-temporal artifacts (e.g., unresolved year) are excluded prior to downstream processing.

3. Validated corpus state

Validated live state reflected in the current repo:

data/raw/Route_A_Modern/
data/raw/Route_B_Legacy/
Route_A_Modern

Current admitted modern corpus:

10 source PDFs
temporal coverage currently realized across:
2000
2001
2003
2007
2012
2013
2018
2022
2024
2026

Operational consequence:

Route A is no longer a singleton placeholder route
Route_B_Legacy

Current admitted legacy corpus:

149 validated legacy documents
current live legacy temporal coverage:
1960–1969
full pipeline completion through route-level metrics has been validated for this admitted legacy set
4. Intake protocol

The live corpus now accepts the following raw-storage forms.

Modern route
data/raw/Route_A_Modern/<YEAR>.pdf
data/raw/Route_A_Modern/<YEAR>/<filename>.pdf
Legacy route
data/raw/Route_B_Legacy/<YEAR>/<filename>.pdf

Constraints:

each document maps to exactly one route
each document maps to exactly one year
unresolved items are quarantined or excluded
epoch assignment is derived post-ingestion from the resolved year
no unsupported year value may be silently guessed
5. Extraction and cleaning (Bin 02)

Processing behaviors:

native text extraction when available
OCR fallback for scanned documents
reference-section truncation
route-aware preprocessing
exclusion of non-temporal artifacts before downstream persistence where year cannot be resolved

The process phase writes cleaned text artifacts to:

data/processed/<route>/...
6. Segmentation and structured export (Bin 03)

Segment outputs are organized into the current canonical top-level section surface used by the project’s structured artifact builder.

Representative semantic section roles:

A_intro
A_methods
A_results

Structured storage:

data/structured/<route>/<year>/<file>.json

For flat modern files whose source path is data/raw/Route_A_Modern/<YEAR>.pdf, the corresponding structured artifact may remain flat under the route root, e.g.:

data/structured/Route_A_Modern/2026.json
Year-resolution precedence
manifest value
explicit legacy filename map
supported filename parsing
supported parent-directory parsing
fail-fast if unresolved
Operational rule

A DOI-style filename without an embedded four-digit year is valid if the file is stored under a year-bucket directory whose parent name is itself a valid year.

Example:

data/raw/Route_A_Modern/2024/10.5032_jae.v65i4.2828.pdf → 2024
7. Embedding generation (Bin 03)
Input
structured JSON artifacts
Output
embedding bundles discovered recursively under data/embeddings/<route>/...
Embedding bundle schema (authoritative)

Each embedding bundle must contain:

doc_id (scalar)
route (scalar)
section_labels (1D array, dtype=object)
embeddings (2D array, shape = [n_sections, 768], dtype=float32)
source_path (scalar)
Current implementation

Current live implementation persists one embedding vector per document:

section_labels = ["document"]
embeddings.shape = (1, 768)
Constraints

embeddings must be:

2D
float32
finite
width 768

Additional constraints:

section-label alignment enforced
doc_id must be derived from source PDF path
manifest integration and analysis execution must use the same doc_id contract
Storage invariant
structured: data/structured/<route>/<year>/<file>.json or the validated flat modern equivalent for legacy flat-path carryover
embeddings: recursively discoverable under data/embeddings/<route>/...
8. Metrics computation (Phase 5)

Implementation:

bins/s03_analysis/metrics.py
Inputs
validated embedding bundles
manifest metadata
Eligibility conditions

A document is eligible if:

structured_status == success
and
embedding_status == success
or an embedding bundle exists on disk
Embedding discovery

The metrics stage supports both flat and nested layouts through recursive lookup.

Record expansion

Each embedding bundle produces one or more MetricRecord objects:

one per (section_label, embedding_vector)
Route-level persistence

Route-level metrics artifacts are written to:

data/metrics/Route_A_Modern/metrics.npz
data/metrics/Route_B_Legacy/metrics.npz
9. Epoch aggregation
Configuration
EPOCH_WIDTH = 5
BASE_YEAR = 1960
Epoch mapping
epoch_start = year - ((year - 1960) % 5)
epoch_end   = epoch_start + 4

Examples:

1960 → 1960–1964
1965 → 1965–1969
2000 → 2000–2004
2024 → 2020–2024
2026 → 2025–2029
Grouping

Vectors are grouped by epoch.

Metrics per epoch
epoch_counts
epoch_centroids
semantic_dispersion
Innovation velocity

Between adjacent epochs:

velocity = cosine_distance(centroid_i, centroid_j)
Cardinality rule

For N epochs:

len(epoch_labels) = N
len(innovation_velocity) = N - 1
10. Validated current metrics state
Route_A_Modern
epoch count: 6
epoch labels: ['2000-2004', '2005-2009', '2010-2014', '2015-2019', '2020-2024', '2025-2029']
innovation-velocity count: 5
source embedding file count: 10
Route_B_Legacy
epoch count: 2
epoch labels: ['1960-1964', '1965-1969']
innovation-velocity count: 1
structured / embedding parity: 149 / 149

Operational consequence:

both routes now support bounded route-internal temporal description
Route A is no longer analytically constrained to a singleton epoch
11. Phase 6 interpretive reporting and manuscript-facing output layer

Phase 6 operates strictly downstream of validated route-level metrics artifacts and does not modify upstream processing, embedding, or metrics-generation stages. Its function is interpretive, descriptive, and reporting-oriented.

Inputs

Phase 6 consumes validated route-level metrics artifacts from:

data/metrics/Route_A_Modern/metrics.npz
data/metrics/Route_B_Legacy/metrics.npz
Output classes
1. Descriptive summary outputs

Generated under:

analysis_outputs/summaries/

These summarize route identity, epoch count, source embedding file count, epoch-level dispersion, and route-internal innovation-velocity structure.

2. Machine-readable export outputs

Generated under:

analysis_outputs/tables/

These exports preserve route/epoch/transition values in structured form suitable for downstream validation, audit inspection, and reproducible reporting workflows.

3. Backend figure outputs

Generated under:

analysis_outputs/figures/

These provide non-manuscript visualization artifacts for inspection and validation of epoch-level semantic dispersion and route-internal innovation velocity where transitions exist.

4. APA manuscript outputs

Generated under:

manuscript/paper/tables/
manuscript/paper/figures/

These outputs provide APA 7–constrained reporting surfaces for manuscript integration.

Route constraints in Phase 6

Phase 6 preserves the validated route structure rather than imposing artificial symmetry across routes.

Route_A_Modern currently contributes:
6 validated epochs
5 validated adjacent-epoch innovation-velocity transitions
epoch-level descriptive output
innovation-velocity tables and figures
Route_B_Legacy currently contributes:
2 validated epochs
1 validated adjacent-epoch innovation-velocity transition
epoch-level descriptive output
innovation-velocity tables and figures
Reporting standard

All Phase 6 reporting artifacts intended for presentation or manuscript use are governed by an embedded APA 7 compliance rule without exception.

Boundary condition

Phase 6 is descriptive and reporting-oriented. It should not be used to silently alter upstream metrics state, infer unsupported conclusions, or reopen stabilized engineering work unless a new contradiction is demonstrated by validated artifacts.

At the current state, broader inferential claims remain limited by uneven corpus coverage across the full 1960–2026 study window, despite Route A’s successful widening.

12. Reproducibility and auditability

The validated pipeline now guarantees:

deterministic filesystem layout
manifest-backed year propagation
stable source-path-derived doc_id
recursive embedding discovery over mixed storage layouts
explicit artifact persistence
fail-fast year-resolution behavior
Phase 6 reproducible output regeneration from route-level metrics
APA 7 governance for manuscript-facing reporting artifacts

Control surfaces:

AUDIT_CONTEXT.md
RESEARCH_LOG.md
DEBUGGING_AUDIT_2026-03-22.md
DATA_SCHEMA.md
SCHEMA_CONTRACT.json
13. Current operational state

The pipeline is currently:

operational
schema-consistent
validated on the currently admitted corpus
reproducible
Phase 6-active with backend and APA reporting outputs
ready for restrained interpretive refinement
ready for continued modern-year and legacy-decade corpus expansion without reopening infrastructure debugging unless new contradictory evidence appears

