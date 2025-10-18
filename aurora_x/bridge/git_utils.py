from __future__ import annotations

import os
import shlex
import subprocess


def run(cmd: str):
    return subprocess.run(shlex.split(cmd), capture_output=True, text=True)
def ensure_remote():
    url = os.getenv("AURORA_GIT_URL","").strip()
    if not url: return False
    run("git config user.email 'aurora@local'")
    run("git config user.name 'Aurora Bridge'")
    r = run("git remote get-url origin")
    if r.returncode != 0 or (r.stdout.strip() and r.stdout.strip()!=url):
        run("git remote remove origin")
        run(f"git remote add origin {url}")
    return True
def push(branch: str='main'):
    ensure_remote()
    run("git add -A")
    run('git commit -m "chore(bridge): sync"')
    run(f"git push origin {branch}")
