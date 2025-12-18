#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Paths
MANIFESTS_DIR="$ROOT/manifests"
INSTALLER_DIR="$ROOT/installer"
SCRIPTS_DIR="$ROOT/scripts"
PACKS_SCRIPT="$SCRIPTS_DIR/create_packs_structure.sh"
NODE_WRAPPER="$INSTALLER_DIR/node_wrapper.js"
PY_INSTALLER="$INSTALLER_DIR/aurora_installer.py"
README="$ROOT/README_INSTALLER.md"

mkdir -p "$MANIFESTS_DIR" "$INSTALLER_DIR" "$SCRIPTS_DIR"

# 1) manifests/manifest_schema.yaml
cat > "$MANIFESTS_DIR/manifest_schema.yaml" <<'YAML'
# manifests/manifest_schema.yaml
# Hybrid manifest schema for PACKs and artifacts.
# Supports YAML or JSON representation (tools auto-detect).
schema_version: "aurora-manifest-v1"
pack:
  id: string               # pack01_unified_process
  name: string             # Human-friendly name
  version: string          # semver
  description: string
  entrypoint:
    install: string        # relative path to install.sh or CLI
    start: string
    stop: string
    health: string
  dependencies:
    - pack_id: string
      version_constraint: string
  artifacts:
    - path: string         # files to include in .axf or tarball
      sha256: string
  env:
    required:
      - name: string
        type: string
        default: any
  autoscan:
    manifest_preference: ["yaml","json"]   # preferred order
    auto_detect_device: true              # whether to let installer pick mode
  safety:
    dry_run_supported: true
    operator_approval_required: true
    health_check_timeout_seconds: 30
YAML

# 2) manifests/pack01_manifest.yaml (example)
cat > "$MANIFESTS_DIR/pack01_manifest.yaml" <<'YAML'
# manifests/pack01_manifest.yaml
schema_version: "aurora-manifest-v1"
pack:
  id: "pack01_unified_process"
  name: "Unified Process Core"
  version: "1.0.0"
  description: "Aurora core orchestrator and service loader"
  entrypoint:
    install: "install.sh"
    start: "start.sh"
    stop: "stop.sh"
    health: "health_check.sh"
  dependencies: []
  artifacts:
    - path: "aurora_core.py"
      sha256: ""   # populate after build
  env:
    required: []
  autoscan:
    manifest_preference: ["yaml","json"]
    auto_detect_device: true
  safety:
    dry_run_supported: true
    operator_approval_required: true
    health_check_timeout_seconds: 20
YAML

# 3) installer/aurora_installer.py (Python core)
cat > "$PY_INSTALLER" <<'PY'
#!/usr/bin/env python3
"""
installer/aurora_installer.py - Universal Aurora Installer CORE (Python).
Hybrid manifest support (yaml/json), auto-detects best installer mode per device,
supports --dry-run, --install, --staging, --activate, --rollback, and operator approval gating.

Usage:
  python3 installer/aurora_installer.py --help
"""
import argparse, os, sys, platform, subprocess, shutil, json, time
from pathlib import Path

try:
    import yaml
except Exception:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
PACKS_DIR = ROOT.parent / "packs"
STAGING_DIR = ROOT.parent / "staging"
LIVE_DIR = ROOT.parent / "live"
BACKUPS_DIR = ROOT.parent / "backups"
AUDIT_DIR = ROOT.parent / "audit"

for d in (STAGING_DIR, LIVE_DIR, BACKUPS_DIR, AUDIT_DIR):
    d.mkdir(parents=True, exist_ok=True)

def load_manifest(path: Path):
    if not path.exists():
        raise FileNotFoundError(path)
    text = path.read_text()
    if path.suffix.lower() in (".yaml", ".yml") and yaml:
        return yaml.safe_load(text)
    try:
        return json.loads(text)
    except Exception:
        if yaml:
            return yaml.safe_load(text)
        raise

def detect_environment():
    info = {
        "platform": platform.system().lower(),
        "machine": platform.machine(),
        "python": platform.python_version()
    }
    try:
        with open("/proc/cpuinfo","r") as f:
            cpu = f.read().lower()
            if "raspberry pi" in cpu or "bcm" in cpu:
                info["device"] = "raspberrypi"
            elif "nvidia" in cpu:
                info["device"] = "jetson"
    except Exception:
        pass
    return info

def best_install_mode(env_info):
    if shutil.which("python3") or shutil.which("python"):
        return "python"
    if shutil.which("node"):
        return "node"
    if env_info.get("platform") == "windows":
        return "windows"
    return "generic"

def run_health_check(pack_live_path: Path, timeout: int=30):
    hc = pack_live_path / "health_check.sh"
    if hc.exists():
        proc = subprocess.run(["bash", str(hc)], capture_output=True, text=True)
        ok = proc.returncode == 0
        out = proc.stdout + proc.stderr
        return ok, out
    return True, "no health_check present"

def stage_pack(pack_dir: Path):
    assert pack_dir.exists()
    name = pack_dir.name
    staging_target = STAGING_DIR / name
    if staging_target.exists():
        shutil.rmtree(staging_target)
    shutil.copytree(pack_dir, staging_target)
    return staging_target

def activate_pack(staging_target: Path):
    name = staging_target.name
    live_target = LIVE_DIR / name
    timestamp = str(int(time.time()))
    backup_target = BACKUPS_DIR / name / timestamp
    if live_target.exists():
        backup_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(live_target), str(backup_target))
    shutil.move(str(staging_target), str(live_target))
    return live_target, backup_target

def deploy_pack(pack_id: str, dry_run=True, auto_approve=False):
    pack_path = PACKS_DIR / pack_id
    if not pack_path.exists():
        raise FileNotFoundError(f"pack not found: {pack_path}")
    print(f"[installer] Staging {pack_id} -> staging")
    staged = stage_pack(pack_path)
    print("[installer] Running pre-activation tests (dry-run)")
    install_sh = staged / "install.sh"
    if install_sh.exists():
        p = subprocess.run(["bash", str(install_sh), "--dry-run"], capture_output=True, text=True)
        print("[installer] install.sh output:", p.stdout, p.stderr)
        if p.returncode != 0:
            print("[installer] Preinstall tests failed; aborting")
            return False
    if dry_run:
        print("[installer] Dry run complete. To activate run with --install")
        return True
    if not auto_approve:
        ans = input("Operator approval required. Type APPROVE to continue: ")
        if ans.strip().upper() != "APPROVE":
            print("Operator approval not granted. Aborting.")
            return False
    live, backup = activate_pack(staged)
    print(f"[installer] Activated {pack_id} -> {live} (backup: {backup})")
    ok, out = run_health_check(live, timeout=30)
    if not ok:
        print("[installer] Health-check failed. Rolling back.")
        if backup.exists():
            if live.exists(): shutil.rmtree(live)
            shutil.move(str(backup), str(live))
            print("[installer] Rolled back to backup", backup)
        return False
    print("[installer] Health-check OK.")
    return True

def rollback_pack(pack_id: str, ts="latest"):
    pack_backups = BACKUPS_DIR / pack_id
    if not pack_backups.exists():
        print("No backups for pack", pack_id); return False
    if ts == "latest":
        choices = sorted([d.name for d in pack_backups.iterdir() if d.is_dir()], reverse=True)
        if not choices:
            print("No valid backups"); return False
        ts = choices[0]
    backup = pack_backups / ts
    live_target = LIVE_DIR / pack_id
    if live_target.exists(): shutil.rmtree(live_target)
    shutil.move(str(backup), str(live_target))
    print("Rollback successful for", pack_id)
    return True

def main():
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["stage","install","activate","rollback","dry-run","info"])
    p.add_argument("--pack", required=False, help="pack id e.g. pack01_unified_process")
    p.add_argument("--auto-approve", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    env = detect_environment()
    print("[installer] env:", env)
    mode = best_install_mode(env)
    print("[installer] preferred installer mode:", mode)
    if args.action in ("stage","dry-run"):
        if not args.pack: p.error("--pack required")
        print("Staging/dry-run:", args.pack)
        deploy_pack(args.pack, dry_run=True, auto_approve=args.auto_approve)
    elif args.action in ("install","activate"):
        if not args.pack: p.error("--pack required")
        ok = deploy_pack(args.pack, dry_run=False, auto_approve=args.auto_approve)
        print("install result:", ok)
    elif args.action == "rollback":
        if not args.pack: p.error("--pack required")
        rollback_pack(args.pack)
    elif args.action == "info":
        print("Packs available:", [p.name for p in PACKS_DIR.iterdir() if p.is_dir()])

if __name__ == "__main__":
    main()
PY

chmod +x "$PY_INSTALLER"

# 4) installer/node_wrapper.js
cat > "$NODE_WRAPPER" <<'NODE'
#!/usr/bin/env node
// installer/node_wrapper.js
const { spawnSync } = require("child_process");
const args = process.argv.slice(2);
function callPython(...a) {
  const p = spawnSync("python3", a, { stdio: "inherit" });
  if (p.error) console.error("Python call failed:", p.error);
  return p.status;
}
if (args[0] === "install") {
  callPython("installer/aurora_installer.py", "install", "--pack", args[1]);
} else {
  console.log("Node installer wrapper: args", args);
}
NODE

chmod +x "$NODE_WRAPPER"

# 5) scripts/create_packs_structure.sh
cat > "$PACKS_SCRIPT" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PACKS="$ROOT/packs"
STAGING="$ROOT/staging"
LIVE="$ROOT/live"
BACKUPS="$ROOT/backups"
AUDIT="$ROOT/audit"
DEVTOOLS="$ROOT/dev-tools"

mkdir -p "$PACKS" "$STAGING" "$LIVE" "$BACKUPS" "$AUDIT" "$DEVTOOLS"

for i in $(seq -w 1 15); do
  pack="pack$(printf "%02d" $i)_pack$(printf "%02d" $i)"
  dir="$PACKS/$pack"
  mkdir -p "$dir"
  cat > "$dir/install.sh" <<'SH2'
#!/usr/bin/env bash
echo "Install stub for PACK"
exit 0
SH2
  cat > "$dir/start.sh" <<'SH2'
#!/usr/bin/env bash
echo "Start stub"
exit 0
SH2
  cat > "$dir/stop.sh" <<'SH2'
#!/usr/bin/env bash
echo "Stop stub"
exit 0
SH2
  cat > "$dir/health_check.sh" <<'SH2'
#!/usr/bin/env bash
# default healthy
exit 0
SH2
  chmod +x "$dir"/*.sh
done

echo "Skeleton packs created under $PACKS"
echo "Safety dirs created: $STAGING $LIVE $BACKUPS $AUDIT $DEVTOOLS"
SH

chmod +x "$PACKS_SCRIPT"

# 6) README_INSTALLER.md
cat > "$README" <<'MD'
README_INSTALLER.md

How to use the Aurora hybrid installer (Section 0):

1) Create pack skeletons:
   ./scripts/create_packs_structure.sh

2) Inspect packs/pack01...pack15 and populate each with real files
   (install.sh, start.sh, stop.sh, health_check.sh)

3) Stage a pack (dry-run):
   python3 installer/aurora_installer.py stage --pack pack01_pack01

4) Install (activate) with operator approval:
   python3 installer/aurora_installer.py install --pack pack01_pack01

5) Rollback:
   python3 installer/aurora_installer.py rollback --pack pack01_pack01

Notes:
- Default behavior is dry-run/staging only. Nothing is moved into live/ until you run install (activation).
- Use READMEs inside each pack for pack-specific install instructions.
MD

echo "Section 0 files written. Run:"
echo "  chmod +x $PACKS_SCRIPT"
echo "  $PACKS_SCRIPT"
echo "Then test a dry-run:"
echo "  python3 $PY_INSTALLER stage --pack pack01_pack01"
