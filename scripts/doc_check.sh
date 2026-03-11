#!/usr/bin/env bash

DOC_DIR="docs"

echo "Checking documentation timestamps..."

find $DOC_DIR -type f -name "*.md" -mtime +7 -print

echo "Files listed above have not been updated in over 7 days."