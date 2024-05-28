#!/bin/bash

PROJECT_ROOT="$(realpath "$(dirname "$0")/../")"
TARGET_DIR="$PROJECT_ROOT/../../../up-tck/up_client_socket/cpp"

format_files() {
    local dir=$1
    echo "Running clang-format on all files in '$dir'"
    pushd "$dir" > /dev/null
    shopt -s globstar
    for f in **/*.h **/*.cpp; do
        echo
        echo "Checking file '$f'"
        clang-format -i "$f"
    done
    popd > /dev/null
}

# Format files in the original PROJECT_ROOT directory
format_files "$PROJECT_ROOT"

# Format files in the up_client_socket/cpp directory
format_files "$TARGET_DIR"
 
