#!/bin/bash
set -eo pipefail

function echo_colour() {
    COLOUR="$1"
    shift
    ARGS=()
    while [[ "$1" =~ ^- ]]; do
        ARGS+=("$1")
        shift
    done
    if [ -t 1 ]; then
        echo "${ARGS[@]}" -e "\033[${COLOUR}m$@\033[0m" >&2
    else
        echo "${ARGS[@]}" "$@" >&2
    fi
}

function echo_title() {
    echo_colour "1;36" "$@"
}

function echo_key_value() {
    KEY="$1"
    VALUE="$2"
    echo_colour "0;32" -n "  ${KEY}"
    echo_colour "0;" ": ${VALUE}"
}

function echo_task() {
    echo_colour "0;36" "  $@"
}

function echo_warning() {
    echo_colour "1;33" "  Warning: $@"
}

function echo_error() {
    echo_colour "1;31" "  Error: $@"
}

export MAIN_PID=$$
trap 'exit 1' SIGUSR1
function fail() {
    echo_error "$@"
    kill -SIGUSR1 $MAIN_PID 2>/dev/null || exit 1
}

function background() {
    while read -r LINE; do
        echo_colour "0;90" "  | ${LINE}"
    done
}

function one_result() {
    RESULTS=()
    while read -r LINE; do
        RESULTS+=("$LINE")
    done
    if [ ${#RESULTS[@]} -eq 0 ]; then
        echo_error "No matches found."
        exit 1
    fi
    if [ ${#RESULTS[@]} -gt 1 ]; then
        echo_warning "Multiple results found:"
        for RESULT in "${RESULTS[@]}"; do
            echo_warning "  ${RESULT}"
        done
        echo_warning "Defaulting to first match."
    fi
    echo "${RESULTS[0]}"
}
