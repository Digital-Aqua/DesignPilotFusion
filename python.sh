#!/bin/bash
# A wrapper for the specific Python interpreter used by Autodesk Fusion.
# Useful for IDEs to find the correct interpreter.
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

. "$DIR/build.sh"
if [ -z "${AUTODESK_PYTHON_PATH}" ]; then
    AUTODESK_PYTHON_PATH="$(find_autodesk_python_path | one_result 2>/dev/null || true)"
fi

exec "${AUTODESK_PYTHON_PATH}" "$@"
