# REPO_KEEP_ARCHIVE_MAP

Project root:

```text
/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit
```

Status: active control map for stabilized analysis continuity and beta-pilot transition

---

## 1. Keep active

### Root / core
- `config.py`
- `main.py`
- `.gitignore`
- `pyproject.toml`
- `requirements-lock.txt`
- `REPO_KEEP_ARCHIVE_MAP.md`

### Active runtime bins
- `bins/s02_processor/**`
- `bins/s03_analysis/**`
- `bins/s04_utils/**`

### Keep active, but reduced / compatibility-only
- `bins/s01_ingest/__init__.py`
- `bins/s01_ingest/ledger.py`

### Active scripts
- `scripts/doctor.sh`
- `scripts/startup_check.sh`
- `scripts/research_snapshot.sh`

### Active tests
- `tests/test_benchmarks.py`
- `tests/test_metrics_contracts.py`
- `tests/test_metrics_math.py`
- `tests/test_section_exports.py`
- `tests/test_year_resolution.py`
- `tests/test_post_phase5_validation.py`

### Active docs / records
- `AUDIT_CONTEXT.md`
- `RESEARCH_LOG.md`
- `DATA_SCHEMA.md`
- `METHODS_PIPELINE.md`
- `SCHEMA_CONTRACT.json`
- `ARCHITECTURE.md`
- `RESEARCH_COMPLIANCE.md`
- `audit.md`
- `docs/BETA_PILOT_EPOCH_PROTOCOL.md`

### Active control data
- `data/manifests/pipeline_manifest.csv`
- `data/manifests/legacy_filename_year_map.csv`
- `data/manifests/beta_sample_manifest_template.csv`

### Active pilot raw-manuscript area
- `data/raw_pdfs/`

Important rule:
- keep `data/raw_pdfs/` distinct from the existing validated benchmark corpus under `data/raw/`
- do not silently merge pilot intake with the benchmark corpus

---

## 2. Keep archived

### Archived scripts
- `scripts/_archive/audit_entry.sh`
- `scripts/_archive/compliance_check.sh`
- `scripts/_archive/doc_check.sh`

### Archived ingest wrapper
- `bins/_archive/orchestrator.py`

### Historical backups / snapshots
- `docs/_audit_backups/...`

---

## 3. Remove / ignore / do not track

```gitignore
__pycache__/
*.pyc
*.pyo
.DS_Store
data/raw/**
data/processed/**
data/metrics/
docs/_audit_backups/
!data/manifests/
!data/manifests/**
!data/structured/
!data/structured/**
data/embeddings/
data/testing/
```

---

## 4. Freeze list — do not prune further right now

- `bins/s04_utils/artifacts.py`
- `bins/s04_utils/manifest_manager.py`
- `bins/s04_utils/schemas.py`
- `bins/s04_utils/validators.py`
- `bins/s04_utils/year_resolution.py`
- `bins/s03_analysis/embedder.py`
- `bins/s03_analysis/metrics.py`
- `bins/s03_analysis/section_export.py`
- `tests/test_year_resolution.py`
- `tests/test_post_phase5_validation.py`
- `data/manifests/beta_sample_manifest_template.csv`
- `docs/BETA_PILOT_EPOCH_PROTOCOL.md`

### Additional runtime rule (post-debug stabilization)

- non-temporal files in `data/raw/` (e.g., `Vol1_1.pdf`) must not be processed
- they may remain in raw storage but are excluded by pipeline logic
- do not relocate or delete unless explicitly archived