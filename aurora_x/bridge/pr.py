from __future__ import annotations
import os, json, subprocess, shlex, time, zipfile, pathlib, urllib.request

# Module-level flag for GPG import caching
_GPG_KEY_IMPORTED = False

def _run(cmd: str, cwd: str | None = None):
    return subprocess.run(shlex.split(cmd), cwd=cwd, capture_output=True, text=True)

def _check_gpg_available():
    """Check if GPG binary is available in the system"""
    try:
        result = subprocess.run(['gpg', '--version'], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return False

def _get_git_config(key: str):
    """Get current git config value, returns None if not set"""
    result = _run(f'git config --get {key}')
    return result.stdout.strip() if result.returncode == 0 else None

def _git(cfg: dict[str,str] | None = None):
    global _GPG_KEY_IMPORTED
    
    # Save original git config values
    original_config = {
        'user.email': _get_git_config('user.email'),
        'user.name': _get_git_config('user.name'),
        'commit.gpgsign': _get_git_config('commit.gpgsign'),
        'gpg.program': _get_git_config('gpg.program'),
        'user.signingkey': _get_git_config('user.signingkey')
    }
    
    try:
        # base identity
        email = os.getenv("AURORA_GIT_EMAIL", "aurora@local")
        name  = os.getenv("AURORA_GIT_NAME",  "Aurora Bridge")
        _run(f'git config user.email {shlex.quote(email)}')
        _run(f'git config user.name {shlex.quote(name)}')
        
        # optional signing (with graceful fallback)
        if os.getenv("AURORA_SIGN","0").lower() in ("1","true","yes","on"):
            key_id = os.getenv("GPG_KEY_ID","").strip()
            armored = os.getenv("GPG_PRIVATE_ASC","").strip()
            
            # Only configure signing if GPG is available AND keys are provided
            if armored and key_id and _check_gpg_available():
                try:
                    # Import key only once per runtime (caching)
                    if not _GPG_KEY_IMPORTED:
                        p = subprocess.run(['gpg', '--batch', '--import'], 
                                         input=armored, capture_output=True, text=True, timeout=10)
                        if p.returncode == 0:
                            _GPG_KEY_IMPORTED = True
                        else:
                            print(f"Warning: GPG key import failed: {p.stderr}")
                    
                    # Verify key exists
                    verify = _run(f"gpg --batch --list-secret-keys {shlex.quote(key_id)}")
                    if verify.returncode == 0:
                        # Configure git for signing
                        _run('git config commit.gpgsign true')
                        _run('git config gpg.program gpg')
                        _run(f'git config user.signingkey {shlex.quote(key_id)}')
                    else:
                        print(f"Warning: GPG signing key not found, continuing without signing")
                        _run('git config commit.gpgsign false')
                        
                except (subprocess.SubprocessError, FileNotFoundError, OSError) as e:
                    # Graceful fallback - continue without signing
                    print(f"Warning: GPG signing setup failed ({e}), continuing without signing")
                    _run('git config commit.gpgsign false')
            else:
                # GPG not available or keys not provided - continue without signing
                if not _check_gpg_available():
                    print("Warning: GPG not available, continuing without signing")
                elif not (armored and key_id):
                    print("Warning: GPG keys not provided, continuing without signing")
                _run('git config commit.gpgsign false')
        
        return original_config
        
    except Exception as e:
        # If anything goes wrong, try to restore original config
        _restore_git_config(original_config)
        raise

def _restore_git_config(original_config: dict):
    """Restore original git config values"""
    for key, value in original_config.items():
        if value is not None:
            _run(f'git config {key} {shlex.quote(value)}')
        else:
            # Unset config if it wasn't previously set
            _run(f'git config --unset {key}')

def _ensure_remote(url: str):
    _run("git rev-parse --is-inside-work-tree")
    _run("git remote remove origin")
    _run(f"git remote add origin {url}")

def _github_api(path: str, method="GET", payload: dict | None = None):
    tok = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or os.getenv("AURORA_GH_TOKEN")
    if not tok:
        return {"ok": False, "err": "missing token"}
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        data=(json.dumps(payload).encode() if payload else None),
        method=method,
        headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json", "User-Agent": "Aurora-Bridge"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"ok": False, "err": str(e)}

def _extract_zip_into_cwd(zip_rel: str | None):
    if not zip_rel:
        return False
    zpath = pathlib.Path(".") / zip_rel.lstrip("/")
    if not zpath.exists():
        # fallback: newest runs/*/project.zip
        candidates = sorted(pathlib.Path("runs").glob("*/project.zip"))
        if not candidates: return False
        zpath = candidates[-1]
    with zipfile.ZipFile(zpath, "r") as z:
        z.extractall(".")
    return True

def pr_create(owner: str, name: str, base: str, title: str, body: str, zip_rel: str | None):
    if not (owner and name):
        return {"ok": False, "err": "missing owner/name"}
    repo_https = os.getenv("AURORA_GIT_URL") or f"https://github.com/{owner}/{name}.git"

    # Apply git config and save original values
    original_config = _git({})
    
    try:
        _ensure_remote(repo_https)
        _run("git fetch origin --prune")
        ts = time.strftime("%Y%m%d-%H%M%S")
        branch = f"aurora/{ts}"
        _run(f"git checkout -B {branch}")

        _extract_zip_into_cwd(zip_rel)
        _run("git add -A")
        
        # Commit with graceful fallback for signing failures
        commit_result = _run('git commit -m "feat(auto): Aurora UCSE generated project"')
        if commit_result.returncode != 0 and "gpg" in commit_result.stderr.lower():
            # If commit failed due to GPG issues, retry without signing
            print("Warning: GPG signing failed, retrying without signing")
            _run('git config commit.gpgsign false')
            commit_result = _run('git commit -m "feat(auto): Aurora UCSE generated project"')
        
        if commit_result.returncode != 0:
            raise Exception(f"Git commit failed: {commit_result.stderr}")
        
        _run(f"git push -u origin {branch}")

        api = _github_api(f"/repos/{owner}/{name}/pulls", method="POST",
                          payload={"title": title, "head": branch, "base": base, "body": body, "maintainer_can_modify": True, "draft": False})
        
        return {"ok": True, "branch": branch, "pr": api}
    
    finally:
        # Always restore original git config
        _restore_git_config(original_config)