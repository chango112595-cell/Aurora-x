# aurora_nexus_v3/autonomy/prod_autonomy.py
"""
Production Autonomy Adapter — ETCD + Container Sandbox Wiring
This file wires AutonomyManager to etcd_store and sandbox_runner so
the entire generate -> inspect -> sandbox-test -> promote flow uses:
  - etcd_store.get_registry / put_registry_atomic / acquire_lock
  - sandbox_runner.run_module_candidate for strong isolation
It expects etcd_store.py and sandbox_runner.py under aurora_nexus_v3/autonomy/
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from aurora_nexus_v3.autonomy import etcd_store, sandbox_runner
from aurora_nexus_v3.autonomy.manager import AutonomyManager, Incident, RepairResult

# Config
REPO_ROOT = Path.cwd()
MODULES_DIR = REPO_ROOT / "aurora_nexus_v3" / "modules"
REGISTRY_KEY = "/aurora/modules_registry"  # etcd key used by adapter
GENERATED_STAGE = REPO_ROOT / "aurora_nexus_v3" / "generated_candidates"
AUDIT_LOG = REPO_ROOT / "aurora_nexus_v3" / "autonomy_audit.log"
APPROVALS_DIR = REPO_ROOT / "aurora_nexus_v3" / "autonomy_approvals"
GENERATOR_CLI = [sys.executable, str(REPO_ROOT / "tools" / "generate_modules.py")]
SANDBOX_TIMEOUT_SEC = int(os.environ.get("SANDBOX_TIMEOUT_SEC", "15"))
SANDBOX_CPUS = float(os.environ.get("SANDBOX_CPUS", "0.5"))
SANDBOX_MEM_MB = int(os.environ.get("SANDBOX_MEM_MB", "256"))
SANDBOX_WORKERS = int(os.environ.get("SANDBOX_WORKERS", "6"))

# Logging
logger = logging.getLogger("prod_autonomy")
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(h)
logger.setLevel(logging.INFO)

# Ensure dirs
GENERATED_STAGE.mkdir(parents=True, exist_ok=True)
APPROVALS_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)


# Simple audit write
def audit_log(entry: dict[str, Any]) -> None:
    record = {"ts": datetime.utcnow().isoformat() + "Z", **entry}
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    logger.info("AUDIT: %s", record.get("action"))


# -- Registry helpers using etcd_store --
def read_registry() -> dict:
    # try etcd first, fallback to file
    try:
        reg = etcd_store.get_registry()
        return reg
    except Exception:
        logger.exception("etcd_store.get_registry failed; fallback to file")
        fallback = REPO_ROOT / "aurora_nexus_v3" / "modules_registry.json"
        if fallback.exists():
            return json.loads(fallback.read_text(encoding="utf-8"))
        return {}


def atomic_registry_update(updater_func):
    """
    Use etcd_store.put_registry_atomic to perform atomic updates.
    """
    ok, new = etcd_store.put_registry_atomic(updater_func)
    if not ok:
        raise RuntimeError("atomic registry update failed")
    return new


# -- Generator adapter (prefer callable, fallback to CLI) --
def generator_adapter(manifest_entry: dict[str, Any]) -> str:
    candidate_id = f"{manifest_entry.get('id')}_{uuid.uuid4().hex[:8]}"
    candidate_dir = GENERATED_STAGE / candidate_id
    candidate_dir.mkdir(parents=True, exist_ok=True)
    # Prefer importable generator
    try:
        import importlib

        gen_mod = None
        try:
            gen_mod = importlib.import_module("tools.generate_modules")
        except Exception:
            gen_mod = None
        if gen_mod and hasattr(gen_mod, "generate_module_files"):
            temp_manifest = candidate_dir / "modules.manifest.json"
            temp_manifest.write_text(
                json.dumps({"modules": [manifest_entry]}, indent=2), encoding="utf-8"
            )
            gen_mod.generate_module_files(
                temp_manifest,
                candidate_dir / "modules",
                dry_run=False,
                force=True,
                update_init=False,
            )
            audit_log(
                {
                    "action": "generate_api",
                    "module_id": manifest_entry.get("id"),
                    "candidate": str(candidate_dir),
                }
            )
            return str(candidate_dir)
    except Exception:
        logger.exception("Generator API path failed; falling back to CLI")

    # CLI fallback
    try:
        temp_manifest = candidate_dir / "modules.manifest.json"
        temp_manifest.write_text(
            json.dumps({"modules": [manifest_entry]}, indent=2), encoding="utf-8"
        )
        cmd = GENERATOR_CLI + [
            "--manifest",
            str(temp_manifest),
            "--out",
            str(candidate_dir / "modules"),
            "--force",
        ]
        logger.info("Running generator CLI: %s", " ".join(cmd))
        subprocess.check_call(cmd, cwd=str(REPO_ROOT))
        audit_log(
            {
                "action": "generate_cli",
                "module_id": manifest_entry.get("id"),
                "candidate": str(candidate_dir),
            }
        )
        return str(candidate_dir)
    except subprocess.CalledProcessError as e:
        logger.exception("Generator CLI failed: %s", e)
        raise


# -- Inspector adapter (AST + compile checks) --
def inspector_adapter(candidate_path: str) -> dict[str, Any]:
    import ast

    p = Path(candidate_path)
    modules_subdir = p / "modules"
    if not modules_subdir.exists():
        return {"ok": False, "issues": ["modules subdir missing"]}
    issues = []
    files_checked = 0
    for py in modules_subdir.rglob("*.py"):
        try:
            source = py.read_text(encoding="utf-8")
            ast.parse(source)
            compile(source, str(py), "exec")
            files_checked += 1
        except SyntaxError as se:
            issues.append(f"SyntaxError in {py}: {se}")
        except Exception as e:
            issues.append(f"Static-check failed for {py}: {type(e).__name__}: {e}")
    found_init = any(str(x).endswith("_init.py") for x in modules_subdir.rglob("*"))
    found_exec = any(str(x).endswith("_execute.py") for x in modules_subdir.rglob("*"))
    found_cleanup = any(str(x).endswith("_cleanup.py") for x in modules_subdir.rglob("*"))
    if not (found_init and found_exec and found_cleanup):
        issues.append("Missing one of init/execute/cleanup files in candidate")
    ok = len(issues) == 0
    audit_log(
        {
            "action": "inspect",
            "candidate": str(candidate_path),
            "ok": ok,
            "issue_count": len(issues),
        }
    )
    return {"ok": ok, "issues": issues, "files_checked": files_checked}


# -- Tester adapter: use sandbox_runner.run_module_candidate for strong isolation --
def tester_adapter(
    candidate_path: str, manifest_entry: dict[str, Any], test_inputs: list[dict[str, Any]]
) -> dict[str, Any]:
    modules_dir = Path(candidate_path) / "modules"
    if not modules_dir.exists():
        return {"ok": False, "error": "modules_dir_missing"}
    exec_files = list(modules_dir.rglob("*_execute.py"))
    if not exec_files:
        return {"ok": False, "error": "no_execute_files_found"}
    exec_rel = str(exec_files[0].relative_to(modules_dir))
    results = []
    ok_all = True
    for inp in test_inputs:
        # pass input as JSON string to wrapper
        inp_json = json.dumps(inp)
        resource_limits = {"mem_mb": SANDBOX_MEM_MB, "cpus": SANDBOX_CPUS}
        res = sandbox_runner.run_module_candidate(
            Path(candidate_path), exec_rel, inp_json, resource_limits, timeout_s=SANDBOX_TIMEOUT_SEC
        )
        results.append(res)
        if not res.get("ok"):
            ok_all = False
            break
    audit_log(
        {
            "action": "sandbox_test",
            "candidate": str(candidate_path),
            "ok": ok_all,
            "tests_run": len(results),
        }
    )
    return {"ok": ok_all, "results": results}


# -- Snapshot & restore using git but coordinated with etcd locks --
def snapshot_adapter(module_id: str) -> str | None:
    try:
        # safe git commit of module files
        # stage files referenced in registry
        reg = read_registry()
        modules_meta = reg.get("modules", {})
        meta = modules_meta.get(module_id) or {}
        files = meta.get("files", [])
        if not files:
            subprocess.check_call(["git", "add", str(MODULES_DIR)], cwd=str(REPO_ROOT))
        else:
            for rel in files:
                abs_path = (MODULES_DIR / rel).resolve()
                if abs_path.exists():
                    subprocess.check_call(["git", "add", str(abs_path)], cwd=str(REPO_ROOT))
        msg = f"autonomy snapshot {module_id} at {datetime.utcnow().isoformat()}Z"
        subprocess.check_call(["git", "commit", "-m", msg], cwd=str(REPO_ROOT))
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT))
        commit = out.decode().strip()
        audit_log({"action": "snapshot", "module_id": module_id, "commit": commit})
        return commit
    except subprocess.CalledProcessError:
        try:
            out = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT))
            commit = out.decode().strip()
            return commit
        except Exception:
            logger.exception("Snapshot failed")
            return None


def restore_snapshot_adapter(commit_hash: str) -> dict[str, Any]:
    try:
        subprocess.check_call(["git", "reset", "--hard", commit_hash], cwd=str(REPO_ROOT))
        audit_log({"action": "restore_snapshot", "commit": commit_hash})
        return {"ok": True}
    except subprocess.CalledProcessError:
        logger.exception("Restore snapshot failed for %s", commit_hash)
        return {"ok": False, "error": "git_reset_failed"}


# -- Sign artifact (SHA256) --
def sign_adapter(path_like: str, metadata: dict[str, Any]) -> str:
    import hashlib

    h = hashlib.sha256()
    p = Path(path_like)
    if p.is_file():
        h.update(p.read_bytes())
    else:
        for f in sorted([x for x in p.rglob("*") if x.is_file()]):
            rel = str(f.relative_to(p)).encode("utf-8")
            h.update(rel)
            h.update(f.read_bytes())
    sig = h.hexdigest()
    audit_log({"action": "sign", "path": str(path_like), "signature": sig})
    return sig


# -- Promote adapter: with etcd lock to avoid races --
def promote_adapter(candidate_path: str, manifest_entry: dict[str, Any]) -> dict[str, Any]:
    module_id = str(manifest_entry.get("id"))
    lock_name = f"promote-{module_id}"
    try:
        with etcd_store.acquire_lock(lock_name, ttl=60):
            cand = Path(candidate_path)
            modules_sub = cand / "modules"
            if not modules_sub.exists():
                return {"ok": False, "error": "candidate_modules_missing"}
            category = manifest_entry.get("category", "processor")
            target_dir = MODULES_DIR / category
            target_dir.mkdir(parents=True, exist_ok=True)
            moved = []
            for f in modules_sub.iterdir():
                dest = target_dir / f.name
                if dest.exists():
                    bak = target_dir / f"{f.name}.bak.{int(time.time())}"
                    shutil.move(str(dest), str(bak))
                # atomic move
                os.replace(str(f), str(dest))
                moved.append(str(dest.relative_to(MODULES_DIR)))

            # update registry using etcd atomic patch
            def updater(curr):
                if "modules" not in curr:
                    curr["modules"] = {}
                curr["modules"][module_id] = {
                    "id": module_id,
                    "name": manifest_entry.get("name"),
                    "category": category,
                    "files": moved,
                    "manifest": manifest_entry,
                }
                return curr

            atomic_registry_update(updater)
            signature = sign_adapter(str(target_dir), {"module_id": module_id})
            artifact = {
                "module_id": module_id,
                "files": moved,
                "signature": signature,
                "promoted_at": datetime.utcnow().isoformat() + "Z",
            }
            audit_log({"action": "promote", "module_id": module_id, "artifact": artifact})
            return {"ok": True, "artifact": artifact}
    except Exception as e:
        logger.exception("Promotion failed: %s", e)
        return {"ok": False, "error": "promotion_exception", "details": str(e)}


# -- Notify human (approval file + optional webhook) --
def notify_adapter(payload: dict[str, Any]) -> str:
    corr = uuid.uuid4().hex
    out = APPROVALS_DIR / f"approval_{corr}.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    audit_log(
        {
            "action": "notify_human",
            "correlation": corr,
            "summary": payload.get("incident", {}).get("module_id"),
        }
    )
    # Optionally send webhook: env AUTONOMY_WEBHOOK_URL
    return corr


# -- Wire into AutonomyManager and provide run helper --
def build_prod_autonomy_manager(
    autonomy_level: str = "balanced",
    hybrid_mode: bool = True,
    protected_scopes: list[str] | None = None,
) -> AutonomyManager:
    reg = read_registry()
    manifest_registry = {}
    modules = reg.get("modules", {}) or {}
    for mid, meta in modules.items():
        manifest_registry[mid] = meta.get("manifest") or meta
    mgr = AutonomyManager(
        manifest_registry=manifest_registry,
        autonomy_level=autonomy_level,
        hybrid_mode=hybrid_mode,
        protected_scopes=protected_scopes or [],
        generator_func=generator_adapter,
        inspector_func=inspector_adapter,
        sandbox_tester=tester_adapter,
        promote_func=promote_adapter,
        snapshot_func=snapshot_adapter,
        restore_snapshot=restore_snapshot_adapter,
        notify_human=notify_adapter,
        sign_artifact=sign_adapter,
        max_repair_attempts=int(os.environ.get("AUTONOMY_MAX_ATTEMPTS", "3")),
        worker_pool=SANDBOX_WORKERS,
    )
    logger.info("Built prod AutonomyManager (level=%s hybrid=%s)", autonomy_level, hybrid_mode)
    return mgr


def handle_incident_and_return(
    incident_payload: dict[str, Any], autonomy_level: str = "balanced"
) -> dict[str, Any]:
    mgr = build_prod_autonomy_manager(autonomy_level=autonomy_level)
    incident = Incident(
        module_id=incident_payload.get("module_id", "unknown"),
        error=incident_payload.get("error", ""),
        stacktrace=incident_payload.get("stacktrace", ""),
        metrics=incident_payload.get("metrics", {}),
        extra=incident_payload.get("extra", {}),
    )
    res: RepairResult = mgr.handle_incident(incident)
    audit_log(
        {"action": "incident_handled", "module_id": incident.module_id, "result": res.__dict__}
    )
    return {
        "success": res.success,
        "promoted": res.promoted,
        "attempts": res.attempts,
        "details": res.details,
    }


if __name__ == "__main__":
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except Exception:
        print("Provide JSON incident on stdin", file=sys.stderr)
        sys.exit(2)
    out = handle_incident_and_return(
        payload, autonomy_level=payload.get("autonomy_level", "balanced")
    )
    print(json.dumps(out, indent=2))
