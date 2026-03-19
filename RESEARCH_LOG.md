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

## 2026-03-18 — Phase 5 contract-lock pass completed (historical)

Objective:
- freeze Phase 5 architectural boundaries before real-artifact execution

Completed:
- scaffolded and aligned `bins/s03_analysis/metrics.py`
- added `MetricsArtifact`
- aligned metrics-stage manifest helpers
- synchronized closeout documentation

Historical note:
- this pass was an intermediate same-day milestone
- it was superseded later the same day by completed real-artifact execution

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

## 2026-03-19 — Cleanup and stabilization pass completed

Work completed:
- reduced stale script surface by retiring or archiving:
  - `scripts/doc_check.sh`
  - `scripts/audit_entry.sh`
  - `scripts/compliance_check.sh`
- removed `scripts/phase5_contract_check.sh`
- rewrote active environment validation scripts to validate the NVMe root directly:
  - `scripts/startup_check.sh`
  - `scripts/doctor.sh`
- retired legacy `bins/s01_ingest/orchestrator.py` from the active workflow
- reduced `bins/s01_ingest/ledger.py` to helper-only compatibility behavior
- restored `MASTER_LEDGER` in `config.py` as compatibility residue only
- repaired `tests/test_benchmarks.py` after pruning-related breakage
- removed the dead ingest phase from `main.py`
- added root-level `pyproject.toml`

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
- compatibility residue is explicitly bounded rather than implicitly active

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
- established explicit legacy mapping support through:
  - `data/manifests/legacy_filename_year_map.csv`

Validation completed:
- `python3 -m py_compile bins/s03_analysis/section_export.py` passed
- `python3 tests/test_section_exports.py` passed
- `python3 tests/test_benchmarks.py` passed

Operational result:
- year resolution is now explicit, deterministic, and portable across future corpus expansion
- unsupported filenames can no longer silently guess a year inside active export code

---

## Session-close resume point

Next work should begin from one of:
- downstream analysis consumption and interpretation of Phase 5 route-level metrics artifacts
- Phase 6 statistical inference
- manuscript/reporting integration tasks explicitly requested by the user
