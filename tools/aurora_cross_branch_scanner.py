
#!/usr/bin/env python3
"""
🔍 Aurora Cross-Branch Scanner
Scans staged/unstaged changes across ALL branches by checking out each one
"""

import json
import subprocess
import sys
from pathlib import Path


def run_git(cmd: list[str]) -> tuple[int, str, str]:
    """Execute git command and return (returncode, stdout, stderr)"""
    result = subprocess.run(
        ["git"] + cmd,
        capture_output=True,
        text=True,
        cwd="."
    )
    return result.returncode, result.stdout, result.stderr


def get_current_branch() -> str:
    """Get current branch name"""
    code, out, _ = run_git(["branch", "--show-current"])
    return out.strip() if code == 0 else "unknown"


def get_all_branches() -> list[str]:
    """Get list of all local branches"""
    code, out, _ = run_git(["branch", "--format=%(refname:short)"])
    if code != 0:
        return []
    return [b.strip() for b in out.strip().split("\n") if b.strip()]


def scan_branch_status(branch: str) -> dict:
    """Scan staged/unstaged changes for a specific branch"""
    # Checkout the branch
    code, _, err = run_git(["checkout", branch])
    if code != 0:
        return {"branch": branch, "error": f"Failed to checkout: {err}"}
    
    # Get staged files
    code, staged_out, _ = run_git(["diff", "--cached", "--name-status"])
    staged_files = []
    if code == 0 and staged_out.strip():
        for line in staged_out.strip().split("\n"):
            parts = line.split("\t")
            if len(parts) >= 2:
                staged_files.append({
                    "status": parts[0],
                    "file": parts[1]
                })
    
    # Get unstaged files
    code, unstaged_out, _ = run_git(["diff", "--name-status"])
    unstaged_files = []
    if code == 0 and unstaged_out.strip():
        for line in unstaged_out.strip().split("\n"):
            parts = line.split("\t")
            if len(parts) >= 2:
                unstaged_files.append({
                    "status": parts[0],
                    "file": parts[1]
                })
    
    # Get untracked files
    code, untracked_out, _ = run_git(["ls-files", "--others", "--exclude-standard"])
    untracked_files = []
    if code == 0 and untracked_out.strip():
        untracked_files = [f.strip() for f in untracked_out.strip().split("\n")]
    
    return {
        "branch": branch,
        "staged": staged_files,
        "unstaged": unstaged_files,
        "untracked": untracked_files,
        "has_changes": bool(staged_files or unstaged_files or untracked_files)
    }


def main():
    print("🔍 Aurora Cross-Branch Scanner")
    print("=" * 60)
    
    # Save current branch to restore later
    original_branch = get_current_branch()
    print(f"📍 Original branch: {original_branch}\n")
    
    # Get all branches
    branches = get_all_branches()
    if not branches:
        print("❌ No branches found!")
        return 1
    
    print(f"Found {len(branches)} branches to scan\n")
    
    # Scan each branch
    results = []
    for branch in branches:
        print(f"Scanning {branch}...", end=" ")
        result = scan_branch_status(branch)
        results.append(result)
        
        if result.get("error"):
            print(f"❌ {result['error']}")
        elif result["has_changes"]:
            print(f"⚠️  Has changes!")
        else:
            print("✅ Clean")
    
    # Restore original branch
    print(f"\n📍 Restoring original branch: {original_branch}")
    run_git(["checkout", original_branch])
    
    # Save results
    output_file = Path("AURORA_CROSS_BRANCH_SCAN.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Scan complete! Results saved to {output_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    branches_with_changes = [r for r in results if r.get("has_changes")]
    if branches_with_changes:
        print(f"\n⚠️  {len(branches_with_changes)} branches have uncommitted changes:\n")
        for result in branches_with_changes:
            print(f"  • {result['branch']}:")
            if result.get("staged"):
                print(f"    - {len(result['staged'])} staged files")
            if result.get("unstaged"):
                print(f"    - {len(result['unstaged'])} unstaged files")
            if result.get("untracked"):
                print(f"    - {len(result['untracked'])} untracked files")
    else:
        print("\n✅ All branches are clean (no uncommitted changes)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
