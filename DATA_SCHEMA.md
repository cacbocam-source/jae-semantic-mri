
# Data Schema Specification

## JAE_Legacy_Audit — Semantic MRI Pipeline

Version: 2.5  
Date: 2026-03-30  
Status: Current schema aligned to the widened Route_A_Modern state and validated Phase 6 reporting stack

> This schema reflects the current validated state after the 2026-03-23 Route_A_Modern expansion, year-resolution repair, manifest-identity repair, and regeneration of Phase 5 and Phase 6 outputs.  
> See `AUDIT_CONTEXT.md` for the controlling current-state handoff, `RESEARCH_LOG.md` for chronology, and `DEBUGGING_AUDIT_2026-03-22.md` for the bounded stabilization audit.

---

## 1. Overview

The live system produces six primary artifact classes:
1. structured JSON (Phase 3)
2. embedding bundles (Phase 4)
3. route-level metrics artifacts (Phase 5)
4. manifest records (control layer)
5. backend reporting outputs (Phase 6)
6. manuscript-facing reporting outputs (Phase 6, APA 7 constrained)

Each artifact boundary is load-bearing. Violations indicate contract drift rather than optional variation.

---

## 2. Structured artifact schema

**Locations**

```text
data/structured/<route>/<year>/<file>.json
```

Validated flat modern carryover remains acceptable for flat-file modern inputs:

```text
data/structured/Route_A_Modern/2026.json
```

**Payload**

```json
{
  "A_intro": "string",
  "A_methods": "string",
  "A_results": "string"
}
```

**Constraints**
- UTF-8 encoded
- one structured artifact per source PDF
- canonical top-level section keys only
- no nested `sections` object
- no mixed-case legacy field names

---

## 3. Embedding bundle schema (authoritative)

**Discovery rule**

Embedding bundles are recursively discoverable under:

```text
data/embeddings/<route>/...
```

**Required keys**

| Key | Type | Description |
|---|---|---|
| `doc_id` | scalar string | Stable document identifier derived from source PDF path |
| `route` | scalar string | Route name |
| `section_labels` | 1D array (`object`) | Labels per embedding |
| `embeddings` | 2D array (`float32`) | Shape `(n_sections, 768)` |
| `source_path` | scalar string | Path to structured source artifact |

**Current implementation**
- one embedding vector per document
- `section_labels = ["document"]`
- `embeddings.shape = (1, 768)`

**Constraints**
- `embeddings.ndim == 2`
- `embeddings.shape[1] == 768`
- dtype must be `float32`
- values must be finite
- `len(section_labels) == embeddings.shape[0]`
- `doc_id` must be derived from source PDF path, not structured JSON path

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
| `epoch_counts` | 1D integer array | Counts per epoch |
| `epoch_centroids` | 2D array (`float32`) | Shape `(N, 768)` |
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

## 5. Year-resolution contract

Resolution precedence:
1. `manifest_row["year"]` when available
2. explicit legacy filename mapping from `data/manifests/legacy_filename_year_map.csv`
3. supported filename parsing from `bins/s04_utils/year_resolution.py`
4. supported parent-directory parsing from `bins/s04_utils/year_resolution.py`
5. fail fast if unresolved

**Operational rules**
- unsupported filenames must not silently guess a year
- manifest year remains authoritative when available
- parent-directory parsing is a supported fallback for admitted year-bucket modern files whose filenames do not themselves contain a 4-digit year

**Validated example**

```text
data/raw/Route_A_Modern/2024/10.5032_jae.v65i4.2828.pdf -> 2024
```

---

## 6. Epoch schema

**Configuration**
- `EPOCH_WIDTH = 5`
- `BASE_YEAR = 1960`

**Mapping rule**

```python
epoch_start = year - ((year - 1960) % 5)
epoch_end   = epoch_start + 4
```

**Examples**
- `1960 -> 1960-1964`
- `1965 -> 1965-1969`
- `2000 -> 2000-2004`
- `2024 -> 2020-2024`
- `2026 -> 2025-2029`

---

## 7. Manifest schema

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

## 8. Metrics eligibility logic

A document is eligible for metrics if:
- `structured_status == success`
- and
  - `embedding_status == success`
  - or an embedding bundle exists on disk

This preserves manifest-first behavior while allowing safe fallback detection when status writeback lags behind artifact persistence.

---

## 9. Cross-artifact relationships

### Document flow
`PDF -> Structured JSON -> Embedding Bundle -> MetricRecord(s) -> Metrics Artifact`

### Identity propagation
- `doc_id` originates from the PDF path
- it is preserved across all stages
- it must remain stable across manifest integration and analysis execution

### Temporal injection
- `year` originates from the manifest
- `year` is not treated as a trusted Phase 5 source when stored elsewhere
- `year` is applied during metrics computation through the manifest join

---

## 10. Validation invariants

The pipeline is valid only if all of the following hold.

### Structural
- structured count equals embedding count for the validated legacy corpus

### Schema
- embedding bundles pass validation
- metrics artifacts pass validation

### Metrics
- each artifact loads without error
- `epoch_labels` are sorted
- `epoch_counts > 0`

### Current validated temporal state
- `Route_A_Modern` epoch labels: `['2000-2004', '2005-2009', '2010-2014', '2015-2019', '2020-2024', '2025-2029']`
- `Route_A_Modern` innovation-velocity count: `5`
- `Route_A_Modern` source embedding file count: `10`
- `Route_B_Legacy` epoch labels: `['1960-1964', '1965-1969']`
- `Route_B_Legacy` innovation-velocity count: `1`
- legacy structured / embedding parity: `149 / 149`

---

## 11. Phase 6 reporting output locations

### Backend analysis outputs
- `analysis_outputs/summaries/`
- `analysis_outputs/tables/`
- `analysis_outputs/figures/`

### Manuscript-facing outputs
- `manuscript/paper/tables/`
- `manuscript/paper/figures/`

These are downstream reporting surfaces and do not replace the authoritative route-level metrics artifacts stored under `data/metrics/`.

---

## 12. Phase 6 reporting artifacts

### Descriptive summary outputs
- `analysis_outputs/summaries/Route_A_Modern_summary.md`
- `analysis_outputs/summaries/Route_B_Legacy_summary.md`

### Machine-readable table exports
- `analysis_outputs/tables/Route_A_Modern_epoch_summary.csv`
- `analysis_outputs/tables/Route_A_Modern_innovation_velocity.csv`
- `analysis_outputs/tables/Route_B_Legacy_epoch_summary.csv`
- `analysis_outputs/tables/Route_B_Legacy_innovation_velocity.csv`

### Backend figure exports
- `analysis_outputs/figures/Route_A_Modern_epoch_dispersion.png`
- `analysis_outputs/figures/Route_A_Modern_innovation_velocity.png`
- `analysis_outputs/figures/Route_B_Legacy_epoch_dispersion.png`
- `analysis_outputs/figures/Route_B_Legacy_innovation_velocity.png`

### APA manuscript outputs
- `manuscript/paper/tables/Table_1_epoch_summary.md`
- `manuscript/paper/tables/Table_2_innovation_velocity.md`
- `manuscript/paper/figures/Figure_1_epoch_dispersion.png`
- `manuscript/paper/figures/Figure_1_epoch_dispersion.md`
- `manuscript/paper/figures/Figure_2_innovation_velocity.png`
- `manuscript/paper/figures/Figure_2_innovation_velocity.md`

### Reporting constraint
All reporting-facing artifacts are governed by mandatory APA 7 compliance.

---

## 13. Current state

The schema is now:
- consistent with the validated widened Route A state
- aligned to mixed flat and year-bucket raw modern storage
- aligned to recursive embedding discovery
- aligned to the active Phase 6 reporting stack
- stable for restrained descriptive and manuscript-facing analysis

---

## 14. Control references
- `AUDIT_CONTEXT.md`
- `RESEARCH_LOG.md`
- `DEBUGGING_AUDIT_2026-03-22.md`
- `METHODS_PIPELINE.md`
- `SCHEMA_CONTRACT.json`
