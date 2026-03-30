#!/usr/bin/env bash
set -euo pipefail

cd "${1:-$(pwd)}"

fail=0

need() {
  if [ ! -e "$1" ] && [ ! -L "$1" ]; then
    echo "MISSING: $1"
    fail=1
  fi
}

need_link() {
  if [ ! -L "$1" ]; then
    echo "NOT A SYMLINK: $1"
    fail=1
  else
    echo "$1 -> $(readlink "$1")"
  fi
}

echo "Checking canonical root files..."
need AUDIT_CONTEXT.md
need RESEARCH_LOG.md
need DATA_SCHEMA.md
need SCHEMA_CONTRACT.json

echo
echo "Checking Tier 00 files..."
need docs/00_state/README.md
need docs/00_state/AUDIT_CONTEXT.md
need docs/00_state/RESEARCH_LOG.md
need docs/00_state/ACQUISITION_LOG.md
need docs/00_state/PROJECT_STATE.md
need docs/00_state/DEBUGGING_AUDIT_2026-03-22.md
need docs/00_state/audit.md

echo
echo "Checking governance file..."
need docs/governance/DOCUMENTATION_POLICY.md

echo
echo "Checking root compatibility links..."
need_link PROJECT_STATE.md
need_link ACQUISITION_LOG.md
need_link DEBUGGING_AUDIT_2026-03-22.md

echo
echo "Checking tier mirrors..."
need_link docs/00_state/AUDIT_CONTEXT.md
need_link docs/00_state/RESEARCH_LOG.md
need_link docs/10_methods/DATA_SCHEMA.md
need_link docs/10_methods/SCHEMA_CONTRACT.json

echo
echo "Checking generated-doc fixed paths..."
need docs/INGESTION_LOG.md
need docs/CORPUS_COVERAGE.md
need docs/PIPELINE_AUDIT.md

echo
grep -q "Role: Operational acquisition runbook" docs/00_state/ACQUISITION_LOG.md || { echo "ACQUISITION_LOG header missing"; fail=1; }
grep -q "Role: Derived executive snapshot" docs/00_state/PROJECT_STATE.md || { echo "PROJECT_STATE header missing"; fail=1; }
grep -q "Documentation authority reconciliation and Tier 00 closeout" RESEARCH_LOG.md || { echo "RESEARCH_LOG reconciliation entry missing"; fail=1; }

echo
if [ "$fail" -ne 0 ]; then
  echo "Verification failed."
  exit 1
else
  echo "Verification passed."
fi
