from git import Repo
from datetime import datetime

def push_changes_to_git(page_name, page_version, last_updated, user_id, base_branch="master",
                        feature_branch="feature-branch"):
    try:
        # Initialize the repository
        repo = Repo('.')
        origin = repo.remote(name='origin')

        # Detect and stage all modified, added, or deleted files
        repo.git.add('--all')
        print("All changes have been staged.")

        # Format the commit message
        commit_message = (f"Page Update: {page_name}\n"
                          f"Version: {page_version}\n"
                          f"Last Updated: {last_updated}\n"
                          f"User ID: {user_id}")

        # Commit changes
        commit = repo.index.commit(commit_message)
        print(f"Committed changes with message:\n{commit_message}")
        print(f"Commit ID: {commit.hexsha}")

        # Push changes to the feature branch
        current_branch = repo.active_branch
        print(f"Current branch: {current_branch}")

        if current_branch.name != feature_branch:
            repo.git.checkout(feature_branch)

        tracking_branch = current_branch.tracking_branch()
        if not tracking_branch:
            print(f"No upstream branch set for {current_branch}, setting it now.")
            origin.push(refspec=f"{current_branch.name}:{current_branch.name}")
            current_branch.set_tracking_branch(origin.refs[current_branch.name])
        else:
            print(f"Upstream branch already set for {current_branch}.")
        origin.push()

        # Merge feature branch into base branch
        repo.git.checkout(base_branch)
        merge_result = repo.git.merge(feature_branch)
        print(f"Merge result:\n{merge_result}")

        # Push the merged changes to the base branch
        origin.push()
        print("Successfully pushed changes to the remote repository.")
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
