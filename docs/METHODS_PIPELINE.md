# Computational Methods Pipeline

## Semantic MRI of Agricultural Education

Version: 2.4  
Date: 2026-03-23  
Status: Post-stabilization methods summary aligned to validated Phase 6 reporting execution

> This document reflects the validated pipeline and reporting state following stabilization and Phase 6 extension.  
> See `DEBUGGING_AUDIT_2026-03-22.md` for full engineering audit and correction history.

---

## 1. Computational environment

All analyses were conducted on an Apple Silicon workstation equipped with an M3 Max processor and 64 GB of unified memory.

Embedding computation used Apple Metal Performance Shaders:

```python
DEVICE = "mps"
```

Primary data storage:

```text
/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
```

Embedding model:

```text
nomic-ai/nomic-embed-text-v1.5
```

Key runtime characteristics:
- 768-dimensional embeddings
- 8192-token context window
- worker pool constrained to `MAX_WORKERS = 8`

Environment reproducibility artifacts:
- `pyproject.toml`
- `requirements-lock.txt`

---

## 2. Corpus processing architecture

The analysis pipeline is organized into five operational stages:
1. extraction and cleaning (Bin 02)
2. segmentation and structured export (Bin 03)
3. embedding generation (Bin 03)
4. route-level metrics aggregation (Phase 5)
5. interpretive/reporting outputs (Phase 6)

### Dual ingestion schema

The system operates across two canonical ingestion routes.

**Route_A_Modern**
- year resolved from filename

**Route_B_Legacy**
- year resolved from directory structure

This dual schema is resolved through deterministic year inference during processing.

### Phase 3 execution behavior

During analysis execution:
- manifest seeding
- year inference
- exclusion of non-temporal artifacts
- structured JSON export
- embedding generation
- metrics eligibility propagation

Implementation note:
- `write_section_export()` may re-access raw PDFs and re-trigger OCR
- the pipeline is not strictly single-pass
- redundancy affects compute cost but not correctness

Non-temporal artifacts (e.g., unresolved year) are excluded prior to downstream processing.

---

## 3. Validated corpus state

Validated benchmark / live state reflected in the current repo:
- `data/raw/Route_A_Modern/`
- `data/raw/Route_B_Legacy/`

Legacy execution state:
- 1960–1969 legacy corpus processed
- 149 validated legacy documents in the current working set
- full pipeline completion through route-level metrics

---

## 4. Intake protocol

Current live ingestion rule:

```text
data/raw/<route>/<year>/<filename>.pdf
```

Constraints:
- each document maps to exactly one route
- each document maps to exactly one year
- unresolved items are quarantined
- epoch assignment is derived post-ingestion

---

## 5. Extraction and cleaning (Bin 02)

Processing behaviors:
- native text extraction when available
- OCR fallback for scanned documents
- reference-section truncation
- route-aware preprocessing

---

## 6. Segmentation and structured export (Bin 03)

Segment outputs:
- `A_intro`
- `A_methods`
- `A_results`

Structured storage:

```text
data/structured/<route>/<year>/<file>.json
```

### Year-resolution precedence
1. manifest value
2. legacy filename map
3. supported filename parsing
4. fail-fast if unresolved

---

## 7. Embedding generation (Bin 03)

### Input
- structured JSON artifacts

### Output
- embedding bundles discovered recursively under `data/embeddings/<route>/...`

### Embedding bundle schema (authoritative)

Each embedding bundle must contain:
- `doc_id` (scalar)
- `route` (scalar)
- `section_labels` (1D array, `dtype=object`)
- `embeddings` (2D array, shape = `[n_sections, 768]`, `dtype=float32`)
- `source_path` (scalar)

### Current implementation

Single embedding per document:
- `section_labels = ["document"]`
- `embeddings.shape = (1, 768)`

### Constraints
`embeddings` must be:
- 2D
- `float32`
- finite
- width 768

Additional constraints:
- section-label alignment enforced
- `doc_id` must be derived from source PDF path

### Storage invariant
- structured: `data/structured/<route>/<year>/<file>.json`
- embeddings: recursively discoverable under `data/embeddings/<route>/...`

---

## 8. Metrics computation (Phase 5)

Implementation:
- `bins/s03_analysis/metrics.py`

### Inputs
- validated embedding bundles
- manifest metadata

### Eligibility conditions
A document is eligible if:
- `structured_status == success`
- and
  - `embedding_status == success`
  - or an embedding bundle exists on disk

### Embedding discovery

The metrics stage supports both flat and nested layouts through recursive lookup.

### Record expansion
Each embedding bundle produces one or more `MetricRecord` objects:
- one per `(section_label, embedding_vector)`

---

## 9. Epoch aggregation

### Configuration
- `EPOCH_WIDTH = 5`
- `BASE_YEAR = 1960`

### Epoch mapping

```python
epoch_start = year - ((year - 1960) % 5)
epoch_end   = epoch_start + 4
```

Examples:
- `1960 → 1960–1964`
- `1965 → 1965–1969`

### Grouping
Vectors are grouped by epoch.

### Metrics per epoch
- `epoch_counts`
- `epoch_centroids`
- `semantic_dispersion`

### Innovation velocity
Between adjacent epochs:

```python
velocity = cosine_distance(centroid_i, centroid_j)
```

### Cardinality rule
For `N` epochs:
- `len(epoch_labels) = N`
- `len(innovation_velocity) = N - 1`

---

## 10. Validated current metrics state

### Route_A_Modern
- epoch count: `1`
- epoch labels: `['2025-2029']`
- innovation-velocity count: `0`

### Route_B_Legacy
- epoch count: `2`
- epoch labels: `['1960-1964', '1965-1969']`
- innovation-velocity count: `1`
- structured / embedding parity: `149 / 149`

---

## 11. Phase 6 interpretive reporting and manuscript-facing output layer

Phase 6 operates strictly downstream of validated route-level metrics artifacts and does not modify upstream processing, embedding, or metrics-generation stages. Its function is interpretive, descriptive, and reporting-oriented.

### Inputs
Phase 6 consumes validated route-level metrics artifacts from:
- `data/metrics/Route_A_Modern/metrics.npz`
- `data/metrics/Route_B_Legacy/metrics.npz`

### Output classes

#### 1. Descriptive summary outputs
Generated under:
- `analysis_outputs/summaries/`

These summarize route identity, epoch count, source embedding file count, epoch-level dispersion, and route-internal innovation-velocity availability.

#### 2. Machine-readable export outputs
Generated under:
- `analysis_outputs/tables/`

These exports preserve route/epoch/transition values in structured form suitable for downstream validation, audit inspection, and reproducible reporting workflows.

#### 3. Backend figure outputs
Generated under:
- `analysis_outputs/figures/`

These provide non-manuscript visualization artifacts for inspection and validation of epoch-level semantic dispersion and route-internal innovation velocity where transitions exist.

#### 4. APA manuscript outputs
Generated under:
- `manuscript/paper/tables/`
- `manuscript/paper/figures/`

These outputs provide APA 7–constrained reporting surfaces for manuscript integration.

### Route constraints in Phase 6
Phase 6 preserves the validated route structure rather than imposing artificial symmetry across routes.

- `Route_A_Modern` currently contains one validated epoch and therefore contributes:
  - epoch-level descriptive output
  - no innovation-velocity transition output

- `Route_B_Legacy` currently contains two validated epochs and therefore contributes:
  - epoch-level descriptive output
  - one validated adjacent-epoch innovation-velocity transition

### Reporting standard
All Phase 6 reporting artifacts intended for presentation or manuscript use are governed by an embedded **APA 7 compliance rule without exception**.

### Boundary condition
Phase 6 is descriptive and reporting-oriented. It should not be used to silently alter upstream metrics state, infer unsupported conclusions, or reopen stabilized engineering work unless a new contradiction is demonstrated by validated artifacts.
