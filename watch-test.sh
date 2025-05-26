#!/bin/bash
set -eo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"


list_files() {
    while [ -n "$1" ]; do
        ROOT="$1"
        (
            cd "$ROOT"
            git ls-files --cached --others --exclude-standard --full-name \
            | while read -r FILE; do
                echo "$ROOT/$FILE"
            done
        )
        shift
    done
}

(
    MD5SUM=""
    while true; do
        FILES=()
        mapfile -t FILES < <(
            list_files "$DIR" "$DIR/External/rxprop" \
            | grep -E '\.py$' \
            | while read -r FILE; do
                [ -f "$FILE" ] && echo "$FILE";
            done
        )
        NEW_MD5SUM=""
        for FILE in "${FILES[@]}"; do
            NEW_MD5SUM="$NEW_MD5SUM$(md5sum "$FILE")"
        done
        if [ "$NEW_MD5SUM" != "$MD5SUM" ]; then
            MD5SUM="$NEW_MD5SUM"
            pytest "$@" || true
            echo "Watching ${#FILES[@]} files."
        fi
        sleep 0.1
    done
)
