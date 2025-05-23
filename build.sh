#!/bin/bash
set -eo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


. "$DIR/External/BuildTools/build-utils.sh"
. "$DIR/External/BuildTools/conda-utils.sh"


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
            DO_DEV_SETUP=true
            ;;
        --zip)
            DO_ZIP=true
            ;;
        *)
            ;;
    esac
done
if [ ! -d ".conda" ]; then
    echo "No conda environment found. Setting up development environment."
    DO_DEV_SETUP=true
fi


ADDIN_NAME="DesignPilotFusion"
SOURCE_DIR="${DIR}/Source"
CACHE_DIR="${DIR}/.cache"
BUILD_DIR="${DIR}/.build"
ADDIN_DIR="${BUILD_DIR}/${ADDIN_NAME}"
PREFIX_DIR="${DIR}/.conda"
set_conda_prefix "$PREFIX_DIR"

COMMIT_HASH="${COMMIT_HASH:-$(git rev-parse --short HEAD)}"
COMMIT_DIRTY="${COMMIT_DIRTY:-$(git status --porcelain | grep -q . && echo 'true' || :)}"
BUILD_VERSION="${BUILD_VERSION:-${COMMIT_HASH}${COMMIT_DIRTY:+-dirty}${DEBUG:+-debug}}"



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


function dev_setup() {
    echo_title "Setting up development environment."

    conda_activate

    # Install the same Python version as Fusion
    FUSION_PYTHON="$( find_autodesk_python_path | one_result )"
    [ -f "${FUSION_PYTHON}" ] \
        || fail "Failed to find Fusion's Python executable."
    FUSION_PYTHON_VERSION="$( "${FUSION_PYTHON}" --version | sed 's/ /=/')"
    [ -n "${FUSION_PYTHON_VERSION}" ] \
        || fail "Failed to get Fusion's Python version."
    conda_install "${FUSION_PYTHON_VERSION,,}"
    echo "$FUSION_PYTHON_VERSION" \
        | sed 's/=/ ==/g' \
        >> "$PREFIX_DIR/conda-meta/pinned"

    # Install Autodesk defs
    AUTODESK_DEFS_PATH="$( find_autodesk_defs_path | one_result || true )"
    [ -d "${AUTODESK_DEFS_PATH}" ] \
        || fail "Failed to find Autodesk defs."
    echo_task "Copying Autodesk defs from $AUTODESK_DEFS_PATH"
    mkdir -p "$CACHE_DIR"
    cp -rf "$AUTODESK_DEFS_PATH" "$CACHE_DIR" \
        || fail "Failed to copy Autodesk defs."

    # Add environment.yaml files to conda environment.
    conda_env_update "$DIR/External/BuildTools/PythonTesting/environment.yaml"
    conda_env_update "$DIR/External/rxprop/environment.yaml"
    conda_env_update "$DIR/environment.yaml"
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

    echo_task "Copying packages."
    cp -r "${SOURCE_DIR}/Packages" "${ADDIN_DIR}/Packages"

    echo_task "Copying pip packages to add-in."
    local SITE_PACKAGES="$(
        echo "$PREFIX_DIR/lib/python"*"/site-packages" \
        | grep -v '\*' \
        | one_result
    )"
    
    local BLACKLIST="$( cat "$DIR/Source/blacklist.txt" )"
    local INSTALLED=""
    for PACKAGE in "$SITE_PACKAGES"/*; do
        [ -d "$PACKAGE" ] \
            && ( ! echo "$BLACKLIST" | grep -q "^\s*$PACKAGE\s*$" ) \
            && ( ! [[ "$PACKAGE" =~ \.dist-info$|^_ ]] ) \
            || continue
        cp -r "$SITE_PACKAGES/$PACKAGE" "${ADDIN_DIR}/Packages/$PACKAGE"
        INSTALLED="${INSTALLED:+$INSTALLED, }$PACKAGE"
    done
    echo_key_value "Installed packages" "$INSTALLED"
    echo_task "Build complete."
}


function bundle() {
    echo_title "Bundling add-in."
    (
        zip -r "${BUILD_DIR}/${ADDIN_NAME}.zip" "${ADDIN_DIR}" \
        || fail 'Failed to bundle add-in.'
    ) 2>&1 | background
}


if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    $DO_DEV_SETUP && dev_setup || :
    conda_activate
    $DO_CLEAN && clean || :
    $DO_BUILD && build || :
    $DO_ZIP && bundle || :
fi
