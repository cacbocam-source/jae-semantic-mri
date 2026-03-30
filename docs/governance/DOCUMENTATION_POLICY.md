# Documentation Policy

## Canonical root files
- `AUDIT_CONTEXT.md` = canonical current-state authority
- `RESEARCH_LOG.md` = canonical chronology
- `DATA_SCHEMA.md` = schema specification
- `SCHEMA_CONTRACT.json` = machine-readable schema contract

## Tier 00 subordinate files
- `docs/00_state/ACQUISITION_LOG.md` = operational acquisition runbook
- `docs/00_state/DEBUGGING_AUDIT_2026-03-22.md` = bounded engineering audit
- `docs/00_state/PROJECT_STATE.md` = derived executive snapshot; non-canonical
- `docs/00_state/audit.md` = supplemental historical infrastructure audit

## Compatibility policy
- Old paths that have existing consumers should remain symlinks until a later cleanup phase.
- Do not delete compatibility shims during Phase 1 stabilization.

## Generated docs
- `docs/INGESTION_LOG.md`
- `docs/CORPUS_COVERAGE.md`
- `docs/PIPELINE_AUDIT.md`

These remain at their current paths until builders and any dependent scripts are patched.

## Deletion policy
Archive first. Delete only after:
1. verification passes,
2. one normal documentation/output cycle completes,
3. no references remain to the old paths.
