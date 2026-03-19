#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="/Volumes/Clemons_Data/_Anchors/Research_Data/JAE_Legacy_Audit"
DEFAULT_BRANCH="main"

usage() {
    echo "Usage: ./scripts/research_snapshot.sh \"commit message\""
    exit 1
}

if [[ $# -lt 1 ]]; then
    usage
fi

COMMIT_MESSAGE="$1"

cd "$PROJECT_ROOT"

echo "-----------------------------------------"
echo "Semantic MRI Research Snapshot"
echo "-----------------------------------------"

if [[ ! -d .git ]]; then
    echo "ERROR: Not a git repository: $PROJECT_ROOT"
    exit 1
fi

echo
echo "[1/6] Running startup checks..."
./scripts/startup_check.sh

echo
echo "[2/6] Running workspace doctor..."
./scripts/doctor.sh

echo
echo "[3/6] Running processor benchmark tests..."
python3 tests/test_benchmarks.py

echo
echo "[4/7] Running section export tests..."
python3 tests/test_section_exports.py

echo
echo "[5/7] Running year resolution tests..."
python3 tests/test_year_resolution.py

echo
echo "[6/7] Staging tracked project changes..."
git add .

echo
echo "Git status preview:"
git status --short

echo
read -r -p "Proceed with commit and push? [y/N]: " CONFIRM
case "$CONFIRM" in
    y|Y|yes|YES)
        ;;
    *)
        echo "Snapshot canceled."
        exit 0
        ;;
esac

if git diff --cached --quiet; then
    echo "No staged changes to commit."
    exit 0
fi

echo
echo "[7/7] Creating commit..."
git commit -m "$COMMIT_MESSAGE"

echo
echo "Pushing to origin/$DEFAULT_BRANCH..."
git push -u origin "$DEFAULT_BRANCH"

echo
echo "-----------------------------------------"
echo "Research snapshot complete."
echo "-----------------------------------------"
