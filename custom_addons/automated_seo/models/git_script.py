from git import Repo
from pathlib import Path

def push_changes_to_git(page_name, page_version, last_updated, user_id, user_name,
                        base_branch="main", feature_branch="feature-branch",
                        target_file_dir="/home/bacancy/PycharmProjects/Git-Project/"):
    try:
        # Initialize the repository
        repo = Repo(target_file_dir)
        origin = repo.remote(name='origin')

        # Pull the latest changes from the base branch
        repo.git.checkout(base_branch)
        origin.pull()
        print(f"Pulled latest changes from {base_branch}.")

        # Construct the target file path
        target_file = f"{page_name}_v{page_version}.php"  # Example: MyPage_v1.0.php
        target_file_path = Path(target_file_dir) / target_file

        # Ensure the target file exists
        if not target_file_path.exists():
            print(f"Target file {target_file} does not exist. Creating it now.")
            with open(target_file_path, "w") as file:
                file.write(f"<?php\n// {page_name} v{page_version} generated on {last_updated}\n")
            print(f"Created new file: {target_file_path}")

        # Stage the file for commit
        repo.index.add([str(target_file_path)])
        print(f"Staged file: {target_file_path}")

        # Format the commit message with user details and file name
        commit_message = (f"Page Update: {page_name}\n"
                          f"Version: {page_version}\n"
                          f"Last Updated: {last_updated}\n"
                          f"User ID: {user_id}\n"
                          f"User Name: {user_name}")

        # Commit changes
        commit = repo.index.commit(commit_message)
        print(f"Committed changes with message:\n{commit_message}")
        print(f"Commit ID: {commit.hexsha}")

        # Switch to feature branch or create it if it doesn't exist
        if feature_branch not in repo.heads:
            print(f"Feature branch '{feature_branch}' does not exist. Creating it.")
            repo.git.checkout(b=feature_branch)
        else:
            repo.git.checkout(feature_branch)
        print(f"Checked out to feature branch: {feature_branch}")

        # Push changes to the remote feature branch
        origin.push(refspec=f"{feature_branch}:{feature_branch}")
        print(f"Successfully pushed changes to {feature_branch}.")

        return True
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

# from git import Repo
# import os
#
# try:
#     repo = Repo('.')
#     origin = repo.remote(name='origin')
#     # status = repo.git.status()
#     # print("Status:\n", status)
#     base_branch = "git-commit-merge-branch"  # The branch you want to merge into
#     feature_branch = "git-commit"
#     add_file = ['/home/bacancy/Development/SPS/git_push.py']  # relative path from git root
#     repo.index.add(add_file)
#     commit_message = "Merge2"
#     repo.index.commit(commit_message)
#     current_branch = repo.active_branch
#     print(f"Current branch: {current_branch}")
#     tracking_branch = current_branch.tracking_branch()
#     if not tracking_branch:
#         print(f"No upstream branch set for {current_branch}, setting it now.")
#         origin.push(refspec=f"{current_branch.name}:{current_branch.name}")
#         current_branch.set_tracking_branch(origin.refs[current_branch.name])
#     else:
#         print(f"Upstream branch already set for {current_branch}.")
#     origin.push()
#     repo.git.checkout(base_branch)
#     merge_result = repo.git.merge(feature_branch)
#     print(f"Merge result:\n{merge_result}")
#     origin = repo.remote(name="origin")
#     origin.push()
#     print("Successfully pushed changes to remote repository.")
#
# except Exception as e:
#     print(f"An error occurred: {str(e)}")
