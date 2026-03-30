#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(pwd)}"
cd "$ROOT"

STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="docs/90_archive/finalize_backups/${STAMP}"

mkdir -p "$BACKUP_DIR"
mkdir -p docs/00_state docs/10_methods docs/20_legacy_route docs/30_generated \
         docs/40_exceptions docs/50_supporting_logs docs/80_drafts docs/90_archive \
         docs/governance scripts

backup_if_exists() {
  for p in "$@"; do
    if [ -e "$p" ] || [ -L "$p" ]; then
      mkdir -p "$BACKUP_DIR/$(dirname "$p")"
      cp -a "$p" "$BACKUP_DIR/$p"
    fi
  done
}

backup_if_exists \
  PROJECT_STATE.md \
  docs/00_state/PROJECT_STATE.md \
  docs/00_state/ACQUISITION_LOG.md \
  docs/00_state/DEBUGGING_AUDIT_2026-03-22.md \
  docs/00_state/audit.md \
  docs/00_state/README.md \
  docs/governance/DOCUMENTATION_POLICY.md \
  docs/10_methods/DATA_SCHEMA.md \
  docs/10_methods/SCHEMA_CONTRACT.json

# Move PROJECT_STATE into Tier 00 if it still lives as a regular root file.
if [ -f PROJECT_STATE.md ] && [ ! -L PROJECT_STATE.md ]; then
  mv PROJECT_STATE.md docs/00_state/PROJECT_STATE.md
fi

# Root compatibility symlink for PROJECT_STATE.
if [ -e docs/00_state/PROJECT_STATE.md ] || [ -L docs/00_state/PROJECT_STATE.md ]; then
  rm -f PROJECT_STATE.md
  ln -s docs/00_state/PROJECT_STATE.md PROJECT_STATE.md
fi

# Ensure root compatibility shims exist for these Tier 00 files.
if [ -e docs/00_state/ACQUISITION_LOG.md ] || [ -L docs/00_state/ACQUISITION_LOG.md ]; then
  rm -f ACQUISITION_LOG.md
  ln -s docs/00_state/ACQUISITION_LOG.md ACQUISITION_LOG.md
fi

if [ -e docs/00_state/DEBUGGING_AUDIT_2026-03-22.md ] || [ -L docs/00_state/DEBUGGING_AUDIT_2026-03-22.md ]; then
  rm -f DEBUGGING_AUDIT_2026-03-22.md
  ln -s docs/00_state/DEBUGGING_AUDIT_2026-03-22.md DEBUGGING_AUDIT_2026-03-22.md
fi

# Mirror canonical root files into tier folders without changing authority.
ln -sfn ../../AUDIT_CONTEXT.md docs/00_state/AUDIT_CONTEXT.md
ln -sfn ../../RESEARCH_LOG.md docs/00_state/RESEARCH_LOG.md
ln -sfn ../../DATA_SCHEMA.md docs/10_methods/DATA_SCHEMA.md
ln -sfn ../../SCHEMA_CONTRACT.json docs/10_methods/SCHEMA_CONTRACT.json

cat > docs/00_state/README.md <<'EOF'
# Tier 00 State Documents

This folder contains current-state and audit-state materials that govern or contextualize the live repository state.

## Authority order
1. `AUDIT_CONTEXT.md` (canonical current-state authority; mirrored here by symlink)
2. `RESEARCH_LOG.md` (canonical chronology; mirrored here by symlink)
3. `DEBUGGING_AUDIT_2026-03-22.md` (bounded engineering audit for the stabilization cycle)
4. `ACQUISITION_LOG.md` (operational acquisition runbook)
5. `PROJECT_STATE.md` (derived executive snapshot; non-canonical)
6. `audit.md` (supplemental historical infrastructure audit)

## Notes
- Root-level canonical files remain authoritative even when mirrored here.
- Compatibility symlinks are preserved to avoid breaking older references.
- Generated closeout documents remain at their current root `docs/` paths until builder patching occurs.
EOF

cat > docs/governance/DOCUMENTATION_POLICY.md <<'EOF'
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
EOF

python3 - <<'PY'
from pathlib import Path

def prepend_if_missing(path_str: str, marker: str, block: str) -> None:
    p = Path(path_str)
    if not p.exists() or p.is_symlink():
        return
    text = p.read_text(encoding="utf-8")
    if marker in text:
        return
    p.write_text(block.rstrip() + "\n\n" + text, encoding="utf-8")

prepend_if_missing(
    "docs/00_state/PROJECT_STATE.md",
    "Role: Derived executive snapshot",
    """> Role: Derived executive snapshot
> Authority: Non-canonical. For controlling current-state interpretation, defer to `AUDIT_CONTEXT.md`.
> Update rule: Revise only after current-state, chronology, and generated audit surfaces are reconciled."""
)

prepend_if_missing(
    "docs/00_state/ACQUISITION_LOG.md",
    "Role: Operational acquisition runbook",
    """> Role: Operational acquisition runbook
> Authority: Subordinate to `AUDIT_CONTEXT.md`.
> Update rule: Use for acquisition procedure and intake logging; when it conflicts with `AUDIT_CONTEXT.md`, the audit context controls."""
)

prepend_if_missing(
    "docs/00_state/DEBUGGING_AUDIT_2026-03-22.md",
    "Role: Bounded engineering audit",
    """> Role: Bounded engineering audit
> Authority: Authoritative for the documented stabilization cycle only.
> Update rule: Historical engineering record; do not use as a global current-state replacement."""
)

prepend_if_missing(
    "docs/00_state/audit.md",
    "Role: Supplemental historical infrastructure audit",
    """> Role: Supplemental historical infrastructure audit
> Authority: Supplemental only. For controlling current-state interpretation, defer to `AUDIT_CONTEXT.md`.
> Update rule: Historical context and infrastructure narrative; not the canonical state source."""
)
PY

echo "Finalization complete."
echo "Backup captured at: $BACKUP_DIR"
