#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"
EXPECTED_PROJECT_ROOT="/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit"
NVME_MOUNT="/Volumes/Clemons_Data"

echo "-----------------------------------------"
echo "Semantic MRI Pipeline Startup Check"
echo "-----------------------------------------"

if [[ ! -d "$NVME_MOUNT" ]]; then
    echo "ERROR: NVMe drive Clemons_Data is not mounted."
    exit 1
fi

echo "✓ NVMe mount detected"

if [[ ! -d "$PROJECT_ROOT" ]]; then
    echo "ERROR: Project root missing:"
    echo "$PROJECT_ROOT"
    exit 1
fi

echo "✓ Project root exists"

if [[ "$PROJECT_ROOT" != "$EXPECTED_PROJECT_ROOT" ]]; then
    echo "ERROR: Project root does not resolve to expected NVMe path"
    echo "Expected: $EXPECTED_PROJECT_ROOT"
    echo "Actual:   $PROJECT_ROOT"
    exit 1
fi

echo "✓ Project root path verified"

REQUIRED_DIRS=(
    "$PROJECT_ROOT/bins"
    "$PROJECT_ROOT/data"
    "$PROJECT_ROOT/scripts"
    "$PROJECT_ROOT/tests"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [[ ! -d "$dir" ]]; then
        echo "ERROR: Missing required directory: $dir"
        exit 1
    fi
done

echo "✓ Directory structure verified"

REQUIRED_FILES=(
    "$PROJECT_ROOT/config.py"
    "$PROJECT_ROOT/main.py"
    "$PROJECT_ROOT/data/manifests/pipeline_manifest.csv"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "ERROR: Missing required file: $file"
        exit 1
    fi
done

echo "✓ Core files verified"

echo "-----------------------------------------"
echo "SYSTEM STATUS: READY"
echo "-----------------------------------------"