import os
import git

def get_git_root():
    curr_path = os.getcwd()
    git_repo = git.Repo(curr_path, search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")
    return git_root