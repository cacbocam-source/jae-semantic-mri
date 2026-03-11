#!/usr/bin/env bash
set -euo pipefail

NVME_MOUNT="/Volumes/Clemons_Data"
PROJECT_ROOT="$HOME/_Anchors/Research_Data/JAE_Legacy_Audit"
EXPECTED_TARGET="/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit"

PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0

pass() {
    printf '[PASS] %s\n' "$1"
    PASS_COUNT=$((PASS_COUNT + 1))
}

warn() {
    printf '[WARN] %s\n' "$1"
    WARN_COUNT=$((WARN_COUNT + 1))
}

fail() {
    printf '[FAIL] %s\n' "$1"
    FAIL_COUNT=$((FAIL_COUNT + 1))
}

section() {
    printf '\n=== %s ===\n' "$1"
}

printf '=========================================\n'
printf 'Semantic MRI Workspace Doctor\n'
printf '=========================================\n'

section "Filesystem"

if [[ -d "$NVME_MOUNT" ]]; then
    pass "NVMe mountpoint exists: $NVME_MOUNT"
else
    fail "NVMe mountpoint missing: $NVME_MOUNT"
fi

if mount | grep -F " on $NVME_MOUNT " >/dev/null; then
    pass "NVMe is mounted"
else
    fail "NVMe is not mounted"
fi

if [[ -e "$PROJECT_ROOT" ]]; then
    pass "Anchor path exists: $PROJECT_ROOT"
else
    fail "Anchor path missing: $PROJECT_ROOT"
fi

if [[ -L "$PROJECT_ROOT" ]]; then
    pass "Anchor path is a symlink"
else
    fail "Anchor path is not a symlink"
fi

if [[ -L "$PROJECT_ROOT" ]]; then
    TARGET="$(readlink "$PROJECT_ROOT")"
    if [[ "$TARGET" == "$EXPECTED_TARGET" ]]; then
        pass "Symlink target is correct"
    else
        fail "Symlink target mismatch: $TARGET"
    fi
fi

for dir in \
    "$PROJECT_ROOT/bins" \
    "$PROJECT_ROOT/data" \
    "$PROJECT_ROOT/logs" \
    "$PROJECT_ROOT/scripts" \
    "$PROJECT_ROOT/docs"
do
    if [[ -d "$dir" ]]; then
        pass "Directory present: $dir"
    else
        fail "Missing directory: $dir"
    fi
done

section "Python Runtime"

if command -v python3 >/dev/null 2>&1; then
    pass "python3 found: $(command -v python3)"
else
    fail "python3 not found in PATH"
fi

if command -v python3 >/dev/null 2>&1; then
    PY_VERSION="$(python3 --version 2>&1)"
    pass "Python version: $PY_VERSION"
fi

section "Disk Capacity"

if df -h "$NVME_MOUNT" >/dev/null 2>&1; then
    df -h "$NVME_MOUNT"
    pass "Disk usage reported for NVMe"
else
    fail "Unable to read disk usage for NVMe"
fi

section "Python Package Checks"

python3 - <<'PY'
import importlib.util
import sys

packages = [
    "torch",
    "numpy",
    "pandas",
]

failed = False
for name in packages:
    spec = importlib.util.find_spec(name)
    if spec is None:
        print(f"[FAIL] Python package missing: {name}")
        failed = True
    else:
        print(f"[PASS] Python package available: {name}")

sys.exit(1 if failed else 0)
PY
PACKAGE_STATUS=$?

if [[ "$PACKAGE_STATUS" -eq 0 ]]; then
    pass "Core Python package check passed"
else
    fail "Core Python package check failed"
fi

section "MPS / Torch Check"

python3 - <<'PY'
import sys

try:
    import torch
except Exception as exc:
    print(f"[FAIL] Unable to import torch: {exc}")
    sys.exit(1)

print(f"[PASS] torch version: {torch.__version__}")

if hasattr(torch.backends, "mps"):
    if torch.backends.mps.is_available():
        print("[PASS] MPS backend is available")
    else:
        print("[WARN] MPS backend is not available")
    if torch.backends.mps.is_built():
        print("[PASS] PyTorch built with MPS support")
    else:
        print("[FAIL] PyTorch not built with MPS support")
        sys.exit(1)
else:
    print("[FAIL] torch.backends.mps not present")
    sys.exit(1)
PY
MPS_STATUS=$?

if [[ "$MPS_STATUS" -eq 0 ]]; then
    pass "PyTorch MPS diagnostic passed"
else
    fail "PyTorch MPS diagnostic failed"
fi

section "Configuration Sanity"

if [[ -f "$PROJECT_ROOT/config.py" ]]; then
    pass "config.py present"
else
    fail "config.py missing"
fi

if [[ -f "$PROJECT_ROOT/main.py" ]]; then
    pass "main.py present"
else
    fail "main.py missing"
fi

section "Summary"

printf 'Pass: %d\n' "$PASS_COUNT"
printf 'Warn: %d\n' "$WARN_COUNT"
printf 'Fail: %d\n' "$FAIL_COUNT"

if [[ "$FAIL_COUNT" -gt 0 ]]; then
    printf '\nSYSTEM STATUS: NOT READY\n'
    exit 1
else
    printf '\nSYSTEM STATUS: READY\n'
    exit 0
fi