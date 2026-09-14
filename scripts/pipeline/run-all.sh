#!/bin/bash
# Run four stages in a fresh workspace, then publish one complete snapshot.
# Usage: ./run-all.sh [source-dir]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_INPUT="${1:-$SCRIPT_DIR/../../sample-docs}"
if [ ! -d "$SOURCE_INPUT" ]; then
    echo "run-all: source directory not found: $SOURCE_INPUT" >&2
    exit 1
fi
SOURCE_ABS="$(cd "$SOURCE_INPUT" && pwd)"
command -v python3 >/dev/null || { echo "run-all: python3 is required" >&2; exit 1; }

if [ -e "$SCRIPT_DIR/output" ] && [ ! -L "$SCRIPT_DIR/output" ]; then
    echo "run-all: output is a legacy directory; move it to a backup before running again" >&2
    exit 1
fi

# Hold the lock through promotion. A competing run fails before any stage runs.
if ! mkdir "$SCRIPT_DIR/.run-lock" 2>/dev/null; then
    echo "run-all: another run holds .run-lock; check its owner before removing a stale lock" >&2
    exit 1
fi
LOCK_RUN_ID=""
cleanup() {
    if [ ! -f "$SCRIPT_DIR/.run-lock/run-id" ] ||
       [ "$(cat "$SCRIPT_DIR/.run-lock/run-id")" = "$LOCK_RUN_ID" ]; then
        rm -f "$SCRIPT_DIR/.run-lock/run-id"
        rmdir "$SCRIPT_DIR/.run-lock"
    fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
mkdir -p "$SCRIPT_DIR/.runs"
RUN_DIR="$(mktemp -d "$SCRIPT_DIR/.runs/run.XXXXXXXX")"
LOCK_RUN_ID="$(basename "$RUN_DIR")"
printf '%s\n' "$LOCK_RUN_ID" > "$SCRIPT_DIR/.run-lock/run-id"
cd "$RUN_DIR"

bash "$SCRIPT_DIR/01-fetch.sh" "$SOURCE_ABS"
python3 "$SCRIPT_DIR/validate-run.py" raw "$RUN_DIR"
bash "$SCRIPT_DIR/02-clean.sh"
python3 "$SCRIPT_DIR/validate-run.py" clean "$RUN_DIR"
bash "$SCRIPT_DIR/03-process.sh"
python3 "$SCRIPT_DIR/validate-run.py" processed "$RUN_DIR"
bash "$SCRIPT_DIR/04-save.sh"
python3 "$SCRIPT_DIR/validate-run.py" output "$RUN_DIR"
python3 "$SCRIPT_DIR/validate-run.py" publish "$RUN_DIR"
echo "run-all: pipeline finished (output in $SCRIPT_DIR/output/; run $(basename "$RUN_DIR"))"
