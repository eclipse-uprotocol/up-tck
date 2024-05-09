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

import subprocess
import sys
import os
import shutil

def run_command(command):
    """Run a shell command and handle the output."""
    try:
        result = subprocess.run(command, check=True, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("An error occurred while executing:", command)
        print(e.stderr)
        sys.exit(1)

def main():
    # Define the repository and desired branch or commit
    REPO_URL = "https://github.com/eclipse-uprotocol/up-python.git"
    BRANCH = "main"

    # Directory to be removed and cloned
    repo_dir = "up-python"

    # Clone the repository
    run_command(f"git clone -b {BRANCH} {REPO_URL}")
    
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

    # Optionally, handle other dependencies via requirements.txt
    os.chdir(os.pardir)  # Move back to the root of the cloned repository directory structure
    run_command("pip install -r requirements.txt")

if __name__ == "__main__":
    main()
