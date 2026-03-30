#!/usr/bin/env bash
set -euo pipefail

cd "${1:-$(pwd)}"

fail=0

require_path() {
  if [ ! -e "$1" ] && [ ! -L "$1" ]; then
    echo "MISSING: $1"
    fail=1
  fi
}

require_symlink() {
  if [ ! -L "$1" ]; then
    echo "NOT A SYMLINK: $1"
    fail=1
  else
    echo "$1 -> $(readlink "$1")"
  fi
}

echo "Checking canonical root files..."
require_path AUDIT_CONTEXT.md
require_path RESEARCH_LOG.md
require_path DATA_SCHEMA.md
require_path SCHEMA_CONTRACT.json

echo
echo "Checking Tier 00 files..."
require_path docs/00_state/ACQUISITION_LOG.md
require_path docs/00_state/DEBUGGING_AUDIT_2026-03-22.md
require_path docs/00_state/PROJECT_STATE.md
require_path docs/00_state/audit.md
require_path docs/00_state/README.md

echo
echo "Checking governance file..."
require_path docs/governance/DOCUMENTATION_POLICY.md

echo
echo "Checking compatibility shims..."
require_symlink ACQUISITION_LOG.md
require_symlink DEBUGGING_AUDIT_2026-03-22.md
require_symlink PROJECT_STATE.md
require_symlink docs/00_state/AUDIT_CONTEXT.md
require_symlink docs/00_state/RESEARCH_LOG.md
require_symlink docs/10_methods/DATA_SCHEMA.md
require_symlink docs/10_methods/SCHEMA_CONTRACT.json

echo
echo "Checking generated-doc fixed paths remain present..."
require_path docs/INGESTION_LOG.md
require_path docs/CORPUS_COVERAGE.md
require_path docs/PIPELINE_AUDIT.md

echo
if [ "$fail" -ne 0 ]; then
  echo "Verification failed."
  exit 1
else
  echo "Verification passed."
fi
