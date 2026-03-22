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
- `scripts/startup_check.sh` → SYSTEM STATUS: READY
- `scripts/doctor.sh` → SYSTEM STATUS: READY

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
- both route-level metrics artifacts remain structurally valid
- current state supports descriptive reporting and readiness work, not substantive temporal inference

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

## Session-close resume point

Next work should begin from:
- beta pilot epoch study execution using live manuscripts
- corpus staging under canonical `route/year` organization
- intake audit of newly captured manuscripts
- rerun of Phases 2–5 on the expanded corpus
- revalidation of route-level metrics artifacts after corpus expansion
- decision on whether expanded epoch coverage justifies broader Phase 6 analysis

# RESEARCH LOG

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
- the remaining bottleneck is narrow legacy metadata/prefill completion rather than general downloader failure

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
- legacy acquisition now has a deterministic workflow boundary
- manual effort is concentrated on ambiguous rows instead of the whole corpus
- the project is now explicitly a hybrid system: automated engine plus controlled legacy intake

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

## Session-close resume point

Next work should begin from:
- generating a bounded legacy prefill queue by year range
- manually confirming unresolved JAATEA-era rows in that queue
- downloading confirmed rows into staging
- promoting approved staged PDFs into canonical raw manuscript storage
- bridging promoted files into the pipeline manifest
- rerunning Phases 2–5 on the newly expanded legacy corpus

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
- `scripts/startup_check.sh` → SYSTEM STATUS: READY
- `scripts/doctor.sh` → SYSTEM STATUS: READY

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
- both route-level metrics artifacts remain structurally valid
- current state supports descriptive reporting and readiness work, not substantive temporal inference

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

## 2026-03-21 — 1960–1969 legacy acquisition batch completed and bridged into the live corpus

Work completed:
- repaired and stabilized the root-level `legacy_acquisition/` layer
- rebuilt the acquisition contract, OpenAlex prefill builder, downloader, promoter, and manifest bridge where needed
- corrected downloader handling for OJS `/article/download/...` URLs so they are treated as direct download targets
- generated the 1960–1969 legacy metadata-prefill queue
- downloaded 149 legacy PDFs into staging successfully
- bulk-approved the verified downloaded rows for promotion
- promoted 149 staged legacy PDFs into:
  - `data/raw/Route_B_Legacy/<year>/...`
- bridged the promoted rows into:
  - `data/manifests/pipeline_manifest.csv`

Verification completed:
- raw legacy corpus count after promotion: 150 files total in `data/raw/Route_B_Legacy/`
- manifest bridge result:
  - `added=149`
  - `updated=0`
  - `skipped=0`
- manifest row count after bridge: 151 rows total

Operational result:
- the legacy acquisition layer is now operational for the 1960–1969 decade batch
- acquisition is no longer the blocker for this batch
- the project can now move from legacy intake back into the stabilized downstream engine

Documentation/state correction:
- current live acquisition code location is `legacy_acquisition/` at repo root
- the executed batch was promoted into `data/raw/`, not `data/raw_pdfs/`
- earlier `data/raw_pdfs/` references should be treated as historical/protocol planning residue unless explicitly reactivated

Next step:
- run the stabilized downstream pipeline on the newly added 1960–1969 legacy manifest rows:
  1. extraction
  2. structured section export
  3. section embeddings
  4. Phase 5 route-level metrics regeneration
  5. post-Phase-5 validation


---

## Session-close resume point

Next work should begin from:
- beta pilot epoch study execution using live manuscripts
- corpus staging under canonical `route/year` organization
- intake audit of newly captured manuscripts
- rerun of Phases 2–5 on the expanded corpus
- revalidation of route-level metrics artifacts after corpus expansion
- decision on whether expanded epoch coverage justifies broader Phase 6 analysis

# RESEARCH LOG

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
- the remaining bottleneck is narrow legacy metadata/prefill completion rather than general downloader failure

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
- legacy acquisition now has a deterministic workflow boundary
- manual effort is concentrated on ambiguous rows instead of the whole corpus
- the project is now explicitly a hybrid system: automated engine plus controlled legacy intake

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

## 2026-03-21 — 1960–1969 legacy acquisition batch completed and bridged into the live corpus

Work completed:
- repaired and stabilized the root-level `legacy_acquisition/` layer
- rebuilt the acquisition contract, OpenAlex prefill builder, downloader, promoter, and manifest bridge where needed
- corrected downloader handling for OJS `/article/download/...` URLs so they are treated as direct download targets
- generated the 1960–1969 legacy metadata-prefill queue
- downloaded 149 legacy PDFs into staging successfully
- bulk-approved the verified downloaded rows for promotion
- promoted 149 staged legacy PDFs into:
  - `data/raw/Route_B_Legacy/<year>/...`
- bridged the promoted rows into:
  - `data/manifests/pipeline_manifest.csv`

Verification completed:
- raw legacy corpus count after promotion: 150 files total in `data/raw/Route_B_Legacy/`
- manifest bridge result:
  - `added=149`
  - `updated=0`
  - `skipped=0`
- manifest row count after bridge: 151 rows total

Operational result:
- the legacy acquisition layer is now operational for the 1960–1969 decade batch
- acquisition is no longer the blocker for this batch
- the project can now move from legacy intake back into the stabilized downstream engine

Documentation/state correction:
- current live acquisition code location is `legacy_acquisition/` at repo root
- the executed batch was promoted into `data/raw/`, not `data/raw_pdfs/`
- earlier `data/raw_pdfs/` references should be treated as historical/protocol planning residue unless explicitly reactivated

Next step:
- run the stabilized downstream pipeline on the newly added 1960–1969 legacy manifest rows:
  1. extraction
  2. structured section export
  3. section embeddings
  4. Phase 5 route-level metrics regeneration
  5. post-Phase-5 validation


---

## Session-close resume point

Next work should begin from:
- generating a bounded legacy prefill queue by year range
- manually confirming unresolved JAATEA-era rows in that queue
- downloading confirmed rows into staging
- promoting approved staged PDFs into canonical raw manuscript storage
- bridging promoted files into the pipeline manifest
- rerunning Phases 2–5 on the newly expanded legacy corpus

---

# INGESTION AND YEAR RESOLUTION (POST-DEBUG STABILIZATION)

The system currently operates under a hybrid ingestion model with two canonical routes:

## Route_A_Modern
- file pattern: `data/raw/Route_A_Modern/<YEAR>.pdf`
- year resolution: filename-derived
- example: `2026.pdf → 2026`

## Route_B_Legacy
- file pattern: `data/raw/Route_B_Legacy/<YEAR>/<file>.pdf`
- year resolution: directory-derived
- example: `1960/<file>.pdf → 1960`

## Non-Temporal Artifacts

Some legacy artifacts do not resolve to a valid year (e.g., `Vol1_1.pdf`).

Operational rule:
- such files are **excluded from manifest seeding and downstream processing**
- they are not assigned a sentinel year in persisted artifacts
- exclusion is explicit and logged during pipeline execution

## Current Constraint

Manifest seeding (`seed_manifest_from_raw_pdfs`) still requires a callable year resolver.

A temporary bridge function (`_safe_infer_year`) is used to:
- support both ingestion schemas
- enforce exclusion of non-temporal artifacts

This is a **transitional architecture** and will be removed when manifest-only year resolution is implemented upstream.

---