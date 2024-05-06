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
