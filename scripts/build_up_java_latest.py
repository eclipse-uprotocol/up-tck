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
            command,
            check=True,
            shell=True,
            text=True,  # , stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("An error occurred while executing:", command)
        print(e.stderr)
        sys.exit(1)


def main():
    # Define the repository and desired branch or commit
    repo_url = "https://github.com/eclipse-uprotocol/up-java.git"

    # Directory to be removed and cloned
    repo_dir = "up-java"

    # Clone the repository
    run_command(f"git clone {repo_url}")

    # Change directory into the repository
    os.chdir(repo_dir)

    run_command("mvn clean install")


if __name__ == "__main__":
    main()
