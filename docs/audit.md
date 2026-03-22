# Computational Infrastructure Audit

Project: A Semantic MRI of Agricultural Education  
Initial Build Date: 2026-03-10  
Status: Supplemental workflow and infrastructure history only

Authority note:
- `AUDIT_CONTEXT.md` is the canonical current-state handoff.
- `RESEARCH_LOG.md` is the canonical chronological session log.
- This file preserves historical build and workflow milestones only.

---

## 2026-03-10 — Infrastructure foundation

Implemented:
- NVMe-backed project workspace
- repository skeleton
- service-bin package structure
- `config.py`
- `main.py`
- startup validation and health-check scripts

---

## 2026-03-15 — Structured export layer completed

Historical significance:
- persistent structured artifacts became available for Phase 4 embedding work
- canonical top-level export replaced ad hoc section payload assumptions

---

## 2026-03-18 — Shared schema and validation hardening

Historical significance:
- corrected schema/export drift that had previously blocked successful real embedding execution
- established stronger shared validation and typed artifact boundaries

---

## 2026-03-18 — Phase 5 real-artifact execution completed

Historical significance:
- Phase 5 moved from scaffold/alignment to completed production artifact generation
- route-level metrics artifacts became real persisted outputs

---

## 2026-03-19 — Baseline contract repair and post-Phase-5 validation hardening

Historical significance:
- live contract drift in the utility layer was repaired
- post-Phase-5 validation became an active checked boundary rather than only a documented expectation
- singleton-epoch route artifacts were verified as valid current-state outputs

---

## 2026-03-19 — Cleanup and stabilization pass completed

Historical significance:
- stale script surface reduced
- active environment validation scripts rewritten to the NVMe-root model
- legacy ingest rebuild orchestration retired
- repo returned to a stable validated state after cleanup

---

## 2026-03-19 — Deterministic year-resolution contract implemented

Historical significance:
- benchmark-only hardcoded filename special cases removed from active export code
- deterministic precedence established:
  1. manifest year
  2. explicit legacy filename map
  3. supported filename parsing
  4. fail fast

---

## 2026-03-20 — Beta pilot epoch protocol formalized

Historical significance:
- the next study was explicitly defined as a live-manuscript beta systems test rather than an inferential historical study
- pilot corpus organization was documented under:
  - `data/raw_pdfs/<route>/<year>/<filename>.pdf`
- pilot intake, quarantine, post-Phase-5 validation, and closeout boundaries were documented
- Phase 6 gating was tied explicitly to whether larger live-manuscript intake yields multi-epoch route coverage

This milestone documents the authorized next-study protocol. It does not imply that the beta pilot has already been executed.
