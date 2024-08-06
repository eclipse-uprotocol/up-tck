import argparse
import os
import subprocess
import sys
from contextlib import contextmanager


@contextmanager
def change_directory(target_dir):
    """Context manager for changing the current working directory."""
    prev_dir = os.getcwd()
    os.chdir(target_dir)
    try:
        yield
    finally:
        os.chdir(prev_dir)


def run_command(command, cwd=None):
    """Run a shell command and handle the output."""
    try:
        result = subprocess.run(
            command, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, shell=False
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing: {e.cmd}")
        print(e.stderr)
        sys.exit(1)


def main():
    print("Installing CPP Test Agent")
    parser = argparse.ArgumentParser(description='Install C++ test agent')
    parser.add_argument('--up-core-api-version', type=str, help='Specify the version of up-core-api', required=False)
    parser.add_argument('--up-cpp-version', type=str, help='Specify the version of up-cpp', required=False)
    parser.add_argument(
        '--up-client-socket-version', type=str, help='Specify the version of up_client_socket', required=False
    )
    args = parser.parse_args()

    repo_url = "https://github.com/eclipse-uprotocol/up-conan-recipes.git"
    branch = "main"
    repo_dir = "up-conan-recipes"

    # Clone the repository
    print("Clone up-conan-recipe")
    run_command(["git", "clone", "-b", branch, repo_url])

    with change_directory(repo_dir):
        # Install up-core-api
        print("Install up-core-api")
        if args.up_core_api_version:
            run_command(
                ["conan", "create", "up-core-api/release", "--version", args.up_core_api_version, "--build=missing"]
            )

        # Install up-cpp
        print("Install up-cpp")
        if args.up_cpp_version:
            run_command(["conan", "create", "up-cpp/release/", "--version", args.up_cpp_version, "--build=missing"])

        # Install up_client_socket
        print("Install up_client_socket")
        if args.up_client_socket_version:
            run_command(
                [
                    "conan",
                    "create",
                    "up-transport-socket-cpp/developer/",
                    "--version",
                    args.up_client_socket_version,
                    "--build=missing",
                ]
            )

        with change_directory(os.path.abspath(os.path.join("..", "..", "test_agent", "cpp"))):
            # Build the CPP test agent executable
            print("Build the CPP test agent executable")
            run_command(["conan", "install", ".", "--build=missing"])
            with change_directory("build"):
                run_command(
                    [
                        "cmake",
                        "../",
                        "-DCMAKE_TOOLCHAIN_FILE=Release/generators/conan_toolchain.cmake",
                        "-DCMAKE_BUILD_TYPE=Release",
                    ]
                )
                run_command(["cmake", "--build", ".", "--", "-j"])

    print("Build and installation completed successfully.")


if __name__ == "__main__":
    main()
