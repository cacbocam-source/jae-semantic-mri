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
- Old paths that have active consumers remain symlinks until a later cleanup phase.
- Do not delete compatibility shims during Phase 1 stabilization.

## Generated docs
- `docs/INGESTION_LOG.md`
- `docs/CORPUS_COVERAGE.md`
- `docs/PIPELINE_AUDIT.md`

These remain at their current paths until builders and dependent scripts are patched.

## Editing rules
- `AUDIT_CONTEXT.md`: edit manually when current-state authority changes.
- `RESEARCH_LOG.md`: append only; do not rewrite historical entries except to correct obvious clerical defects.
- `docs/00_state/ACQUISITION_LOG.md`: edit manually as the operational runbook for acquisition-state procedure.
- `docs/00_state/PROJECT_STATE.md`: derived summary only; must defer to `AUDIT_CONTEXT.md`.
- generated docs must not be manually edited unless the builder path is intentionally bypassed and that choice is explicitly documented.

## Deletion policy
Archive first. Delete only after:
1. verification passes,
2. one normal documentation/output cycle completes,
3. no references remain to the old paths.
