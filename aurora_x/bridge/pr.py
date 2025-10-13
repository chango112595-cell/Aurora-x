"""
GitHub Pull Request creation module for Aurora Bridge.
Handles automated PR creation with optional GPG signing support.
"""
from __future__ import annotations
import os
import json
import subprocess
import shlex
import time
import zipfile
import pathlib
import urllib.request
from contextlib import contextmanager

# Module-level cache for GPG key import status
_GPG_KEY_IMPORTED = False

def _run(cmd: str, cwd: str | None = None):
    """Execute a shell command and return the result."""
    return subprocess.run(shlex.split(cmd), cwd=cwd, capture_output=True, text=True)

def _get_git_config(key: str) -> str | None:
    """Get the current value of a git config key."""
    result = _run(f"git config --get {key}")
    return result.stdout.strip() if result.returncode == 0 else None

def _import_gpg_key_once(key_id: str, armored: str) -> bool:
    """Import GPG key only once per runtime, with caching."""
    global _GPG_KEY_IMPORTED
    
    if _GPG_KEY_IMPORTED:
        return True
    
    try:
        # Check if GPG is available
        check_result = subprocess.run(
            ['gpg', '--version'], 
            capture_output=True, 
            text=True,
            timeout=5
        )
        if check_result.returncode != 0:
            return False
        
        # Import the key
        import_result = subprocess.run(
            ['gpg', '--batch', '--import'],
            input=armored,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if import_result.returncode == 0:
            # Verify the key was imported
            verify_result = _run(f"gpg --batch --list-secret-keys {shlex.quote(key_id)}")
            if verify_result.returncode == 0:
                _GPG_KEY_IMPORTED = True
                return True
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        # GPG not available or operation failed
        pass
    
    return False

@contextmanager
def _temporary_git_config(configs: dict[str, str | None]):
    """
    Context manager to temporarily set git config values and restore them afterwards.
    
    Args:
        configs: Dictionary of config keys to temporary values
    """
    # Save original values
    original_values = {}
    for key in configs:
        original_values[key] = _get_git_config(key)
    
    try:
        # Set temporary values
        for key, value in configs.items():
            if value is not None:
                _run(f"git config {key} {shlex.quote(str(value))}")
            else:
                # Unset the config if value is None
                _run(f"git config --unset {key}")
        
        yield
    finally:
        # Restore original values
        for key, original_value in original_values.items():
            if original_value is not None:
                _run(f"git config {key} {shlex.quote(original_value)}")
            else:
                # The key didn't exist before, so remove it
                _run(f"git config --unset {key}")

def _setup_git_identity():
    """Set up git identity for commits."""
    email = os.getenv("AURORA_GIT_EMAIL", "aurora@local")
    name = os.getenv("AURORA_GIT_NAME", "Aurora Bridge")
    _run(f'git config user.email {shlex.quote(email)}')
    _run(f'git config user.name {shlex.quote(name)}')

def _ensure_remote(url: str):
    """Ensure git remote is configured."""
    # Check if we're in a git repo
    result = _run("git rev-parse --is-inside-work-tree")
    if result.returncode != 0:
        # Initialize git repo if not exists
        _run("git init")
    
    # Remove and re-add origin
    _run("git remote remove origin")
    _run(f"git remote add origin {url}")

def _github_api(path: str, method="GET", payload: dict | None = None):
    """Make a request to the GitHub API."""
    tok = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or os.getenv("AURORA_GH_TOKEN")
    if not tok:
        return {"ok": False, "err": "No GitHub token found. Please set GITHUB_TOKEN, GH_TOKEN, or AURORA_GH_TOKEN environment variable"}
    
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        data=(json.dumps(payload).encode() if payload else None),
        method=method,
        headers={
            "Authorization": f"Bearer {tok}", 
            "Accept": "application/vnd.github+json", 
            "User-Agent": "Aurora-Bridge"
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            error_data = json.loads(error_body)
            return {"ok": False, "err": error_data.get("message", str(e))}
        except:
            return {"ok": False, "err": str(e)}
    except Exception as e:
        return {"ok": False, "err": str(e)}

def _extract_zip_into_cwd(zip_rel: str | None):
    """Extract ZIP file contents into current working directory."""
    if not zip_rel:
        return False
    
    # Handle API path format
    if zip_rel.startswith("/api/runs/"):
        # Extract the run timestamp and construct local path
        parts = zip_rel.split("/")
        if len(parts) >= 4:
            run_ts = parts[3]
            zpath = pathlib.Path(f"runs/run-{run_ts}/project.zip")
        else:
            zpath = pathlib.Path(".") / zip_rel.lstrip("/")
    else:
        zpath = pathlib.Path(".") / zip_rel.lstrip("/")
    
    if not zpath.exists():
        # fallback: newest runs/*/project.zip
        candidates = sorted(pathlib.Path("runs").glob("*/project.zip"))
        if not candidates: 
            return False
        zpath = candidates[-1]
    
    with zipfile.ZipFile(zpath, "r") as z:
        z.extractall(".")
    return True

def pr_create(owner: str, name: str, base: str = "main", 
              title: str = "Aurora UCSE Generated Project",
              body: str = "Automatically generated by Aurora Bridge Universal Code Synthesis Engine",
              zip_rel: str | None = None):
    """
    Create a GitHub Pull Request with generated code.
    
    Args:
        owner: Repository owner (GitHub username or organization)
        name: Repository name  
        base: Base branch to merge into (default: "main")
        title: PR title
        body: PR description
        zip_rel: Relative path to ZIP file containing generated code
        
    Returns:
        Dictionary with PR creation results
    """
    if not (owner and name):
        return {"ok": False, "err": "missing owner/name"}
    
    # Get repository URL from environment or construct from owner/name
    repo_https = os.getenv("AURORA_GIT_URL") or f"https://github.com/{owner}/{name}.git"
    
    # Set up git identity (this is always needed for commits)
    _setup_git_identity()
    
    # Set up remote
    _ensure_remote(repo_https)
    
    # Fetch latest from remote
    _run("git fetch origin --prune")
    
    # Create unique branch name with timestamp
    ts = time.strftime("%Y%m%d-%H%M%S")
    branch = f"aurora/{ts}"
    
    # Create and checkout new branch
    _run(f"git checkout -B {branch}")
    
    # Extract ZIP file if provided
    if zip_rel:
        _extract_zip_into_cwd(zip_rel)
    
    # Stage all changes
    _run("git add -A")
    
    # Check if there are changes to commit
    result = _run("git status --porcelain")
    if not result.stdout.strip():
        return {"ok": False, "err": "No changes to commit"}
    
    # Prepare commit message
    commit_msg = f"feat(auto): {title}\n\n{body}\n\nGenerated at {time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Check if we should sign commits
    should_sign = os.getenv("AURORA_SIGN", "0").lower() in ("1", "true", "yes", "on")
    commit_success = False
    
    if should_sign:
        key_id = os.getenv("GPG_KEY_ID", "").strip()
        armored = os.getenv("GPG_PRIVATE_ASC", "").strip()
        
        # Try to sign the commit if we have the necessary credentials
        if key_id and armored:
            # Import GPG key if not already imported
            gpg_available = _import_gpg_key_once(key_id, armored)
            
            if gpg_available:
                # Use temporary git config for signing
                signing_config = {
                    "commit.gpgsign": "true",
                    "gpg.program": "gpg",
                    "user.signingkey": key_id
                }
                
                try:
                    with _temporary_git_config(signing_config):
                        # Try to commit with signing
                        commit_result = _run(f'git commit -m {shlex.quote(commit_msg)}')
                        commit_success = (commit_result.returncode == 0)
                        
                        if not commit_success:
                            # Log the error but continue with fallback
                            print(f"Warning: Signed commit failed: {commit_result.stderr}")
                except Exception as e:
                    # Log the error but continue with fallback
                    print(f"Warning: Error during signed commit: {e}")
    
    # Fallback to unsigned commit if signing failed or was not requested
    if not commit_success:
        # Ensure signing is disabled for this commit
        with _temporary_git_config({"commit.gpgsign": "false"}):
            commit_result = _run(f'git commit -m {shlex.quote(commit_msg)}')
            if commit_result.returncode != 0:
                return {"ok": False, "err": f"Failed to commit: {commit_result.stderr}"}
    
    # Push branch to remote
    push_result = _run(f"git push -u origin {branch}")
    if push_result.returncode != 0:
        # Try with force if regular push fails
        push_result = _run(f"git push -u origin {branch} --force")
        if push_result.returncode != 0:
            return {"ok": False, "err": f"Failed to push branch: {push_result.stderr}"}
    
    # Create PR via GitHub API
    api_result = _github_api(
        f"/repos/{owner}/{name}/pulls", 
        method="POST",
        payload={
            "title": title, 
            "head": branch, 
            "base": base, 
            "body": body, 
            "maintainer_can_modify": True, 
            "draft": False
        }
    )
    
    if api_result.get("err"):
        return {"ok": False, "err": f"PR creation failed: {api_result.get('err')}",
                "branch": branch, "push_success": True}
    
    return {"ok": True, "branch": branch, "pr": api_result}

# Convenience function for testing
def test_connection(owner: str, name: str) -> bool:
    """Test GitHub API connection and repository access."""
    tok = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or os.getenv("AURORA_GH_TOKEN")
    if not tok:
        print("No GitHub token found")
        return False
    
    api_result = _github_api(f"/repos/{owner}/{name}")
    if api_result.get("err"):
        print(f"Connection test failed: {api_result.get('err')}")
        return False
    
    print(f"Successfully connected to {api_result.get('full_name', 'repository')}")
    return True