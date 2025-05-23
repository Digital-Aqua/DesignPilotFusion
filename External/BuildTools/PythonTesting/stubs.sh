#!/bin/bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PACKAGE="$1"

TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TEMP_DIR"' EXIT

echo "Running stubgen."
stubgen -p "$PACKAGE" --include-docstrings -o "$TEMP_DIR"

for FILE in $(cd "$TEMP_DIR/$PACKAGE" && find . -name "*.pyi"); do
    echo "================================================"
    echo "$FILE"
    echo "================================================"
    cat "$TEMP_DIR/$PACKAGE/$FILE"
    echo ""
done
