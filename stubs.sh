#!/bin/bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHONPATH="$DIR/External/rxprop/Source:$DIR/Source/Packages:$PYTHONPATH"
"$DIR/External/BuildTools/PythonTesting/stubs.sh" "$@"
