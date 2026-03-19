# Data Schema

## Semantic MRI of Agricultural Education Pipeline

Schema Version: 2.1  
Date: 2026-03-19  
Status: Supplemental schema reference aligned to implemented Phase 5 state

---

# 1. Scope

This document defines the current documentation-facing data schema for the production pipeline.

Current implemented coverage:
- corpus storage structure
- structured export artifacts
- deterministic year resolution
- Phase 4 embedding bundles
- manifest-driven execution tracking
- Phase 5 route-level metrics artifacts

Current-state authority remains:
- `AUDIT_CONTEXT.md` for operational status
- `SCHEMA_CONTRACT.json` for machine-readable contract summary

---

# 2. Operational Data Layout

All data paths are repo-relative and assumed to resolve under the NVMe project root.

```text
data/
│
├── raw/
│   ├── Route_A_Modern/
│   └── Route_B_Legacy/
│
├── processed/
│   ├── Route_A_Modern/
│   └── Route_B_Legacy/
│
├── structured/
│   ├── Route_A_Modern/
│   └── Route_B_Legacy/
│
├── embeddings/
│   ├── Route_A_Modern/
│   └── Route_B_Legacy/
│
├── metrics/
│   ├── Route_A_Modern/
│   └── Route_B_Legacy/
│
├── manifests/
│   ├── pipeline_manifest.csv
│   └── legacy_filename_year_map.csv
│
└── testing/
    └── doi_abstracts_2021_2026/
```

Directory purposes:
- `raw/` — source PDFs or equivalent corpus inputs
- `processed/` — cleaned text intermediates
- `structured/` — canonical structured JSON exports
- `embeddings/` — validated Phase 4 embedding bundles
- `metrics/` — route-level Phase 5 metrics artifacts
- `manifests/` — execution tracking, temporal join metadata, and explicit legacy filename year mappings
- `testing/` — isolated non-production validation corpus

---

# 3. Routes

Canonical route names:
- `Route_A_Modern`
- `Route_B_Legacy`

Route semantics:
- `Route_A_Modern` — modern manuscripts processed with modern-route segmentation logic
- `Route_B_Legacy` — legacy manuscripts processed with legacy-route segmentation logic

---

# 4. Processed Text Outputs

Cleaned text outputs are stored under:

```text
data/processed/<route_name>/
```

One cleaned text artifact is written per source manuscript.

Role in pipeline:
- intermediate output of extraction and cleaning
- direct input to segmentation and structured export
- not a final analysis artifact

---

# 5. Structured Export Schema

Structured JSON artifacts are stored under:

```text
data/structured/<route_name>/<doc_id>.json
```

Canonical required fields:
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

Section semantics:
- `A_intro` — introduction section text
- `A_methods` — methods section text
- `A_results` — results section text

Important exclusions:
- `A_TAK` is not part of the structured export contract
- nested `sections` payloads are not valid
- mixed-case legacy keys such as `A_Intro`, `A_Methods`, and `A_Results` are not valid

---

# 6. Year Resolution Contract

Structured export year values must resolve deterministically.

Resolution precedence:
1. manifest `year` when available
2. explicit legacy filename mapping from:
   - `data/manifests/legacy_filename_year_map.csv`
3. supported filename parsing
4. fail fast if unresolved

Supported filename parsing currently includes:
- `JAE_YYYY_NNNN.pdf`
- bare-year filenames such as `2026.pdf`
- filenames containing exactly one valid standalone 4-digit year in the configured year range

Important rules:
- unsupported filenames must not silently guess a year
- legacy filename exceptions belong in the explicit mapping CSV, not as hardcoded conditionals inside active export code
- manifest metadata remains authoritative when available

---

# 7. Embedding Bundle Schema

Phase 4 embedding bundles are stored under:

```text
data/embeddings/<route_name>/<doc_id>.npz
```

Canonical bundle fields:
- `doc_id`
- `route`
- `section_labels`
- `embeddings`
- `source_path`

Bundle semantics:
- the artifact stores section embeddings, not a single manuscript-level vector
- `section_labels` identifies which canonical sections were embedded
- `embeddings` stores the aligned section embedding array
- `source_path` records the originating structured artifact or source lineage used by the stage

Important constraint:
- `year` is not a bundle contract field for Phase 5 consumption
- temporal metadata is joined later from the manifest

---

# 8. Manifest Schema

Operational manifest path:

```text
data/manifests/pipeline_manifest.csv
```

The manifest is the authoritative execution-tracking table for multi-stage runs.

Minimum operational semantics:
- one row per document
- stable document identity
- route assignment
- publication year
- stage-status tracking
- source-path tracking
- error-state tracking

Stage status fields:
- `extract_status`
- `structured_status`
- `embedding_status`
- `metrics_status`

Allowed status values:
- `pending`
- `success`
- `failed`
- `skipped`

Important rules:
- `year` for metrics grouping is injected via manifest-row join
- `metrics_status` must not be marked `success` until route-level artifact persistence succeeds

Explicit legacy year map path:

```text
data/manifests/legacy_filename_year_map.csv
```

This auxiliary CSV is not a replacement for the manifest. It exists only to support deterministic year resolution for legacy filenames when manifest metadata is not available at the call site.

---

# 9. Phase 5 Metrics Artifact Contract

Phase 5 metrics artifacts are stored under:

```text
data/metrics/<route_name>/metrics.npz
```

Granularity:
- route-level
- not document-level

Contract semantics:
- one artifact summarizes epoch-level metrics for one route
- epoch grouping uses manifest year values
- artifact creation consumes validated Phase 4 embedding bundles
- artifact persistence must succeed before manifest success writeback

Documentation-facing interpretation:
- the artifact contains route-level epoch metrics and associated serialized arrays
- downstream code should treat `MetricsArtifact` as the authoritative implementation boundary for the internal array layout

---

# 10. Temporal Grouping Rules

Temporal grouping uses deterministic 5-year epochs.

Range:
- 1960–2026

Examples:
- 1960–1964
- 1965–1969
- 1970–1974

Important rules:
- epoch assignment for Phase 5 is based on manifest `year`
- epoch assignment is not derived from embedding bundle contents
- unsupported filenames must not silently determine epoch membership by guessing a year

---

# 11. Testing Corpus Isolation

Testing corpus location:

```text
data/testing/doi_abstracts_2021_2026/
```

The testing corpus is intentionally separate from the production manuscript corpus.

Do not:
- merge testing files into production route directories
- treat testing metrics as production metrics
- use testing artifacts as canonical production documentation examples unless explicitly labeled as testing

---

# 12. Data Integrity Rules

The pipeline enforces the following documentation-facing integrity rules:
- each `doc_id` must be unique within the production corpus
- every production artifact must map back to a manifest-tracked document
- structured export must use flattened top-level section fields
- year resolution must follow the documented precedence order
- embedding bundles must match the validated Phase 4 schema
- metrics artifacts must be route-level outputs
- manifest stage state must reflect actual artifact persistence status

---

# 13. Identifier Semantics

`doc_id` is a stable pipeline-generated document identifier.

Consumer rule:
- treat `doc_id` as an opaque identifier
- do not assume semantic fields can be safely parsed from the identifier string
- use manifest metadata for year and route semantics rather than inferring them from file names when manifest data is available

---

# 14. Versioning Rule

Any change to the documentation-facing contract for:
- structured export fields
- year-resolution precedence
- legacy filename mapping rules
- embedding bundle fields
- manifest stage semantics
- metrics artifact granularity or path semantics

must update:
- this file
- `SCHEMA_CONTRACT.json`
- any other affected canonical documentation
