# RESEARCH LOG

Status: Canonical chronological session log  
Current-state authority: `AUDIT_CONTEXT.md`  
Historical workflow supplement: `audit.md`

---

## 2026-03-10 — Infrastructure build established

Work completed:
- created the NVMe-backed project workspace
- established the repository skeleton under the project root
- initialized service-bin package structure
- created `config.py`
- created `main.py`
- added startup and health-check scripts

Operational result:
- deterministic repository layout established
- Apple Silicon / MPS execution environment confirmed
- project ready for extraction-stage development

---

## 2026-03-14 — Extraction pipeline implemented

Work completed:
- implemented digital extraction
- implemented OCR fallback
- implemented cleaning and reference truncation
- implemented era-aware segmentation
- validated benchmark processing on one modern file and one legacy file

Key outputs validated:
- `data/processed/Route_A_Modern/2026.txt`
- `data/processed/Route_B_Legacy/Vol1_1.txt`

Operational result:
- Phase 2 extraction path became functional across modern and legacy routes

---

## 2026-03-14 — Manifest/ledger groundwork added

Work completed:
- added deterministic corpus-tracking infrastructure
- established document-level execution tracking for downstream stages

Operational result:
- corpus items became trackable across multi-stage execution
- later manifest-driven Phase 3–5 execution was enabled by this groundwork

---

## 2026-03-15 — Benchmark regression coverage completed

Work completed:
- implemented benchmark regression tests
- validated modern extraction route
- validated legacy extraction route
- validated segmentation stability
- validated corpus registration behavior

Operational result:
- benchmark corpus became a stable regression guard for future pipeline changes

---

## 2026-03-15 — Structured export layer completed

Work completed:
- implemented `bins/s03_analysis/section_export.py`
- implemented `bins/s03_analysis/orchestrator.py`
- added persistent structured JSON export for segmented manuscripts

Outputs validated:
- `data/structured/Route_A_Modern/2026.json`
- `data/structured/Route_B_Legacy/Vol1_1.json`

Operational result:
- Phase 3 structured artifacts became available for embedding

---

## 2026-03-18 — Structured schema normalization and shared utility hardening

Work completed:
- normalized structured export to canonical top-level section fields:
  - `A_intro`
  - `A_methods`
  - `A_results`
- removed nested structured export assumptions
- reinforced schema handling through:
  - `bins/s04_utils/schemas.py`
  - `bins/s04_utils/validators.py`
  - `bins/s04_utils/artifacts.py`
  - `bins/s04_utils/manifest_manager.py`
- aligned tests to reject mixed-case legacy keys and nested export regressions

Operational result:
- early Phase 4 “no embeddable section text” failures were resolved at the schema/export boundary
- structured export and embedding inputs became contract-stable

---

## 2026-03-18 — Embedding bundles validated against real structured artifacts

Work completed:
- verified successful embedding generation from real structured JSON artifacts
- confirmed embedding bundles use the real schema:
  - `doc_id`
  - `route`
  - `section_labels`
  - `embeddings`
  - `source_path`

Operational result:
- Phase 4 became a stable production input for Phase 5 metrics execution

---

## 2026-03-18 — Phase 5 real-artifact execution completed

Primary file:
- `bins/s03_analysis/metrics.py`

Work completed:
- bound Phase 5 ingestion to the real Phase 4 `.npz` schema
- enforced embedding-bundle validation for:
  - `doc_id`
  - `route`
  - `section_labels`
  - `embeddings`
  - `source_path`
- enforced manifest-row `year` join
- implemented route-level metrics artifact construction
- implemented route-level artifact persistence at:
  - `data/metrics/<route_name>/metrics.npz`
- enforced success writeback only after artifact persistence
- executed full Phase 5 run on real production artifacts

Validation completed:
- one-route real-artifact validation passed
- full executor run passed for:
  - `Route_A_Modern`
  - `Route_B_Legacy`

Artifacts written:
- `data/metrics/Route_A_Modern/metrics.npz`
- `data/metrics/Route_B_Legacy/metrics.npz`

Manifest summary after run:
- `metrics_success=2`
- `metrics_failed=0`
- `metrics_pending=0`

Operational result:
- Phase 5 is complete
- metrics artifacts are route-level, not document-level
- Phase 5 no longer resumes at schema integration or executor wiring

---

## 2026-03-19 — Baseline contract repair and post-Phase-5 validation hardening completed

Work completed:
- identified live contract drift between current docs / `metrics.py` and the utility layer
- restored `MetricsArtifact` in `bins/s04_utils/artifacts.py`
- restored metrics-stage manifest wrapper helpers in `bins/s04_utils/manifest_manager.py`
- restored embedding-bundle key constants in `bins/s04_utils/schemas.py`
- reapplied hardened `bins/s03_analysis/metrics.py`
- activated post-Phase-5 validation helpers including artifact reload/validate behavior and route-level structural checks
- added and passed `tests/test_post_phase5_validation.py`

Validation completed:
- `python3 -m unittest tests/test_post_phase5_validation.py` → passed
- `python3 tests/test_benchmarks.py` → passed
- `python3 tests/test_section_exports.py` → passed
- `scripts/startup_check.sh` → `SYSTEM STATUS: READY`
- `scripts/doctor.sh` → `SYSTEM STATUS: READY`

Operational result:
- baseline contract boundaries were repaired in the load-bearing utility layer
- post-Phase-5 validation became live and verified against the current repo state

---

## 2026-03-19 — Route-level metrics artifacts revalidated after hardening

Read-only validation completed through the active metrics artifact boundary.

Verified artifact summaries:

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

Manifest result:
- `metrics_success=2`
- `metrics_failed=0`
- `metrics_pending=0`
- no Phase 5-eligible manifest rows remained at rerun time

Operational result:
- both route-level metrics artifacts remained structurally valid
- current state supported descriptive reporting and readiness work, not substantive temporal inference

---

## 2026-03-19 — Cleanup and stabilization pass completed

Work completed:
- reduced stale script surface
- rewrote active environment validation scripts to validate the NVMe root directly
- retired legacy ingest rebuild orchestration from the active workflow
- reduced `bins/s01_ingest/ledger.py` to helper-only compatibility behavior
- restored `MASTER_LEDGER` in `config.py` as compatibility residue only
- removed the dead ingest phase from `main.py`
- added root-level `pyproject.toml`
- captured validated environment in `requirements-lock.txt`

Validation completed:
- `python3 tests/test_benchmarks.py` passed
- `python3 tests/test_section_exports.py` passed
- `python3 tests/test_metrics_contracts.py` returned `0`
- `python3 tests/test_metrics_math.py` returned `0`
- `scripts/startup_check.sh` returned `SYSTEM STATUS: READY`
- `scripts/doctor.sh` returned `SYSTEM STATUS: READY`

Operational result:
- the repo returned to a stable, validated state after cleanup
- the active runtime surface is now clearer and less cluttered

---

## 2026-03-19 — Deterministic year-resolution contract implemented

Primary files:
- `bins/s04_utils/year_resolution.py`
- `bins/s03_analysis/section_export.py`
- `data/manifests/legacy_filename_year_map.csv`

Work completed:
- introduced deterministic year resolution with explicit precedence:
  1. manifest-row `year` when available
  2. explicit legacy filename mapping CSV
  3. supported filename parsing
  4. fail fast if unresolved
- removed benchmark-only hardcoded filename special cases from active export code
- wired `section_export.py` to call `resolve_year(path)`
- added `tests/test_year_resolution.py`

Validation completed:
- year-resolution tests passed
- section export tests passed
- benchmark tests passed

Operational result:
- year resolution is now explicit, deterministic, and portable across future corpus expansion
- unsupported filenames can no longer silently guess a year inside active export code

---

## 2026-03-20 — Beta pilot epoch study protocol formalized

Primary file:
- `docs/BETA_PILOT_EPOCH_PROTOCOL.md`

Work completed:
- defined the beta pilot as a live-manuscript systems-validation study rather than an inferential historical study
- established canonical pilot raw-manuscript organization:
  - `data/raw_pdfs/<route>/<year>/<filename>.pdf`
- defined deterministic route/year intake requirements
- documented quarantine rules for unresolved route/year/path conflicts
- documented intake audit, pipeline execution, post-Phase-5 validation, and pilot closeout workflow
- documented pilot outcomes and Phase 6 decision gate tied to realized epoch coverage

Operational result:
- the next study is now explicitly defined
- future scraper / intake work has a documented route/year corpus contract
- Phase 6 is framed as descriptive/readiness work unless beta ingestion expands route epoch coverage

---

## 2026-03-20 — Beta acquisition run validated modern route and narrowed legacy blocker

Work completed:
- executed live beta acquisition run using the dedicated manuscript download runner
- confirmed 11/11 successful downloads for all rows eligible to run
- confirmed 9/9 successful modern acquisitions from 2000–2024
- confirmed 2/2 successful legacy acquisitions where OJS article IDs were already resolvable
- confirmed the `LEGACY_CUTOFF=2000` route boundary behavior
- added `article_title` support to the beta acquisition manifest flow

Operational result:
- beta runner behavior is validated on real traffic
- unresolved legacy rows were upstream prefill/discovery failures, not runner failures
- the remaining bottleneck was narrow legacy metadata/prefill completion rather than general downloader failure

---

## 2026-03-20 — Legacy acquisition architecture reframed around metadata-prefill queue + controlled downloader

Decision:
- stopped treating abstract/metadata harvesting as a study-data substitute
- adopted metadata harvesting as the front end of the legacy acquisition workflow
- separated the acquisition layer from the stabilized downstream engine

Operational design adopted:
1. metadata prefill queue generation
2. row-level confirmation / manual completion where needed
3. controlled downloader on confirmed rows only
4. staged PDF QC
5. promotion to canonical `data/raw_pdfs/<route>/<year>/`
6. manifest bridge into `data/manifests/pipeline_manifest.csv`
7. rerun of Phases 2–5 on the expanded corpus

Operational result:
- legacy acquisition now had a deterministic workflow boundary
- manual effort was concentrated on ambiguous rows instead of the whole corpus
- the project was explicitly a hybrid system: automated engine plus controlled legacy intake

---

## 2026-03-20 — Old OpenAlex abstract harvester superseded by JAE-aligned acquisition build

Reviewed files:
- `Full_Census_Harvester_v2.py`
- `Journal_Inventory.py`

Findings:
- earlier scripts were standalone abstract text harvesters rather than acquisition-queue builders
- earlier scripts wrote loose `.txt` abstract files outside the current manifest/staging workflow
- earlier scripts were not aligned to the current route/year storage model
- earlier scripts also contained journal inventory conflicts and did not emit the fields required by the beta acquisition flow

Build-out completed:
- defined a shared acquisition contract for route/year assignment, statuses, staging paths, canonical raw-PDF paths, and prefill field names
- rebuilt the OpenAlex harvester as a metadata-prefill queue generator
- added a controlled downloader for confirmed rows
- added a promotion script for staged PDFs
- added a manifest-bridge script for promoted files
- added an atomic walkthrough for operator use

Operational result:
- the abstract-harvest code is no longer treated as an isolated research script
- acquisition tooling is now aligned to the JAE_Legacy_Audit recovery plan and current legacy audit workflows

---

## 2026-03-22 — Full legacy-batch stabilization, metrics repair, and Phase 6 initiation

Completed full stabilization of the JAE_Legacy_Audit pipeline for the 1960–1969 corpus.

### Work completed
- resolved analyze-phase import failure tied to removed `infer_year_from_path`
- implemented robust year inference across modern and legacy routes
- excluded non-temporal artifacts from processing and analysis
- repaired Bin 03 orchestration so embedding generation is invoked during analysis
- corrected embedding `doc_id` provenance to derive from source PDF path
- rebuilt embedding bundle schema to match Phase 5 metrics contract
- corrected metrics discovery over nested legacy embedding directories
- hardened manifest eligibility logic for Phase 5
- regenerated metrics artifacts successfully for both routes
- implemented Phase 6 scaffold:
  - `bins/s06_analysis/loaders.py`
  - `bins/s06_analysis/interpret.py`
  - `bins/s06_analysis/report_builder.py`
- generated first Phase 6 route summaries

### Validation completed
- structured / embedding parity confirmed:
  - `149 / 149`
- metrics artifacts load successfully
- `Route_B_Legacy` epoch aggregation corrected:
  - `1960-1964`
  - `1965-1969`
- `Route_B_Legacy` innovation velocity validated:
  - `1` transition
- `Route_A_Modern` remains singleton:
  - `2025-2029`
- Phase 6 terminal interpretation executed successfully
- Phase 6 markdown summaries written:
  - `analysis_outputs/summaries/Route_A_Modern_summary.md`
  - `analysis_outputs/summaries/Route_B_Legacy_summary.md`

### Operational result
- pipeline is now stable, reproducible, and analysis-ready
- `Route_B_Legacy` is no longer singleton
- Phase 6 interpretive work has begun
- next work should extend interpretation, table export, and visualization rather than reopen infrastructure debugging

Engineering details and file-level changes are documented in:

→ `DEBUGGING_AUDIT_2026-03-22.md`

---

## 2026-03-22 — Documentation synchronization

Documentation surfaces aligned to validated current state:
- `METHODS_PIPELINE.md`
- `DATA_SCHEMA.md`
- `AUDIT_CONTEXT.md`
- `RESEARCH_LOG.md`
- `DEBUGGING_AUDIT_2026-03-22.md`

Operational result:
- methods, schema, audit context, and chronology reflected the same validated post-stabilization state

---

## 2026-03-23 — Phase 6 extension: tables, figures, and APA reporting layer

### Objective
Continue Phase 6 from the validated post-stabilization state by extending the interpretive/reporting layer without reopening Phases 2–5 infrastructure work.

### Preconditions confirmed
- upstream Phases 2–5 remained stable and validated
- `Route_B_Legacy` remained corrected and validated
- validated route state at start of this cycle:
  - `Route_A_Modern` = one epoch, no transition
  - `Route_B_Legacy` = two epochs, one transition
- the loader contract remained intact and was preserved as the read-only boundary for Phase 6 extension work

### Completed work

#### 1. Machine-readable table export layer
Implemented and validated machine-readable CSV exports under `analysis_outputs/tables/`.

Artifacts produced:
- `Route_A_Modern_epoch_summary.csv`
- `Route_A_Modern_innovation_velocity.csv`
- `Route_B_Legacy_epoch_summary.csv`
- `Route_B_Legacy_innovation_velocity.csv`

Validation outcomes:
- Route A epoch table contained one data row for `2025-2029`
- Route A innovation-velocity table was header-only, consistent with singleton-route behavior
- Route B epoch table contained two data rows for `1960-1964` and `1965-1969`
- Route B innovation-velocity table contained one transition row
- Route B row counts remained consistent with validated parity (`149 / 149`)

Commit:
- `c27c086` — `Phase 6: add machine-readable table exports`

#### 2. Backend figure layer
Implemented and validated backend figure generation under `analysis_outputs/figures/`.

Artifacts produced:
- `Route_A_Modern_epoch_dispersion.png`
- `Route_B_Legacy_epoch_dispersion.png`
- `Route_B_Legacy_innovation_velocity.png`

Validation outcomes:
- Route A innovation-velocity figure was correctly skipped
- Route A epoch dispersion rendered as a singleton-route figure
- Route B epoch dispersion and innovation-velocity figures rendered as expected

Commit:
- `3b33525` — `Phase 6: add first visualization layer`

#### 3. APA manuscript table layer
Implemented and validated manuscript-facing APA tables under `manuscript/paper/tables/`.

Artifacts produced:
- `Table_1_epoch_summary.md`
- `Table_2_innovation_velocity.md`

Validation outcomes:
- Table 1 reported epoch-level descriptive summaries across both routes
- Table 2 reported the single validated legacy transition
- values were rounded for reporting and notes explicitly documented singleton-route behavior

Commit:
- `04c8acd` — `Phase 6: add APA manuscript tables`

#### 4. APA manuscript figure layer
Implemented and validated manuscript-facing APA figures under `manuscript/paper/figures/`.

Artifacts produced:
- `Figure_1_epoch_dispersion.png`
- `Figure_1_epoch_dispersion.md`
- `Figure_2_innovation_velocity.png`
- `Figure_2_innovation_velocity.md`

Validation outcomes:
- Figure 1 documented epoch-level semantic dispersion across validated route/epoch units
- Figure 2 documented the validated legacy transition only
- figure notes explicitly documented why Route A does not contribute a transition estimate

Commit:
- `51ceb70` — `Phase 6: add APA manuscript figures`

### Methodological constraints preserved
- no reopening of upstream infrastructure debugging
- no modification of validated Phase 2–5 logic
- no loader-contract breakage
- additive extension only
- auditability and reproducibility preserved

### Reporting rule added
APA 7 compliance is now treated as an embedded rule for all data analysis reporting artifacts without exception.

### Result
Phase 6 now includes:
- descriptive route summaries
- machine-readable tables
- backend figures
- APA manuscript tables
- APA manuscript figures

This establishes the current validated reporting baseline for subsequent interpretive and manuscript-oriented work.

---

## 2026-03-23 — Route_A_Modern expansion, repair, and revalidation completed

### Objective

Expand `Route_A_Modern` beyond the singleton 2025–2029 state by admitting the validated modern batch, rerunning downstream stages, repairing the resulting year-resolution and manifest-identity defects, and regenerating Phase 6 outputs.

### Work completed

- promoted the validated modern scraper-beta batch into live `data/raw/Route_A_Modern/`
- bridged the promoted modern rows into `data/manifests/pipeline_manifest.csv`
- reran process and analyze phases on the expanded Route A corpus
- identified and fixed a year-resolution defect for DOI-style modern filenames stored under year-bucket directories
- identified and fixed a manifest-identity mismatch between bridge-created rows and analyze-seeded rows
- restored a clean manifest state and re-bridged Route A using canonical pipeline `doc_id` values
- reran analyze successfully on the repaired manifest
- reran Phase 5 metrics successfully
- regenerated backend Phase 6 outputs
- regenerated APA manuscript tables and figures

### Validation completed

#### Route_A_Modern

- `epoch_count = 6`
- `epoch_labels = ['2000-2004', '2005-2009', '2010-2014', '2015-2019', '2020-2024', '2025-2029']`
- `innovation_velocity_count = 5`
- `source_embedding_file_count = 10`

#### Route_B_Legacy

- `epoch_count = 2`
- `epoch_labels = ['1960-1964', '1965-1969']`
- `innovation_velocity_count = 1`

### Operational result

- `Route_A_Modern` is no longer a singleton placeholder route
- the project now supports bounded descriptive temporal interpretation for both routes
- Phase 6 backend and APA reporting outputs have been successfully widened to reflect the expanded Route A state

### Remaining cleanup

- synchronize APA table note text with the new Route A state
- synchronize current-state documentation surfaces with the new validated Route A state
- treat manifest extract/embedding status writeback as a later hygiene pass rather than a current functional blocker
