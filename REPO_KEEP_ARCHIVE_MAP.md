# REPO_KEEP_ARCHIVE_MAP

Project root:

```text
/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
```

Status: active control map for cleanup closeout  
Purpose: define what stays active, what stays archived, and what should be ignored or removed without destabilizing the current build

---

## 1. Keep active

These are part of the current working system and should remain in the active repo surface.

### Root / core
- `config.py`
- `main.py`
- `.gitignore`

### Active runtime bins
- `bins/s02_processor/__init__.py`
- `bins/s02_processor/cleaning.py`
- `bins/s02_processor/diagnostics.py`
- `bins/s02_processor/digital_extract.py`
- `bins/s02_processor/ocr_engine.py`
- `bins/s02_processor/orchestrator.py`
- `bins/s02_processor/segmenter.py`
- `bins/s02_processor/smart_extract.py`

- `bins/s03_analysis/__init__.py`
- `bins/s03_analysis/embedder.py`
- `bins/s03_analysis/metrics.py`
- `bins/s03_analysis/orchestrator.py`
- `bins/s03_analysis/section_export.py`

- `bins/s04_utils/__init__.py`
- `bins/s04_utils/artifacts.py`
- `bins/s04_utils/manifest_manager.py`
- `bins/s04_utils/schemas.py`
- `bins/s04_utils/validators.py`

### Keep active, but reduced / compatibility-only
- `bins/s01_ingest/__init__.py`
- `bins/s01_ingest/ledger.py`

Current role of `bins/s01_ingest/ledger.py`:
- compatibility/support only
- keep the trimmed helper-only version
- do not restore ledger rebuild logic

### Active scripts
- `scripts/doctor.sh`
- `scripts/startup_check.sh`
- `scripts/research_snapshot.sh`

Status of `scripts/research_snapshot.sh`:
- keep active
- acceptable as-is for now
- may be tightened later to reduce hardcoded assumptions and broad staging behavior

### Active tests
- `tests/test_benchmarks.py`
- `tests/test_metrics_contracts.py`
- `tests/test_metrics_math.py`
- `tests/test_section_exports.py`

### Active docs / records
- `AUDIT_CONTEXT.md`
- `RESEARCH_LOG.md`
- `DATA_SCHEMA.md`
- `METHODS_PIPELINE.md`
- `SCHEMA_CONTRACT.json`
- `ARCHITECTURE.md`
- `RESEARCH_COMPLIANCE.md`
- `audit.md`

### Active data / control surfaces
- `data/manifests/pipeline_manifest.csv`
- production directories under:
  - `data/raw/`
  - `data/processed/`
  - `data/structured/`
  - `data/embeddings/`
  - `data/metrics/`
  - `data/testing/`

---

## 2. Keep archived

These should remain preserved for historical trace, but should not remain in the active operational surface.

### Archived scripts
- `scripts/doc_check.sh`
- `scripts/audit_entry.sh`
- `scripts/compliance_check.sh`

Recommended archive convention:
- `scripts/_archive/doc_check.sh`
- `scripts/_archive/audit_entry.sh`
- `scripts/_archive/compliance_check.sh`

### Archived ingest wrapper
- `bins/s01_ingest/orchestrator.py`

Reason:
- it was only wrapping the legacy ledger rebuild path
- it is not part of the current manifest-driven Phase 3–5 workflow

### Historical backups / snapshots
Keep, but clearly non-active:
- `docs/_audit_backups/...`
- timestamped closeout or snapshot folders

Rule:
- preserve for provenance
- do not let active scripts scan them as canonical docs

---

## 3. Remove / ignore / do not track

These are clutter or disposable artifacts, not meaningful source.

### Remove from working tree when present
- all `__pycache__/` directories
- all `*.pyc`
- all `*.pyo`

### Ignore in Git
Keep these in `.gitignore`:

```gitignore
__pycache__/
*.pyc
*.pyo
.DS_Store

data/raw/**
data/processed/**

!data/manifests/
!data/manifests/**
!data/structured/
!data/structured/**

data/embeddings/
data/testing/
```

### Already removed and should stay removed
- `scripts/phase5_contract_check.sh`

Reason:
- scaffold-era governance
- not an active runtime requirement

---

## 4. Freeze list — do not prune further right now

These should be treated as load-bearing for the current stable build.

### Contract / state / validation boundary
- `bins/s04_utils/artifacts.py`
- `bins/s04_utils/manifest_manager.py`
- `bins/s04_utils/schemas.py`
- `bins/s04_utils/validators.py`

### Core analysis stage files
- `bins/s03_analysis/embedder.py`
- `bins/s03_analysis/metrics.py`
- `bins/s03_analysis/section_export.py`
- `bins/s03_analysis/orchestrator.py`

### Current compatibility bridge
- `config.py`
- keep `MASTER_LEDGER` in place for now

### Test protection surface
- `tests/test_benchmarks.py`
- `tests/test_metrics_contracts.py`
- `tests/test_metrics_math.py`
- `tests/test_section_exports.py`

### Active environment checks
- `scripts/doctor.sh`
- `scripts/startup_check.sh`

---

## 5. Legacy-but-tolerated for now

These are not ideal, but they are not worth destabilizing the repo further today.

### `config.py`
Keep this for now:
- `MASTER_LEDGER = MANIFEST_DIR / "jae_master_ledger.csv"`

Reason:
- currently serving as a compatibility constant
- removing it prematurely caused breakage
- retire it only in a future traced cleanup pass after all imports are removed

### `bins/s01_ingest/ledger.py`
Keep only:
- `make_doc_id(...)`
- `infer_route(...)`

Do not reintroduce:
- ledger rebuild logic
- extraction re-run logic
- file-writing ledger contract logic

---

## 6. Repo roles summary

### Canonical current-state control
- `AUDIT_CONTEXT.md`

### Canonical chronological record
- `RESEARCH_LOG.md`

### Supplemental historical record
- `audit.md`

### Machine-readable contract
- `SCHEMA_CONTRACT.json`

### Current active runtime spine
- `s02_processor`
- `s03_analysis`
- `s04_utils`

### Compatibility residue
- `s01_ingest/ledger.py`
- `MASTER_LEDGER` in `config.py`

### Retired operational surfaces
- old compliance/doc/audit-entry scripts
- old Phase 5 contract-check script
- old ingest ledger orchestrator

---

## 7. Operational rule going forward

Use this as the repo policy.

### Active
Anything needed to:
- run
- validate
- test
- document current state accurately

### Archived
Anything that:
- explains history
- preserves provenance
- represents a retired workflow
- is useful only for forensic reference

### Removed
Anything that is:
- regenerated cache
- stale scaffolding with no surviving dependency
- non-source build residue

---

## 8. One-line decision rule for future cleanup

Before moving or deleting anything, ask:

**Does this file currently define a contract, a validation boundary, a persistence boundary, a state-tracking boundary, or a tested import surface?**

- If yes: keep or refactor only with traced replacements.
- If no: archive or remove.

---

## 9. Final practical map

### Keep active
- `config.py`
- `main.py`
- `bins/s02_processor/**`
- `bins/s03_analysis/**`
- `bins/s04_utils/**`
- `bins/s01_ingest/ledger.py`
- `scripts/doctor.sh`
- `scripts/startup_check.sh`
- `scripts/research_snapshot.sh`
- `tests/**`
- canonical docs
- `data/manifests/pipeline_manifest.csv`

### Keep archived
- `bins/s01_ingest/orchestrator.py`
- `scripts/doc_check.sh`
- `scripts/audit_entry.sh`
- `scripts/compliance_check.sh`
- docs backup folders
- historical closeout artifacts

### Remove / ignore
- `__pycache__/`
- `*.pyc`
- `*.pyo`
- `.DS_Store`
- already-removed `scripts/phase5_contract_check.sh`
