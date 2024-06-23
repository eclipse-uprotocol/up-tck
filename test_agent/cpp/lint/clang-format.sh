#!/bin/bash

TEST_AGENT="$(realpath "$(dirname "$0")/../")"
CPP_SOCKET_TRANSPORT="$TEST_AGENT/../../../up-tck/up_client_socket/cpp"

format_files() {
    local dir=$1
    echo "Running clang-format on all files in '$dir'"
    pushd "$dir" > /dev/null
    shopt -s globstar
    for f in **/*.h **/*.cpp; do
        echo
        echo "Checking file '$f'"
        clang-format-12 -i "$f"
    done
    popd > /dev/null
}

# Format files in the original TEST_AGENT directory
format_files "$TEST_AGENT"

# Format files in the up_client_socket/cpp directory
format_files "$CPP_SOCKET_TRANSPORT"
 
