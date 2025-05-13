#!/bin/bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


DEBUG="${DEBUG:-}"
CLEAN_FIRST=
for ARG in "$@"; do
    case "${ARG}" in
        --clean)
            CLEAN_FIRST=true
            ;;
        --debug)
            DEBUG=true
            ;;
        *)
            ;;
    esac
done


ADDIN_NAME="DesignPilotFusion"
SOURCE_DIR="${DIR}/Source"
BUILD_DIR="${DIR}/.build"
ADDIN_DIR="${BUILD_DIR}/${ADDIN_NAME}"


COMMIT_HASH="${COMMIT_HASH:-$(git rev-parse --short HEAD)}"
COMMIT_DIRTY="${COMMIT_DIRTY:-$(git status --porcelain | grep -q . && echo 'true' || :)}"
BUILD_VERSION="${BUILD_VERSION:-${COMMIT_HASH}${COMMIT_DIRTY:+-dirty}${DEBUG:+-debug}}"


function echo_title() {
    if [ -t 1 ]; then
        echo -e "\033[1;36m$@\033[0m"
    else
        echo "$@"
    fi
}

function echo_key_value() {
    KEY="$1"
    VALUE="$2"
    if [ -t 1 ]; then
        echo -e "  \033[0;32m${KEY}\033[0m: \033[0m${VALUE}\033[0m"
    else
        echo "  ${KEY}: ${VALUE}"
    fi
}

function echo_task() {
    if [ -t 1 ]; then
        echo -e "  \033[0;36m$@\033[0m"
    else
        echo "  $@"
    fi
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

    echo_task "Bundling Add-In."
    (
        cd "${ADDIN_DIR}"
        zip -r "${BUILD_DIR}/${ADDIN_NAME}.zip" .
    )

    echo_task "Build complete."

}


[ "${CLEAN_FIRST}" ] && clean || :
build
