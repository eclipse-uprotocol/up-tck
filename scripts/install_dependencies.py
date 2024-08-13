"""
SPDX-FileCopyrightText: Copyright (c) 2024 Contributors to the Eclipse Foundation
See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
SPDX-FileType: SOURCE
SPDX-License-Identifier: Apache-2.0
"""

import os
import subprocess
import sys


def run_command(command):
    """Run a shell command and handle the output."""
    try:
        result = subprocess.run(
            command, check=True, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("An error occurred while executing:", command)
        print(e.stderr)
        sys.exit(1)


def check_conan_version():
    try:
        # Check Conan version
        result = subprocess.run(["conan", "--version"], capture_output=True, text=True, check=True)
        version_str = result.stdout.strip().split()[-1]
        version_parts = version_str.split('.')
        major, minor = int(version_parts[0]), int(version_parts[1])

        # Check if version is 2.3 or greater
        if major > 2 or (major == 2 and minor >= 3):
            print(f"Conan version {version_str} is installed.")
            return True
        else:
            print(f"Conan version {version_str} is lower than the required 2.3.")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Conan is not installed.")
        return False


def main():
    # Define the repository and desired branch or commit
    repo_url = "https://github.com/eclipse-uprotocol/up-python.git"
    branch = "main"

    if not check_conan_version():
        print("Conan is not installed or version is lower than 2.3.")
        sys.exit(1)

    # Install dependencies
    run_command("pip install -r requirements.txt")

    # Directory to be removed and cloned
    repo_dir = "up-python"

    # Clone the repository
    run_command(f"git clone -b {branch} {repo_url}")

    # Change directory into the repository
    os.chdir(repo_dir)

    run_command("pip install .")

    # Change directory into the repository scripts
    os.chdir("scripts")

    # Run a script within the repository
    run_command("python pull_and_compile_protos.py")

    # Move back to the root of the repository
    os.chdir(os.pardir)

    # Install the package from the repository
    run_command("pip install .")

    os.chdir(os.pardir)  # Move back to the root of the cloned repository directory structure

    run_command(
        "python install_cpp_test_agent.py "
        "--up-core-api-version 1.6.0 "
        "--up-cpp-version 1.0.1-rc1 "
        "--up-client-socket-version 1.0.0-dev"
    )


if __name__ == "__main__":
    main()
