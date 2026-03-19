#!/usr/bin/env bash
set -euo pipefail

AUDIT_FILE="docs/audit.md"
DATE="$(date +"%Y-%m-%d")"
TMP_FILE="$(mktemp)"

cleanup() {
    rm -f "$TMP_FILE"
}
trap cleanup EXIT

if [[ ! -f "$AUDIT_FILE" ]]; then
    echo "ERROR: Audit file not found: $AUDIT_FILE"
    exit 1
fi

echo "Enter audit entry below."
echo "Finish with CTRL + D on a new line."
echo

cat > "$TMP_FILE"

if [[ ! -s "$TMP_FILE" ]]; then
    echo "ERROR: Audit entry cannot be empty."
    exit 1
fi

echo
echo "----------------------------------------"
echo "Audit entry preview"
echo "----------------------------------------"
echo
cat "$TMP_FILE"
echo
echo "----------------------------------------"

read -r -p "Append this entry to $AUDIT_FILE? [y/N]: " CONFIRM

case "$CONFIRM" in
    y|Y|yes|YES)
        {
            echo
            echo "## Change — $DATE"
            cat "$TMP_FILE"
        } >> "$AUDIT_FILE"
        echo "Audit entry added."
        ;;
    *)
        echo "Audit entry canceled."
        exit 0
        ;;
esac