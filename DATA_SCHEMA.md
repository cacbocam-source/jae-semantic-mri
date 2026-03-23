# Data Schema Specification

## JAE_Legacy_Audit — Semantic MRI Pipeline

Version: 2.4  
Date: 2026-03-23  
Status: Post-stabilization schema aligned with validated Phase 6 reporting execution

> This schema reflects the corrected and validated system state.  
> See `DEBUGGING_AUDIT_2026-03-22.md` for full correction history.

---

## 1. Overview

The current system produces six primary artifact classes:
1. structured JSON (Phase 3)
2. embedding bundles (Phase 4)
3. metrics artifacts (Phase 5)
4. manifest records (control layer)
5. backend reporting outputs (Phase 6)
6. manuscript-facing reporting outputs (Phase 6, APA 7 constrained)

Each artifact has a strict schema or contract boundary. Violations indicate pipeline drift.

---

## 2. Structured artifact schema

**Location**

```text
data/structured/<route>/<year>/<file>.json
```

**Structure**

Each JSON file contains flattened section fields:

```json
{
  "A_intro": "string",
  "A_methods": "string",
  "A_results": "string"
}
```

**Constraints**
- UTF-8 encoded
- non-empty text fields where section text exists
- one file per source PDF
- no embedded metadata required beyond the section payload
- no nested `sections` dict

---

## 3. Embedding bundle schema (authoritative)

**Location**

Embedding bundles are recursively discoverable under:

```text
data/embeddings/<route>/...
```

**Required keys**

Each `.npz` file must contain:

| Key | Type | Description |
|---|---|---|
| `doc_id` | scalar string | Stable document identifier |
| `route` | scalar string | Route name |
| `section_labels` | 1D array (`object`) | Labels per embedding |
| `embeddings` | 2D array (`float32`) | Shape: `(n_sections, 768)` |
| `source_path` | scalar string | Path to structured JSON source |

**Current implementation**
- single embedding per document
- `section_labels = ["document"]`
- `embeddings.shape = (1, 768)`

**Constraints**
- `embeddings.ndim == 2`
- `embeddings.shape[1] == 768`
- dtype must be `float32`
- values must be finite
- `len(section_labels) == embeddings.shape[0]`
- `doc_id` must be derived from source PDF path, not JSON path

**Storage invariant**
- structured: `data/structured/<route>/<year>/<file>.json`
- embeddings: recursively discoverable under `data/embeddings/<route>/...`

---

## 4. Metrics artifact schema

**Location**

```text
data/metrics/<route>/metrics.npz
```

**Required keys**

| Key | Type | Description |
|---|---|---|
| `corpus_name` | scalar | Corpus identifier |
| `route_name` | scalar | Route identifier |
| `epoch_labels` | 1D array (`object`) | Epoch strings |
| `epoch_counts` | 1D array (`int32` or equivalent integer array) | Counts per epoch |
| `epoch_centroids` | 2D array (`float32`) | Shape: `(N, 768)` |
| `semantic_dispersion` | 1D array (`float32`) | Per-epoch dispersion |
| `innovation_velocity` | 1D array (`float32`) | Between-epoch distances |
| `source_embedding_files` | 1D array (`object`) | Source bundle paths |
| `created_at_utc` | scalar | Timestamp |
| `metric_version` | scalar | Version string |

**Constraints**
- `len(epoch_labels) = N`
- `epoch_centroids.shape = (N, 768)`
- `len(innovation_velocity) = N - 1`
- all numeric arrays must be finite
- epoch labels must be sorted ascending

---

## 5. Epoch schema

**Configuration**
- `EPOCH_WIDTH = 5`
- `BASE_YEAR = 1960`

**Mapping rule**

```python
epoch_start = year - ((year - 1960) % 5)
epoch_end   = epoch_start + 4
```

**Label format**
- `1960-1964`
- `1965-1969`

**Interpretation**
- each epoch aggregates all vectors within its interval
- epochs are non-overlapping and contiguous

---

## 6. Manifest schema

**Location**

```text
data/manifests/pipeline_manifest.csv
```

**Required columns**
- `doc_id`
- `source_pdf_path`
- `source_filename`
- `route`
- `year`
- `extract_status`
- `structured_status`
- `embedding_status`
- `metrics_status`
- `extract_method`
- `page_count`
- `error_message`
- `last_stage_run`
- `artifact_version`
- `updated_at`

**Allowed status values**
- `pending`
- `success`
- `failed`
- `skipped`

**Role**
The manifest provides:
- pipeline state tracking
- stage eligibility control
- metadata injection (`year`, `route`)
- audit traceability

---

## 7. Metrics eligibility logic

A document is eligible for metrics if:
- `structured_status == success`
- and
  - `embedding_status == success`
  - or an embedding bundle exists on disk

---

## 8. Cross-artifact relationships

### Document flow
`PDF → Structured JSON → Embedding Bundle → MetricRecord(s) → Metrics Artifact`

### Identity propagation
- `doc_id` originates from the PDF path
- it is preserved across all stages
- it must remain stable

### Temporal injection
- `year` originates from the manifest
- `year` is not stored in embedding bundles as a trusted Phase 5 source
- `year` is applied during metrics computation

---

## 9. Validation invariants

The pipeline is valid only if all of the following hold.

### Structural
- structured count equals embedding count for the validated legacy corpus

### Schema
- all embedding bundles pass validation
- all metrics artifacts pass validation

### Metrics
- each artifact loads without error
- `epoch_labels` are sorted
- `epoch_counts > 0`

### Current validated temporal state
- `Route_A_Modern`: `['2025-2029']`
- `Route_B_Legacy`: `['1960-1964', '1965-1969']`
- `Route_B_Legacy` innovation-velocity count: `1`

---

## 10. Phase 6 reporting output locations

### Backend analysis outputs
- `analysis_outputs/summaries/`
- `analysis_outputs/tables/`
- `analysis_outputs/figures/`

### Manuscript-facing outputs
- `manuscript/paper/tables/`
- `manuscript/paper/figures/`

These locations are downstream reporting/output surfaces and do not replace the validated route-level metrics artifacts stored under `data/metrics/`.

---

## 11. Phase 6 reporting artifacts

### Descriptive summary outputs
Current validated outputs:
- `analysis_outputs/summaries/Route_A_Modern_summary.md`
- `analysis_outputs/summaries/Route_B_Legacy_summary.md`

### Machine-readable table exports
Current validated outputs:
- `analysis_outputs/tables/Route_A_Modern_epoch_summary.csv`
- `analysis_outputs/tables/Route_A_Modern_innovation_velocity.csv`
- `analysis_outputs/tables/Route_B_Legacy_epoch_summary.csv`
- `analysis_outputs/tables/Route_B_Legacy_innovation_velocity.csv`

### Backend figure exports
Current validated outputs:
- `analysis_outputs/figures/Route_A_Modern_epoch_dispersion.png`
- `analysis_outputs/figures/Route_B_Legacy_epoch_dispersion.png`
- `analysis_outputs/figures/Route_B_Legacy_innovation_velocity.png`

### APA manuscript outputs
Current validated outputs:
- `manuscript/paper/tables/Table_1_epoch_summary.md`
- `manuscript/paper/tables/Table_2_innovation_velocity.md`
- `manuscript/paper/figures/Figure_1_epoch_dispersion.png`
- `manuscript/paper/figures/Figure_1_epoch_dispersion.md`
- `manuscript/paper/figures/Figure_2_innovation_velocity.png`
- `manuscript/paper/figures/Figure_2_innovation_velocity.md`

### Reporting constraint
All manuscript-facing and reporting-facing Phase 6 outputs are governed by mandatory APA 7 compliance.

---

## 12. Known failure modes (resolved)

Previously observed and corrected:
- embedding bundles missing required keys
- `doc_id` derived from incorrect path
- metrics loader assuming flat directory structure only
- manifest eligibility blocking valid records
- epoch collapse to singleton due to ingestion/schema issues
- documentation drift across current-state and historical files

All pipeline-state issues above were resolved by 2026-03-22; the documentation/reporting synchronization layer was extended on 2026-03-23.

---

## 13. Current state

The schema is now:
- consistent with code
- validated through full pipeline execution
- aligned with current audit record
- extended to cover Phase 6 reporting outputs
- stable for downstream descriptive and manuscript-facing analysis

---

## 14. Control references
- `METHODS_PIPELINE.md`
- `AUDIT_CONTEXT.md`
- `RESEARCH_LOG.md`
- `DEBUGGING_AUDIT_2026-03-22.md`
- `SCHEMA_CONTRACT.json`
- `REPO_KEEP_ARCHIVE_MAP.md`
