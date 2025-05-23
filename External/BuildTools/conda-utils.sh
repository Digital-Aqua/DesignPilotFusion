#!/bin/bash
set -eo pipefail
BUILD_UTILS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

. "$BUILD_UTILS_DIR/build-utils.sh"

function check_conda() {
    if ! command -v conda &> /dev/null; then
        echo "Conda could not be found. Please install it from https://conda-forge.org/download/"
        exit 1
    fi
}
check_conda
eval "$(conda shell.bash hook)"


PREFIX=""
function set_conda_prefix() {
    PREFIX="$1"
}


function conda_() {
    (
        conda "$@" \
        || fail 'conda command failed.'
    ) 2>&1 | background
}


function conda_create() {
    echo_task "Creating conda environment."
    conda_ create --prefix "$PREFIX" --yes
}


function conda_activate() {
    [ -n "${PREFIX}" ] \
        || fail "Can't activate a conda environment without a prefix."
    [ -d "${PREFIX}" ] \
        || conda_create
    echo_task "Activating conda environment."
    conda_ activate "$PREFIX"
}


function conda_env_update() {
    local FILE="$1"
    echo_task "Updating conda environment: $FILE"
    conda_ env update --prefix "$PREFIX" --file "$FILE"
}


function conda_install() {
    echo_task "Installing packages: $@"
    conda_ install --prefix "$PREFIX" -c conda-forge -y "$@"
}


function conda_add_packages() {
    local PACKAGES_DIR="$1"
    local PTH_NAME="$2"
    echo_task "Adding packages to conda environment: $PACKAGES_DIR"
    local SITE_PACKAGES="$(
        echo "$PREFIX/lib/python"*"/site-packages" \
        | grep -v '\*' \
        | head -n 1
    )"
    echo "$PACKAGES_DIR" > "$SITE_PACKAGES/$PTH_NAME.pth"
}


function conda_add_package_pth() {
    local PACKAGE="$1"
    local PTH_NAME="$2"
    local ANY_PTH=false
    echo_task "Adding packages to conda environment: $PACKAGE"
    for SP in "$PREFIX/lib/python"*"/site-packages"; do
        echo "$PACKAGE" > "$SP/$PTH_NAME.pth"
        ANY_PTH=true
    done
    if ! "$ANY_PTH"; then
        fail "Failed to add package to conda environment: $PACKAGE"
    fi
}
