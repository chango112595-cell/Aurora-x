from __future__ import annotations

import os
import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

RUNS = Path("runs")
RUNS.mkdir(exist_ok=True)


def _run(cmd: str):
    p = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def _discord(msg: str):
    url = os.getenv("DISCORD_WEBHOOK_URL")
    if not url:
        return
    try:
        import json as _json
        import urllib.request

        req = urllib.request.Request(
            url, data=_json.dumps({"content": msg}).encode("utf-8"), headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=6).read()
    except Exception:
        pass


def _git_available() -> bool:
    return Path(".git").exists()


def _git_commit_push(msg: str) -> bool:
    if not _git_available():
        return False
    _run("git add -A")
    code, _, _ = _run(f"git commit -m {shlex.quote(msg)}")
    _run("git push")
    return code == 0


@dataclass
class BridgeResult:
    ok: bool
    message: str
    run_dir: str | None = None
    files: list[str] | None = None
    zip_rel: str | None = None
    logs: list[str] | None = None
    components: dict[str, Any] | None = None
    stack: str | None = None
    repo_info: dict[str, Any] | None = None


def compile_from_nl(prompt: str) -> BridgeResult:
    from aurora_x.synthesis.universal_engine import generate_project

    res = generate_project(prompt)
    code, out, err = _run("pytest -q")
    ok = code == 0
    msg = f"bridge: NL→Project :: {prompt[:64]}"
    _git_commit_push(msg)
    _discord(("✅" if ok else "❌") + f" Aurora Bridge: {msg}")
    ts = res.manifest["ts"]
    return BridgeResult(
        ok=ok,
        message="compiled",
        run_dir=str(res.run_dir),
        files=res.manifest["files"],
        zip_rel=f"/api/runs/{ts}/project.zip",
        logs=[out, err],
    )


def compile_from_nl_project(
    prompt: str,
    repo_info: dict | None = None,
    stack: str | None = None,
    components: dict | None = None,
    skip_git_operations: bool = False,
) -> BridgeResult:
    """
    Enhanced version of compile_from_nl that accepts additional project parameters.

    Args:
        prompt: The natural language prompt describing the project
        repo_info: Repository information (owner, name, branch)
        stack: Technology stack preference (e.g., "react", "flask", "fullstack")
        components: Pre-determined component needs (ui_needed, api_needed, etc.)
        skip_git_operations: If True, skip git commit and push operations (used for PR mode)
    """
    from aurora_x.synthesis.universal_engine import generate_project

    # Build context dict with all the additional information

    # Generate project with enhanced context
    # Note: generate_project will need to be updated to accept context in a future iteration
    # For now, we'll embed the stack info in the prompt
    enhanced_prompt = prompt
    if stack:
        enhanced_prompt = f"[Stack: {stack}] {prompt}"

    res = generate_project(enhanced_prompt)

    # Run tests
    code, out, err = _run("pytest -q")
    ok = code == 0

    # Build commit message with stack info
    msg = "bridge: NL→Project"
    if stack:
        msg += f" [{stack}]"
    msg += f" :: {prompt[:64]}"

    # Only perform git operations if not in PR mode
    if not skip_git_operations:
        _git_commit_push(msg)
        _discord(("✅" if ok else "❌") + f" Aurora Bridge: {msg}")

    # Get timestamp from result
    ts = res.manifest["ts"] if hasattr(res, "manifest") and res.manifest else time.strftime("%Y%m%d-%H%M%S")

    # Return enhanced result with component info
    result = BridgeResult(
        ok=ok,
        message="compiled",
        run_dir=str(res.run_dir) if hasattr(res, "run_dir") else None,
        files=res.manifest["files"] if hasattr(res, "manifest") and res.manifest else None,
        zip_rel=f"/api/runs/{ts}/project.zip",
        logs=[out, err],
        components=components,
        stack=stack,
        repo_info=repo_info,
    )

    return result


def compile_from_spec(spec_path: str) -> BridgeResult:
    sp = Path(spec_path)
    if not sp.exists():
        return BridgeResult(False, f"spec not found: {spec_path}")
    code, out, err = _run(f"python -m aurora_x.main --spec {spec_path}")
    ok = code == 0
    msg = ("spec compiled " if ok else "spec failed ") + sp.name
    _git_commit_push("bridge: " + msg)
    _discord(("✅ " if ok else "❌ ") + "Aurora Bridge: " + msg)
    runs = sorted([p for p in RUNS.glob("run-*") if p.is_dir()])
    latest = str(runs[-1]) if runs else None
    return BridgeResult(
        ok=ok,
        message="spec-compiled" if ok else "spec-failed",
        run_dir=latest,
        files=None,
        zip_rel=None,
        logs=[out, err],
    )


def deploy_replit_ping() -> bool:
    url = os.getenv("BRIDGE_REPLIT_PING")
    if not url:
        return False
    try:
        import urllib.request

        urllib.request.urlopen(url, timeout=6).read()
        _discord("🔁 Replit ping triggered")
        return True
    except Exception:
        _discord("⚠️ Replit ping failed")
        return False
