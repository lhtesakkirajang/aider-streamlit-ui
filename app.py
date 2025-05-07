import subprocess

def get_most_recent_branch():
    cmd = [
        "git",
        "for-each-ref",
        "--sort=-committerdate",
        "--format=%(refname:short)",
        "refs/heads/"
    ]
    
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"Git command failed: {result.stderr.strip()}")
    
    branches = result.stdout.strip().split("\n")
    
    if not branches:
        raise ValueError("No branches found.")
    
    return branches[0]  # Most recently updated branch

# Example usage
recent_branch = get_most_recent_branch()
print(f"Most recent branch: {recent_branch}")
