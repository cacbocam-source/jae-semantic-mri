# DEBUGGING AUDIT — 2026-03-22
## JAE_Legacy_Audit Pipeline Stabilization

## Purpose

This document records the debugging and stabilization sequence required to bring the
JAE_Legacy_Audit pipeline into a valid, reproducible, analysis-ready state for the
1960–1969 legacy corpus.

This is an engineering audit artifact, not a methods narrative. Its function is to:
- preserve exact failure history
- distinguish root causes from symptoms
- document file-level corrections
- record terminal validation evidence for closure

---

## Scope

This audit covers the following pipeline layers:

- Bin 02 processing
- Bin 03 structured export
- embedding generation
- metrics aggregation
- manifest eligibility logic

The audit window spans the stabilization of the 1960–1969 legacy batch through final
epoch-level metrics validation.

---

## Initial Symptoms

The following symptoms were observed during the debugging sequence.

### 1. Analyze-phase import failure
The analysis phase failed during startup due to an unresolved import dependency.

Observed symptom:
- `cannot import name 'infer_year_from_path'`

### 2. Missing `infer_year_from_path`
The analysis orchestrator still referenced `infer_year_from_path` after the function
had been removed from the section export layer.

Observed symptom:
- stale import in `bins/s03_analysis/orchestrator.py`

### 3. Embedder not wired
Structured export completed, but embeddings were not being generated because the
embedder stage was not actually invoked by the analysis orchestrator.

Observed symptom:
- empty `data/embeddings/Route_B_Legacy/`
- no `[EMBED]` lines in terminal output

### 4. Incorrect embedding schema
The embedder wrote `.npz` bundles that did not conform to the schema expected by the
metrics pipeline.

Observed symptom:
- embedding bundles missing required keys:
  - `embeddings`
  - `route`
  - `section_labels`
  - `source_path`

### 5. Metrics collapsing to one epoch
Metrics output initially loaded, but produced only one epoch and zero innovation
transitions.

Observed symptom:
- `epoch_labels: 1`
- `innovation_velocity: 0`

---

## Root Causes

The following root causes were confirmed.

### 1. Stale import dependency
`bins/s03_analysis/orchestrator.py` retained an import of `infer_year_from_path`
after that function no longer existed in `section_export.py`.

### 2. Year-resolution mismatch across routes
The corpus uses two ingestion patterns:

- `Route_A_Modern` → year encoded in filename (`2026.pdf`)
- `Route_B_Legacy` → year encoded in directory path (`1960/...`)

A single-mode year resolver failed on one or both routes until a hybrid resolver was
introduced.

### 3. Non-temporal artifact contamination risk
`Vol1_1.pdf` existed in raw legacy storage without a resolvable year and therefore
could contaminate processing, structured output, embeddings, and metrics if not
explicitly excluded.

### 4. `make_doc_id` called on JSON path instead of PDF path
The embedder originally derived `doc_id` from the structured JSON path rather than
the original PDF path. This broke path assumptions inside the identity layer and
caused failures during analysis.

### 5. Embedding bundles not matching metrics schema
The embedder initially wrote simplified bundles (e.g. `embedding`, `source`) instead
of the schema contract required by metrics:

- `doc_id`
- `route`
- `section_labels`
- `embeddings`
- `source_path`

### 6. Metrics loader assuming flat embedding paths
The metrics phase originally looked for embedding bundles at:

- `data/embeddings/<route>/<doc_id>.npz`

but legacy embeddings were actually stored under nested year directories:

- `data/embeddings/Route_B_Legacy/<year>/<doc_id>.npz`

This caused incorrect or incomplete metrics aggregation.

### 7. Manifest eligibility lag for Phase 5
The Phase 5 metrics runner depended on manifest eligibility logic that could exclude
valid documents when embeddings existed on disk but `embedding_status` was not yet
backfilled correctly in the manifest.

---

## Files Modified

The following files were modified during stabilization.

### 1. `bins/s02_processor/orchestrator.py`
Changes:
- added year-resolution filtering
- excluded non-temporal artifacts before processing
- aligned Bin 02 filtering behavior with Bin 03

### 2. `bins/s03_analysis/orchestrator.py`
Changes:
- removed stale import dependency
- added robust year filtering for analysis phase
- excluded non-temporal artifacts
- wired structured export to embedding generation
- passed original PDF path into embedder for stable `doc_id` generation

### 3. `bins/s03_analysis/embedder.py`
Changes:
- corrected input semantics (JSON path for content, PDF path for identity)
- rebuilt output bundle schema to match metrics contract
- enforced one-file-per-document behavior
- preserved structured directory mirroring inside embeddings tree

### 4. `bins/s03_analysis/metrics.py`
Changes:
- corrected embedding bundle lookup to support nested year directories
- preserved route-level processing
- restored correct epoch grouping behavior
- rebuilt artifact typing to satisfy schema and static analysis constraints

### 5. `bins/s04_utils/manifest_manager.py`
Changes:
- removed duplicate pasted content
- hardened metrics eligibility logic
- allowed Phase 5 metrics eligibility when embedding bundles exist on disk even if
  manifest embedding status lags
- preserved manifest-first behavior while adding safe fallback detection

---

## Correction Sequence Summary

The debugging sequence proceeded in the following order.

1. Restored authoritative state from uploaded audit and repo context.
2. Verified raw corpus and partial prior artifacts.
3. Ran Bin 02 processing and confirmed legacy extraction throughput.
4. Repaired stale Bin 03 import dependency.
5. Repaired year-resolution logic across modern and legacy routes.
6. Excluded non-temporal legacy artifact (`Vol1_1.pdf`) from downstream stages.
7. Repaired analysis orchestrator to actually invoke embedding generation.
8. Repaired embedder path semantics and `doc_id` provenance.
9. Rebuilt embedding output schema to satisfy metrics contract.
10. Repaired metrics bundle lookup for nested year directories.
11. Repaired Phase 5 manifest eligibility fallback logic.
12. Regenerated metrics and confirmed correct epoch aggregation.

---

## Final Validation Evidence

The following terminal-verified evidence closed the debugging cycle.

### 1. Structured / embedding cardinality
- structured JSON files: `149`
- embedding bundles: `149`

Validated via shell count:
- `ls data/structured/Route_B_Legacy/*/*.json | wc -l`
- `ls data/embeddings/Route_B_Legacy/*/*.npz | wc -l`

Result:
- `149 / 149`

### 2. Metrics keys load correctly
The Route_B_Legacy metrics artifact successfully loaded and exposed the expected keys:

- `corpus_name`
- `route_name`
- `epoch_labels`
- `epoch_counts`
- `epoch_centroids`
- `semantic_dispersion`
- `innovation_velocity`
- `source_embedding_files`
- `created_at_utc`
- `metric_version`

### 3. Epoch grouping correct
Final metrics validation showed:

- `epoch_labels: 2`
- `innovation_velocity: 1`

Expected epoch labels:
- `1960-1964`
- `1965-1969`

This matches:
- corpus time span `1960–1969`
- configured `EPOCH_WIDTH = 5`

### 4. Final freeze commits
Engineering freeze commits recorded during stabilization:

- `f77b0bf` — `SYSTEM FREEZE: JAE Legacy 1960–1969 stabilized`
- `be85846` — `FINAL FREEZE: pipeline validated, embeddings complete, cardinality verified`

A final documentation freeze commit should be added after all `.md` updates are applied.

---

## Final State

At closure, the system satisfied the following conditions:

- processing phase operational
- analysis phase operational
- embeddings generated per document
- embedding schema aligned with metrics contract
- metrics regenerated successfully
- epoch aggregation valid
- non-temporal contamination excluded
- manifest compatibility restored
- cardinality invariant satisfied
- system in reproducible post-freeze state

---

## Remaining Recommended Actions

These are not blockers, but should be completed after this audit.

1. Update canonical documentation:
   - `AUDIT_CONTEXT.md`
   - `RESEARCH_LOG.md`
   - `METHODS_PIPELINE.md`
   - `DATA_SCHEMA.md`
   - `ARCHITECTURE.md`
   - `RESEARCH_COMPLIANCE.md`

2. Add cross-reference notes in:
   - `AUDIT_CONTEXT.md`
   - `RESEARCH_LOG.md`

3. Create documentation freeze commit after all `.md` updates are merged.

---

## Cross-Reference Note (recommended)

Add this note to `AUDIT_CONTEXT.md` and `RESEARCH_LOG.md`:

> See `DEBUGGING_AUDIT_2026-03-22.md` for the complete stabilization and validation record covering Bin 02, Bin 03, embedding schema correction, metrics aggregation repair, and final freeze validation.

---