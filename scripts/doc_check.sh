#!/usr/bin/env bash
set -euo pipefail

DOC_DIR="docs"

if [[ ! -d "$DOC_DIR" ]]; then
    echo "ERROR: Documentation directory not found: $DOC_DIR"
    exit 1
fi

echo "Checking documentation timestamps..."

if find "$DOC_DIR" -type f -name "*.md" -mtime +7 -print | grep -q .; then
    find "$DOC_DIR" -type f -name "*.md" -mtime +7 -print
    echo
    echo "Files listed above have not been updated in over 7 days."
else
    echo "All markdown documentation files have been updated within the last 7 days."
fi