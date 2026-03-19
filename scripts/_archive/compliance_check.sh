#!/usr/bin/env bash
set -euo pipefail

echo "---------------------------------------------"
echo "JAE Legacy Audit — Research Compliance Check"
echo "---------------------------------------------"
echo

echo "1. Confirm lawful access to data sources."
echo "2. Verify API and publisher policies."
echo "3. Ensure rate limiting and backoff are implemented."
echo "4. Confirm corpus will not be redistributed."
echo "5. Verify ledger tracking and audit logging."
echo

echo "If any item above is uncertain, pause development"
echo "and review docs/RESEARCH_COMPLIANCE.md"
echo

echo "Compliance check complete."