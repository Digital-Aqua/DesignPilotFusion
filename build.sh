#!/bin/bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


# TODO: Use a conda development environment to ensure prerequisites
# TODO: Use pip to gather dependencies


DEBUG="${DEBUG:-}"
DO_DEV_SETUP=false
DO_CLEAN=false
DO_BUILD=true
DO_ZIP=false
for ARG in "$@"; do
    case "${ARG}" in
        --clean)
            DO_CLEAN=true
            ;;
        --debug)
            DEBUG=true
            ;;
        --dev-setup)
            DO_BUILD=false
            DO_ZIP=false
            DO_DEV_SETUP=true
            ;;
        --zip)
            DO_ZIP=true
            ;;
        *)
            ;;
    esac
done


ADDIN_NAME="DesignPilotFusion"
SOURCE_DIR="${DIR}/Source"
CACHE_DIR="${DIR}/.cache"
BUILD_DIR="${DIR}/.build"
ADDIN_DIR="${BUILD_DIR}/${ADDIN_NAME}"


COMMIT_HASH="${COMMIT_HASH:-$(git rev-parse --short HEAD)}"
COMMIT_DIRTY="${COMMIT_DIRTY:-$(git status --porcelain | grep -q . && echo 'true' || :)}"
BUILD_VERSION="${BUILD_VERSION:-${COMMIT_HASH}${COMMIT_DIRTY:+-dirty}${DEBUG:+-debug}}"


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

function background() {
    while read -r LINE; do
        echo_colour "0;90" "  | ${LINE}"
    done
}

function find_matching_path() {
    ROOT="$1"
    RX="$2"
    MATCHING_PATHS=( "$(find "${ROOT}" -type f -regex "${RX}" 2>/dev/null)" )
    N_MATCHES=${#MATCHING_PATHS[@]}
    if [ "${N_MATCHES}" -eq 0 ]; then
        echo_error "No matching path found."
        exit 1
    elif [ "${N_MATCHES}" -gt 1 ]; then
        echo_warning "Multiple matching paths found:"
        for PATH in "${MATCHING_PATHS[@]}"; do
            echo_warning "  ${PATH}"
        done
        echo_warning "Defaulting to first match."
    fi
    echo "${MATCHING_PATHS[0]}"
}


function find_autodesk_defs_path() {
    {
        echo /*/Users/*'/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/Python/defs'
        echo /mnt/*/Users/*'/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/Python/defs'
    } | grep -v '\*'
}

function find_autodesk_python_path() {
    {
        echo /*/Users/*/AppData/Local/Autodesk/webdeploy/production/*/Python/python.exe
        echo /mnt/*/Users/*/AppData/Local/Autodesk/webdeploy/production/*/Python/python.exe
    } | grep -v '\*'
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
    echo_key_value "  Path" "${RESULTS[0]}"
    echo "${RESULTS[0]}"
}


function dev_setup() {

    echo_title "Setting up development environment."

    AUTODESK_DEFS_PATH="$( find_autodesk_defs_path | one_result || true )"
    echo_task "Copying Autodesk defs to cache."
    mkdir -p "${CACHE_DIR}/defs"
    cp -r "${AUTODESK_DEFS_PATH}" "${CACHE_DIR}"
}


function clean() {

    echo_title "Cleaning build directory."
    rm -rf "${BUILD_DIR}"

}


function build() {

    echo_title "Building add-in."
    echo_key_value "Version" "${BUILD_VERSION}"

    mkdir -p "${ADDIN_DIR}"

    echo_task "Building manifest."
    cat "${SOURCE_DIR}/manifest.template" \
        | BUILD_VERSION="${BUILD_VERSION}" \
          IS_DEBUG="$( [ -n "${DEBUG}" ] && echo "true" || echo "false" )" \
          NOT_DEBUG="$( [ -n "${DEBUG}" ] && echo "false" || echo "true" )" \
          envsubst \
        > "${ADDIN_DIR}/${ADDIN_NAME}.manifest"

    echo_task "Building config."

    cp "${SOURCE_DIR}/${ADDIN_NAME}.py" "${ADDIN_DIR}"
    cp "${SOURCE_DIR}/config.py" "${ADDIN_DIR}"

    echo_task "Copying libraries."
    cp -r "${SOURCE_DIR}/Packages" "${ADDIN_DIR}/lib"

    # TODO: get pip modules and copy them into the add-in 'lib' directory

    echo_task "Build complete."

}


function bundle() {
    echo_title "Bundling add-in."
    zip -r "${BUILD_DIR}/${ADDIN_NAME}.zip" "${ADDIN_DIR}" | background
}


if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    [ "${DO_DEV_SETUP}" ] && dev_setup || :
    [ "${DO_CLEAN}" ] && clean || :
    [ "${DO_BUILD}" ] && build || :
    [ "${DO_ZIP}" ] && bundle || :
fi
