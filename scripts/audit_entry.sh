#!/usr/bin/env bash

DATE=$(date +"%Y-%m-%d")

echo "Enter change description:"
read CHANGE

echo "" >> docs/audit.md
echo "## Change — $DATE" >> docs/audit.md
echo "$CHANGE" >> docs/audit.md

echo "Audit entry added."