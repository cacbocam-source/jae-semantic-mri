# Computational Methods Pipeline

## Semantic MRI of Agricultural Education

Version: 2.2
Date: 2026-03-20
Status: Supplemental methods summary aligned to the stabilized Phase 5 state and the active beta pilot epoch protocol

---

# 1. Computational Environment

All analyses were conducted on an Apple Silicon workstation equipped with an M3 Max processor and 64 GB of unified memory.

Embedding computation used Apple Metal Performance Shaders through:

```python
DEVICE = "mps"
```

Primary data storage was provided through the NVMe-backed project root:

```text
/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
```

The embedding model was:

```text
nomic-ai/nomic-embed-text-v1.5
```

Key model/runtime properties:
- 768-dimensional embeddings
- 8192-token context window
- worker pool constrained to `MAX_WORKERS = 8`

Validated environment capture:
- `pyproject.toml`
- `requirements-lock.txt`

---

# 2. Corpus Processing Architecture

The analysis repository is organized around:
1. extraction and cleaning
2. segmentation and structured export
3. section embedding generation
4. route-level vector metrics

Acquisition is external to the active analysis runtime spine, but the next-study beta pilot protocol is now defined for controlled live-manuscript intake.

---

---

# 2. Corpus Processing Architecture (Updated)

The analysis pipeline operates under a dual ingestion schema:

- Route_A_Modern (filename-based year resolution)
- Route_B_Legacy (directory-based year resolution)

During Phase 3 (structured export), the system performs:

1. manifest seeding (requires temporary year inference bridge)
2. filtering of non-temporal artifacts (no resolvable year)
3. section-level JSON export
4. embedding generation
5. route-level metrics aggregation

Important implementation note:

- `write_section_export()` may re-access raw PDFs and re-trigger OCR
- therefore, the pipeline is not strictly single-pass between bins
- this does not affect correctness but introduces computational redundancy

Non-temporal documents are excluded prior to processing and do not contribute to metrics.

---

# 3. Existing Validated Benchmark Corpus

The current implemented and validated pipeline proofs used a benchmark corpus under:

```text
data/raw/Route_A_Modern/
data/raw/Route_B_Legacy/
```

These files support the current regression tests and Phase 2–5 validation surface.

---

# 4. Beta Pilot Epoch Intake Protocol

The active next-study intake rule for live manuscripts is:

```text
data/raw_pdfs/<route>/<year>/<filename>.pdf
```

Operational rules:
- each manuscript must resolve to exactly one route and one year
- manuscripts are not stored by epoch folder
- unresolved route/year items are quarantined
- epoch assignment is derived later from year

Pilot sample logic is documented in `docs/BETA_PILOT_EPOCH_PROTOCOL.md`.

Recommended pilot characteristics:
- both routes represented
- multiple years if available
- heterogeneous PDF characteristics
- enough corpus breadth to test whether multi-epoch coverage emerges in one or both routes

---

# 5. Extraction and Cleaning

Source manuscripts are processed through `bins/s02_processor/`.

Implemented behaviors:
- digital extraction where native text is available
- OCR fallback for scan-derived legacy materials
- reference-section truncation before downstream analysis
- route-aware preparation for later segmentation

---

# 6. Segmentation and Structured Export

The operational segmentation output relevant to downstream analysis is:
- `A_intro`
- `A_methods`
- `A_results`

These are exported as flattened top-level JSON fields in structured artifacts under:

```text
data/structured/<route_name>/<doc_id>.json
```

Year resolution is delegated to `bins/s04_utils/year_resolution.py`.

Year precedence:
1. manifest year when available
2. explicit legacy filename map
3. supported filename parsing
4. fail fast

---

# 7. Phase 4 — Section Embedding Generation

Input:
- validated structured JSON artifacts from `data/structured/<route_name>/`

Output:
- validated embedding bundles at:

```text
data/embeddings/<route_name>/<doc_id>.npz
```

Bundle schema:
- `doc_id`
- `route`
- `section_labels`
- `embeddings`
- `source_path`

---

# 8. Phase 5 — Vector Metrics

Phase 5 is implemented in:

```text
bins/s03_analysis/metrics.py
```

Inputs:
- validated Phase 4 embedding artifacts
- manifest metadata from `data/manifests/pipeline_manifest.csv`

Temporal join:
- `year` is injected from the manifest row
- `year` is not read from the embedding bundle

Outputs:
- route-level metrics artifacts written to:

```text
data/metrics/<route_name>/metrics.npz
```

Current interpretation boundary:
- the validated current artifact state is singleton-epoch for both routes
- therefore current analysis is descriptive/readiness-oriented rather than substantively inferential

---

# 9. Beta Readiness Gate Before Broader Phase 6 Work

Before broader inferential Phase 6 work is justified, the beta pilot must demonstrate:
- deterministic intake under route/year organization
- manifest integrity
- successful Phases 2–5 execution on the live-manuscript pilot corpus
- route-level metrics artifact generation and validation
- evidence that epoch coverage expands beyond the current singleton-route artifact condition if the expanded corpus allows it

---

# 10. Reproducibility and Auditability

The computational pipeline incorporates:
- deterministic filesystem layout
- explicit stage artifacts
- manifest-driven execution tracking
- validation layers for schema conformity
- typed artifact boundaries
- route-level output persistence
- synchronized control documentation

Current handoff/control docs:
- `AUDIT_CONTEXT.md`
- `RESEARCH_LOG.md`
- `audit.md`
- `REPO_KEEP_ARCHIVE_MAP.md`
- `docs/BETA_PILOT_EPOCH_PROTOCOL.md`

# Computational Methods Pipeline

## Semantic MRI of Agricultural Education

Version: 2.2
Date: 2026-03-20
Status: Supplemental methods summary aligned to the stabilized Phase 5 state and the active beta pilot epoch protocol

---

# 1. Computational Environment

All analyses were conducted on an Apple Silicon workstation equipped with an M3 Max processor and 64 GB of unified memory.

Embedding computation used Apple Metal Performance Shaders through:

```python
DEVICE = "mps"
```

Primary data storage was provided through the NVMe-backed project root:

```text
/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
```

The embedding model was:

```text
nomic-ai/nomic-embed-text-v1.5
```

Key model/runtime properties:
- 768-dimensional embeddings
- 8192-token context window
- worker pool constrained to `MAX_WORKERS = 8`

Validated environment capture:
- `pyproject.toml`
- `requirements-lock.txt`

---

# 2. Corpus Processing Architecture

The analysis repository is organized around:
1. extraction and cleaning
2. segmentation and structured export
3. section embedding generation
4. route-level vector metrics

Acquisition is external to the active analysis runtime spine, but the next-study beta pilot protocol is now defined for controlled live-manuscript intake.

---

# 3. Existing Validated Benchmark Corpus

The current implemented and validated pipeline proofs used a benchmark corpus under:

```text
data/raw/Route_A_Modern/
data/raw/Route_B_Legacy/
```

These files support the current regression tests and Phase 2–5 validation surface.

---

# 4. Beta Pilot Epoch Intake Protocol

The current executed intake rule for live manuscripts is:

```text
data/raw/<route>/<year>/<filename>.pdf
```

Historical note:
- earlier beta-protocol planning referenced `data/raw_pdfs/<route>/<year>/<filename>.pdf`
- the successful 1960–1969 legacy acquisition batch was promoted into `data/raw/`

Operational rules:
- each manuscript must resolve to exactly one route and one year
- manuscripts are not stored by epoch folder
- unresolved route/year items are quarantined
- epoch assignment is derived later from year

Pilot sample logic is documented in `docs/BETA_PILOT_EPOCH_PROTOCOL.md`.

Recommended pilot characteristics:
- both routes represented
- multiple years if available
- heterogeneous PDF characteristics
- enough corpus breadth to test whether multi-epoch coverage emerges in one or both routes

---

# 5. Extraction and Cleaning

Source manuscripts are processed through `bins/s02_processor/`.

Implemented behaviors:
- digital extraction where native text is available
- OCR fallback for scan-derived legacy materials
- reference-section truncation before downstream analysis
- route-aware preparation for later segmentation

---

# 6. Segmentation and Structured Export

The operational segmentation output relevant to downstream analysis is:
- `A_intro`
- `A_methods`
- `A_results`

These are exported as flattened top-level JSON fields in structured artifacts under:

```text
data/structured/<route_name>/<doc_id>.json
```

Year resolution is delegated to `bins/s04_utils/year_resolution.py`.

Year precedence:
1. manifest year when available
2. explicit legacy filename map
3. supported filename parsing
4. fail fast

---

# 7. Phase 4 — Section Embedding Generation

Input:
- validated structured JSON artifacts from `data/structured/<route_name>/`

Output:
- validated embedding bundles at:

```text
data/embeddings/<route_name>/<doc_id>.npz
```

Bundle schema:
- `doc_id`
- `route`
- `section_labels`
- `embeddings`
- `source_path`

---

# 8. Phase 5 — Vector Metrics

Phase 5 is implemented in:

```text
bins/s03_analysis/metrics.py
```

Inputs:
- validated Phase 4 embedding artifacts
- manifest metadata from `data/manifests/pipeline_manifest.csv`

Temporal join:
- `year` is injected from the manifest row
- `year` is not read from the embedding bundle

Outputs:
- route-level metrics artifacts written to:

```text
data/metrics/<route_name>/metrics.npz
```

Current interpretation boundary:
- the validated current artifact state is singleton-epoch for both routes
- therefore current analysis is descriptive/readiness-oriented rather than substantively inferential

---

# 9. Beta Readiness Gate Before Broader Phase 6 Work

Before broader inferential Phase 6 work is justified, the beta pilot must demonstrate:
- deterministic intake under route/year organization
- manifest integrity
- successful Phases 2–5 execution on the live-manuscript pilot corpus
- route-level metrics artifact generation and validation
- evidence that epoch coverage expands beyond the current singleton-route artifact condition if the expanded corpus allows it

---

# 10. Reproducibility and Auditability

The computational pipeline incorporates:
- deterministic filesystem layout
- explicit stage artifacts
- manifest-driven execution tracking
- validation layers for schema conformity
- typed artifact boundaries
- route-level output persistence
- synchronized control documentation

Current handoff/control docs:
- `AUDIT_CONTEXT.md`
- `RESEARCH_LOG.md`
- `audit.md`
- `REPO_KEEP_ARCHIVE_MAP.md`
- `docs/BETA_PILOT_EPOCH_PROTOCOL.md`


---

# 11. Legacy Acquisition Execution Update

The 1960–1969 legacy decade batch has now been executed through the acquisition layer.

Verified operational result:
- 149 legacy PDFs downloaded into staging
- 149 legacy PDFs promoted into `data/raw/Route_B_Legacy/<year>/`
- 149 manifest rows added to `data/manifests/pipeline_manifest.csv`

Methodological implication:
- the project has moved from planned beta intake to a real executed legacy decade batch
- the next active methods step is downstream processing of the newly added legacy rows through extraction, structured export, embeddings, and regenerated route-level metrics
