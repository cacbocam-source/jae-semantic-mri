#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"
EXPECTED_PROJECT_ROOT="/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit"
NVME_MOUNT="/Volumes/Clemons_Data"

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

if [[ -d "$PROJECT_ROOT" ]]; then
    pass "Project root exists: $PROJECT_ROOT"
else
    fail "Project root missing: $PROJECT_ROOT"
fi

if [[ "$PROJECT_ROOT" == "$EXPECTED_PROJECT_ROOT" ]]; then
    pass "Project root resolves to expected NVMe path"
else
    fail "Project root mismatch: $PROJECT_ROOT"
fi

for dir in \
    "$PROJECT_ROOT/bins" \
    "$PROJECT_ROOT/data" \
    "$PROJECT_ROOT/scripts" \
    "$PROJECT_ROOT/tests"
do
    if [[ -d "$dir" ]]; then
        pass "Directory present: $dir"
    else
        fail "Missing required directory: $dir"
    fi
done

for dir in \
    "$PROJECT_ROOT/docs" \
    "$PROJECT_ROOT/logs" \
    "$PROJECT_ROOT/manuscript"
do
    if [[ -d "$dir" ]]; then
        pass "Optional directory present: $dir"
    else
        warn "Optional directory missing: $dir"
    fi
done

section "Core Files"

for file in \
    "$PROJECT_ROOT/config.py" \
    "$PROJECT_ROOT/main.py" \
    "$PROJECT_ROOT/data/manifests/pipeline_manifest.csv"
do
    if [[ -f "$file" ]]; then
        pass "File present: $file"
    else
        fail "Missing required file: $file"
    fi
done

section "Python Runtime"

if command -v python3 >/dev/null 2>&1; then
    pass "python3 found: $(command -v python3)"
    pass "Python version: $(python3 --version 2>&1)"
else
    fail "python3 not found in PATH"
fi

section "Disk Capacity"

if df -h "$NVME_MOUNT" >/dev/null 2>&1; then
    df -h "$NVME_MOUNT"
    pass "Disk usage reported for NVMe"
else
    fail "Unable to read disk usage for NVMe"
fi

section "Core Python Package Checks"

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

section "Extraction Package Checks"

python3 - <<'PY'
import importlib.util
import sys

packages = [
    "fitz",
    "pytesseract",
    "pdf2image",
]

failed = False
for name in packages:
    spec = importlib.util.find_spec(name)
    if spec is None:
        print(f"[FAIL] Extraction package missing: {name}")
        failed = True
    else:
        print(f"[PASS] Extraction package available: {name}")

sys.exit(1 if failed else 0)
PY
EXTRACT_STATUS=$?

if [[ "$EXTRACT_STATUS" -eq 0 ]]; then
    pass "Extraction package check passed"
else
    fail "Extraction package check failed"
fi

section "OCR System Dependency Checks"

if command -v tesseract >/dev/null 2>&1; then
    pass "tesseract found: $(command -v tesseract)"
else
    fail "tesseract not found in PATH"
fi

if command -v pdftoppm >/dev/null 2>&1; then
    pass "pdftoppm found: $(command -v pdftoppm)"
else
    fail "pdftoppm not found in PATH"
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