import os
import shutil


def clean_project():
    # Remove build/ directory
    if os.path.exists('build'):
        shutil.rmtree('build')

    # Remove dist/ directory
    if os.path.exists('dist'):
        shutil.rmtree('dist')

    # Remove *.egg-info/ directories
    egg_info_directories = [d for d in os.listdir() if d.endswith('.egg-info')]
    for egg_info_directory in egg_info_directories:
        shutil.rmtree(egg_info_directory)


if __name__ == "__main__":
    clean_project()
    print("Cleanup complete.")