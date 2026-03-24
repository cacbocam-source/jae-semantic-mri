# Computational Infrastructure Audit

Project: *A Semantic MRI of Agricultural Education*  
Initial Build Date: 2026-03-10  
Last Updated: 2026-03-23  
Status: Supplemental workflow and infrastructure history only

## Authority note

- `AUDIT_CONTEXT.md` is the canonical current-state handoff.
- `RESEARCH_LOG.md` is the canonical chronological session log.
- `DEBUGGING_AUDIT_2026-03-22.md` is the authoritative engineering record for the stabilization cycle completed on 2026-03-22.
- `METHODS_PIPELINE.md` is the current methods summary.
- `DATA_SCHEMA.md` and `SCHEMA_CONTRACT.json` are the current schema/contract summaries.
- This file preserves historical build, repair, and workflow milestones only.
- If any conflict exists between this file and `AUDIT_CONTEXT.md`, `AUDIT_CONTEXT.md` controls.

---

## 2026-03-10 — Infrastructure foundation

Implemented:
- NVMe-backed project workspace
- repository skeleton
- service-bin package structure
- `config.py`
- `main.py`
- startup validation and health-check scripts

Historical significance:
- established the working repository, runtime entry surface, and storage-root discipline used by all later stages

---

## 2026-03-15 — Structured export layer completed

Historical significance:
- persistent structured artifacts became available for Phase 4 embedding work
- canonical top-level export replaced ad hoc section payload assumptions
- the project moved from extraction-only operation to reusable document-structure persistence

---

## 2026-03-18 — Shared schema and validation hardening

Historical significance:
- corrected schema/export drift that had previously blocked successful real embedding execution
- established stronger shared validation and typed artifact boundaries
- reduced ambiguity between extraction, structured export, embedding, and metrics contracts

---

## 2026-03-18 — Phase 5 real-artifact execution completed

Historical significance:
- Phase 5 moved from scaffold/alignment to completed production artifact generation
- route-level metrics artifacts became real persisted outputs
- the project crossed from preparatory engineering into executable route-level aggregation

---

## 2026-03-19 — Baseline contract repair and post-Phase-5 validation hardening

Historical significance:
- live contract drift in the utility layer was repaired
- post-Phase-5 validation became an active checked boundary rather than only a documented expectation
- singleton-epoch route artifacts were verified as valid current-state outputs

Operational consequence:
- the project could now distinguish true singleton-route states from pipeline defects

---

## 2026-03-19 — Cleanup and stabilization pass completed

Historical significance:
- stale script surface reduced
- active environment validation scripts rewritten to the NVMe-root model
- legacy ingest rebuild orchestration retired
- repo returned to a stable validated state after cleanup

Operational consequence:
- the repository was simplified into a more controlled execution surface before larger corpus expansion resumed

---

## 2026-03-19 — Deterministic year-resolution contract implemented

Historical significance:
- benchmark-only hardcoded filename special cases removed from active export code
- deterministic precedence established:
  1. manifest year
  2. explicit legacy filename map
  3. supported filename parsing
  4. fail fast

Operational consequence:
- unresolved year state became explicit rather than silently inferred

---

## 2026-03-20 — Beta pilot epoch protocol formalized

Historical significance:
- the next study was explicitly defined as a live-manuscript beta systems test rather than an inferential historical study
- pilot corpus organization was documented under:
  - `data/raw_pdfs/<route>/<year>/<filename>.pdf`
- pilot intake, quarantine, post-Phase-5 validation, and closeout boundaries were documented
- Phase 6 gating was tied explicitly to whether larger live-manuscript intake yields multi-epoch route coverage

This milestone documents the authorized next-study protocol. It does not imply that the beta pilot had already been executed.

---

## 2026-03-22 — Stabilization cycle and interpretive scaffold transition

Historical significance:
- final engineering defects across Bin 03, embedding schema, metrics aggregation, and manifest eligibility were resolved
- `Route_B_Legacy` advanced from singleton artifact state to validated two-epoch aggregation
- the Phase 6 interpretive scaffold was established and first route summaries were generated
- the project transitioned from pipeline stabilization into a controlled interpretive analysis phase

For full engineering detail, see:

→ `DEBUGGING_AUDIT_2026-03-22.md`

---

## 2026-03-23 — Phase 6 reporting stack completed

Historical significance:
- machine-readable table exports were added under `analysis_outputs/tables/`
- backend figure exports were added under `analysis_outputs/figures/`
- APA manuscript tables were added under `manuscript/paper/tables/`
- APA manuscript figures were added under `manuscript/paper/figures/`
- the project moved from an initial interpretive scaffold to a validated descriptive reporting stack

Interpretive significance:
- the reporting surface now supports route-level descriptive summaries, epoch summaries, innovation-velocity summaries, and manuscript-facing APA outputs
- this did not reopen stabilized engineering work in Phases 2–5
- Phase 6 remained downstream of validated metrics artifacts throughout the extension cycle

Reporting rule added:
- all Phase 6 reporting artifacts are now governed by APA 7 compliance without exception

---

## 2026-03-23 — Route_A_Modern expansion and downstream revalidation

Historical significance:
- the admitted modern corpus expanded beyond the earlier singleton `2026` state
- a validated Route A batch was promoted into live raw storage and bridged into the manifest
- process and analyze phases were rerun against the expanded Route A corpus
- the project crossed the first major threshold from singleton-modern placeholder state to multi-epoch modern route state

Operational consequence:
- `Route_A_Modern` ceased to be a singleton route artifact
- Route A became eligible for bounded route-internal temporal description

---

## 2026-03-23 — Year-resolution repair for DOI-style modern filenames

Historical significance:
- a failure was identified for modern DOI-style filenames that did not themselves contain a 4-digit year
- the failing case was the admitted 2024 modern file:
  - `10.5032_jae.v65i4.2828.pdf`
- the year-resolution contract was widened to support parent-directory-derived year parsing for year-bucket modern paths
- isolated structured export for the 2024 file succeeded after repair

Operational consequence:
- year resolution now supports:
  1. manifest year
  2. explicit legacy map
  3. filename parsing
  4. parent-directory parsing
  5. fail-fast unresolved state

This repair generalized the live contract rather than adding a one-off filename exception.

---

## 2026-03-23 — Manifest identity mismatch repaired

Historical significance:
- a manifest duplication defect was identified after Route A expansion
- bridge-created rows and analyze-seeded rows used different `doc_id` namespaces for the same Route A files
- this caused duplicate Route A manifest rows after analyze
- the bridge was repaired to use the canonical pipeline `doc_id` contract derived from the source PDF path

Operational consequence:
- Route A manifest rows were restored to a clean deduplicated state
- manifest identity once again aligned with the active pipeline execution contract

This was a contract-level repair rather than a cosmetic cleanup.

---

## 2026-03-23 — Route_A_Modern metrics and reporting outputs regenerated

Historical significance:
- Phase 5 metrics were rerun successfully after Route A expansion and repair
- Phase 6 backend and APA outputs were regenerated successfully
- the modern route widened from singleton state to a real multi-epoch structure

Validated Route_A_Modern outcome:
- `epoch_count = 6`
- `epoch_labels = ['2000-2004', '2005-2009', '2010-2014', '2015-2019', '2020-2024', '2025-2029']`
- `innovation_velocity_count = 5`
- `source_embedding_file_count = 10`

Validated Route_B_Legacy retained:
- `epoch_count = 2`
- `epoch_labels = ['1960-1964', '1965-1969']`
- `innovation_velocity_count = 1`

Interpretive significance:
- both routes now support bounded within-route temporal description
- Route A now contributes innovation-velocity reporting rather than remaining excluded as a singleton artifact
- broader inferential interpretation remains constrained by uneven corpus coverage across the full 1960–2026 window

---

## 2026-03-23 — Documentation synchronization required after Route_A expansion

Historical significance:
- authoritative and supplementary documentation required synchronization after the Route A state widened
- singleton-Route-A language in current-state and APA reporting surfaces became stale after successful regeneration
- current-state documentation, methods documentation, research chronology, and historical audit surfaces required revision to reflect the widened modern route

Operational consequence:
- documentation synchronization became the next correct closeout step after the successful technical rerun cycle

This milestone records the need for synchronization; current truth remains controlled by `AUDIT_CONTEXT.md` and `RESEARCH_LOG.md`.