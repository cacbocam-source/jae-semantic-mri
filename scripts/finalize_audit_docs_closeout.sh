#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(pwd)}"
cd "$ROOT"

STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="docs/90_archive/finalize_audit_docs/${STAMP}"

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
  AUDIT_CONTEXT.md \
  RESEARCH_LOG.md \
  DATA_SCHEMA.md \
  SCHEMA_CONTRACT.json \
  PROJECT_STATE.md \
  ACQUISITION_LOG.md \
  DEBUGGING_AUDIT_2026-03-22.md \
  docs/00_state/PROJECT_STATE.md \
  docs/00_state/ACQUISITION_LOG.md \
  docs/00_state/DEBUGGING_AUDIT_2026-03-22.md \
  docs/00_state/audit.md \
  docs/00_state/README.md \
  docs/governance/DOCUMENTATION_POLICY.md

# Put PROJECT_STATE under Tier 00 if it still exists as a regular root file.
if [ -f PROJECT_STATE.md ] && [ ! -L PROJECT_STATE.md ]; then
  mv PROJECT_STATE.md docs/00_state/PROJECT_STATE.md
elif [ ! -e docs/00_state/PROJECT_STATE.md ] && [ ! -L docs/00_state/PROJECT_STATE.md ]; then
  touch docs/00_state/PROJECT_STATE.md
fi

# If ACQUISITION_LOG is still a regular root file, move it into Tier 00.
if [ -f ACQUISITION_LOG.md ] && [ ! -L ACQUISITION_LOG.md ]; then
  mv ACQUISITION_LOG.md docs/00_state/ACQUISITION_LOG.md
elif [ ! -e docs/00_state/ACQUISITION_LOG.md ] && [ ! -L docs/00_state/ACQUISITION_LOG.md ]; then
  touch docs/00_state/ACQUISITION_LOG.md
fi

# If DEBUGGING audit is still regular root, move it into Tier 00.
if [ -f DEBUGGING_AUDIT_2026-03-22.md ] && [ ! -L DEBUGGING_AUDIT_2026-03-22.md ]; then
  mv DEBUGGING_AUDIT_2026-03-22.md docs/00_state/DEBUGGING_AUDIT_2026-03-22.md
fi

# Compatibility symlinks at root.
rm -f PROJECT_STATE.md
ln -s docs/00_state/PROJECT_STATE.md PROJECT_STATE.md

rm -f ACQUISITION_LOG.md
ln -s docs/00_state/ACQUISITION_LOG.md ACQUISITION_LOG.md

if [ -e docs/00_state/DEBUGGING_AUDIT_2026-03-22.md ] || [ -L docs/00_state/DEBUGGING_AUDIT_2026-03-22.md ]; then
  rm -f DEBUGGING_AUDIT_2026-03-22.md
  ln -s docs/00_state/DEBUGGING_AUDIT_2026-03-22.md DEBUGGING_AUDIT_2026-03-22.md
fi

# Mirror canonical root surfaces into tier folders without changing authority.
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
EOF

cat > docs/00_state/ACQUISITION_LOG.md <<'EOF'
# Acquisition Log — Route_A_Modern

> Role: Operational acquisition runbook  
> Authority: Subordinate to `AUDIT_CONTEXT.md`.  
> If this file conflicts with `AUDIT_CONTEXT.md`, the audit context controls.

## Current validated status

### Fully completed modern epoch
- `2005–2009` is the first fully reconstructed and validated modern epoch.

### Currently admitted modern year coverage
Covered:
- `2000`
- `2001`
- `2003`
- `2005`
- `2006`
- `2007`
- `2008`
- `2009`
- `2012`
- `2013`
- `2018`
- `2022`
- `2024`
- `2026`

Missing:
- `2002`
- `2004`
- `2010`
- `2011`
- `2014`
- `2015`
- `2016`
- `2017`
- `2019`
- `2020`
- `2021`
- `2023`
- `2025`

## Validated raw-storage forms

The live Route_A_Modern intake contract accepts both of these forms:

1. Flat-file modern layout  
   `data/raw/Route_A_Modern/<YEAR>.pdf`

2. Year-bucket modern layout  
   `data/raw/Route_A_Modern/<YEAR>/<file>.pdf`

## Year-resolution contract

Resolution precedence:

1. manifest year when available
2. supported filename parsing
3. supported parent-directory parsing for year-bucket modern paths
4. fail-fast unresolved state

Operational rule:

A DOI-style filename without an embedded four-digit year is valid if the file is stored under a year-bucket directory whose parent name is itself a valid year.

Example:
`data/raw/Route_A_Modern/2024/10.5032_jae.v65i4.2828.pdf -> 2024`

## Intake rules

- Accept only `.pdf` files.
- Do not treat HTML or landing pages as corpus files.
- One file = one article.
- Do not silently guess a year.
- Keep each acquisition year in its own staging folder during manual intake.
- Mixed final raw-storage forms are allowed only within the validated contract above.

## Operational workflow

1. retrieve PDFs for the target year
2. stage them in a clean per-year working folder
3. perform QC on file type and article identity
4. place accepted files into the validated Route_A_Modern raw layout
5. run manifest integration according to the active repo workflow
6. run:
   - `python3 main.py --phase process`
   - `python3 main.py --phase analyze`
7. regenerate downstream state surfaces as required by the current pipeline
8. verify outputs before treating the intake as live

## Scope note

This file is an operational runbook for acquisition-state work only.  
It does not override:
- current-state authority in `AUDIT_CONTEXT.md`
- chronology in `RESEARCH_LOG.md`
- methods/schema contracts in `METHODS_PIPELINE.md`, `DATA_SCHEMA.md`, and `SCHEMA_CONTRACT.json`
EOF

cat > docs/00_state/PROJECT_STATE.md <<'EOF'
# JAE_Legacy_Audit — Project State (Derived Snapshot)

> Role: Derived executive snapshot  
> Authority: Non-canonical. For controlling current-state interpretation, defer to `AUDIT_CONTEXT.md`.  
> Update rule: Revise only after current-state, chronology, and generated audit surfaces are reconciled.

## System status
- pipeline operational
- manifest integrity validated
- route-level metrics validated
- Phase 6 backend and APA reporting surfaces active

## Current validated route state

### Route_A_Modern
- 6 validated epochs
- 5 validated adjacent innovation-velocity transitions
- 10 admitted source embedding files

### Route_B_Legacy
- 2 validated epochs
- 1 validated adjacent innovation-velocity transition
- structured / embedding parity validated for the admitted legacy set

## Modern coverage snapshot

### Fully completed epoch
- `2005–2009` ✅ complete

### Year coverage
| Year | Status |
|------|--------|
| 2000 | Covered |
| 2001 | Covered |
| 2002 | Missing |
| 2003 | Covered |
| 2004 | Missing |
| 2005 | Covered |
| 2006 | Covered |
| 2007 | Covered |
| 2008 | Covered |
| 2009 | Covered |
| 2010 | Missing |
| 2011 | Missing |
| 2012 | Covered |
| 2013 | Covered |
| 2014 | Missing |
| 2015 | Missing |
| 2016 | Missing |
| 2017 | Missing |
| 2018 | Covered |
| 2019 | Missing |
| 2020 | Missing |
| 2021 | Missing |
| 2022 | Covered |
| 2023 | Missing |
| 2024 | Covered |
| 2025 | Missing |
| 2026 | Covered |

## Current reporting state
- backend summaries generated
- machine-readable tables generated
- backend figures generated
- APA manuscript tables generated
- APA manuscript figures generated

## Interpretation boundary
- descriptive route-internal reporting is justified
- strong inferential claims remain constrained by uneven corpus coverage

## Next-step rule
Do not treat this file as the operational scheduler.
For the current official next work surface, defer to `AUDIT_CONTEXT.md`.
EOF

python3 - <<'PY'
from pathlib import Path

audit = Path("docs/00_state/audit.md")
if audit.exists() and not audit.is_symlink():
    text = audit.read_text(encoding="utf-8")
    marker = "> Role: Supplemental historical infrastructure audit"
    if marker not in text:
        block = """> Role: Supplemental historical infrastructure audit
> Authority: Supplemental only. For controlling current-state interpretation, defer to `AUDIT_CONTEXT.md`.
> Update rule: Historical context and infrastructure narrative; not the canonical state source."""
        audit.write_text(block + "\n\n" + text, encoding="utf-8")

debug = Path("docs/00_state/DEBUGGING_AUDIT_2026-03-22.md")
if debug.exists() and not debug.is_symlink():
    text = debug.read_text(encoding="utf-8")
    marker = "> Role: Bounded engineering audit"
    if marker not in text:
        block = """> Role: Bounded engineering audit
> Authority: Authoritative for the documented stabilization cycle only.
> Update rule: Historical engineering record; do not use as a global current-state replacement."""
        debug.write_text(block + "\n\n" + text, encoding="utf-8")

research = Path("RESEARCH_LOG.md")
marker = "## 2026-03-30 — Documentation authority reconciliation and Tier 00 closeout"
if research.exists():
    text = research.read_text(encoding="utf-8")
    if marker not in text:
        entry = """

## 2026-03-30 — Documentation authority reconciliation and Tier 00 closeout

Work completed:
- finalized the active documentation authority model
- confirmed `AUDIT_CONTEXT.md` remains the canonical current-state surface
- confirmed `PROJECT_STATE.md` is a derived snapshot rather than a controlling state file
- rebuilt `ACQUISITION_LOG.md` as the current operational acquisition runbook
- preserved root compatibility paths through symlink shims
- formalized the documentation policy and Tier 00 authority order

Operational result:
- repo documentation now has one controlling current-state surface, one canonical chronology, and subordinate Tier 00 audit/runbook files
- older path consumers remain supported without reopening engine work
- the repo/doc/audit-trail closeout is complete pending standard verification and commit

Interpretive note:
- historical entries remain preserved as chronology and are not rewritten as if they were current-state controllers
- current truth remains governed by `AUDIT_CONTEXT.md`
"""
        research.write_text(text.rstrip() + "\n" + entry + "\n", encoding="utf-8")
PY

echo "Final audit-doc closeout patch applied."
echo "Backup captured at: $BACKUP_DIR"
