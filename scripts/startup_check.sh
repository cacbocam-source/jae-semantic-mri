#!/usr/bin/env bash
set -euo pipefail

NVME_MOUNT="/Volumes/Clemons_Data"
PROJECT_ROOT="$HOME/_Anchors/Research_Data/JAE_Legacy_Audit"
EXPECTED_TARGET="/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit"

echo "-----------------------------------------"
echo "Semantic MRI Pipeline Startup Check"
echo "-----------------------------------------"

# Run research compliance guardrail
if [[ ! -x "$PROJECT_ROOT/scripts/compliance_check.sh" ]]; then
    echo "ERROR: compliance_check.sh missing or not executable."
    exit 1
fi
"$PROJECT_ROOT/scripts/compliance_check.sh"

# Check NVMe mount
if [[ ! -d "$NVME_MOUNT" ]]; then
    echo "ERROR: NVMe drive Clemons_Data is not mounted."
    exit 1
fi

echo "✓ NVMe mount detected"

# Check project root exists
if [[ ! -e "$PROJECT_ROOT" ]]; then
    echo "ERROR: Project anchor path missing:"
    echo "$PROJECT_ROOT"
    exit 1
fi

echo "✓ Anchor path exists"

# Verify symlink
if [[ ! -L "$PROJECT_ROOT" ]]; then
    echo "ERROR: Project root is not a symlink."
    exit 1
fi

echo "✓ Anchor is a symlink"

# Verify correct symlink target
TARGET=$(readlink "$PROJECT_ROOT")

if [[ "$TARGET" != "$EXPECTED_TARGET" ]]; then
    echo "ERROR: Symlink points to wrong location"
    echo "Expected: $EXPECTED_TARGET"
    echo "Actual:   $TARGET"
    exit 1
fi

echo "✓ Symlink target verified"

# Verify critical directories
REQUIRED_DIRS=(
    "$PROJECT_ROOT/bins"
    "$PROJECT_ROOT/data"
    "$PROJECT_ROOT/logs"
    "$PROJECT_ROOT/docs"
    "$PROJECT_ROOT/manuscript"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [[ ! -d "$dir" ]]; then
        echo "ERROR: Missing required directory: $dir"
        exit 1
    fi
done

echo "✓ Directory structure verified"

echo "-----------------------------------------"
echo "SYSTEM STATUS: READY"
echo "-----------------------------------------"