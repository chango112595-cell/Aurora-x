#!/usr/bin/env python3
"""
T07 Orchestrator - Continuous spec monitoring daemon
Monitors specs/*.md for changes and auto-runs synthesis
Optional git auto-commit/push gated by env vars
"""
from pathlib import Path
import os, time, subprocess, json, hashlib, sys
from datetime import datetime

SPEC_DIR = Path("specs")
RUNS = Path("runs")
POLL_SECS = int(os.getenv("AURORA_ORCH_INTERVAL", "300"))  # 5 min default
GIT_AUTO = os.getenv("AURORA_GIT_AUTO", "0") == "1"       # gate push
BRANCH = os.getenv("AURORA_GIT_BRANCH", "main")
REPO_URL = os.getenv("AURORA_GIT_URL", "")                # e.g. https://github.com/..git
DISCORD = Path("tools/discord_cli.py")

def spec_digest(p: Path) -> str:
    """Compute SHA256 hash of spec file"""
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()

def list_specs():
    """List all markdown spec files"""
    return sorted([p for p in SPEC_DIR.glob("*.md") if p.is_file()])

def latest_run_for(spec_name: str):
    """Get latest run info for a spec from spec_runs.jsonl"""
    log = RUNS / "spec_runs.jsonl"
    if not log.exists(): 
        return None
    last = None
    for line in log.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
            if row.get("spec") == spec_name:
                last = row
        except:
            pass
    return last

def synth(spec: Path):
    """Run v3 synthesis for a spec"""
    print(f"⚙️  Synthesizing {spec.name}")
    try:
        # Run spec compilation
        result = subprocess.run(
            ["python", "tools/spec_compile_v3.py", str(spec)],
            env=os.environ.copy(),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Successfully synthesized {spec.name}")
            # Send Discord notification if available
            if DISCORD.exists():
                try:
                    subprocess.run(
                        ["python", str(DISCORD), "success", 
                         f"🔄 Auto-synth: {spec.name}"],
                        check=False
                    )
                except:
                    pass
        else:
            print(f"❌ Failed to synthesize {spec.name}")
            print(f"Error: {result.stderr}")
            if DISCORD.exists():
                try:
                    subprocess.run(
                        ["python", str(DISCORD), "error",
                         f"❌ Auto-synth failed: {spec.name}"],
                        check=False
                    )
                except:
                    pass
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Exception synthesizing {spec.name}: {e}")
        return False

def git_push_if_enabled(msg: str):
    """Auto-commit and push if enabled via env vars"""
    if not GIT_AUTO:
        return
    
    if not REPO_URL:
        print("⚠️  AURORA_GIT_URL not set, skipping git push")
        return
    
    try:
        # Add all changes
        subprocess.run(["git", "add", "-A"], check=True)
        
        # Try to commit
        result = subprocess.run(
            ["git", "commit", "-m", msg],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"📝 Committed: {msg}")
            # Push to remote
            push_result = subprocess.run(
                ["git", "push", "origin", BRANCH],
                capture_output=True,
                text=True
            )
            if push_result.returncode == 0:
                print(f"🚀 Pushed to {BRANCH}")
            else:
                print(f"⚠️  Push failed: {push_result.stderr}")
        else:
            # Nothing to commit is OK
            if "nothing to commit" not in result.stdout:
                print(f"⚠️  Commit failed: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Git operation failed: {e}")
    except Exception as e:
        print(f"❌ Git error: {e}")

def run_once(digests: dict) -> dict:
    """Run one iteration of spec monitoring"""
    specs_processed = 0
    specs_changed = 0
    
    for p in list_specs():
        d = spec_digest(p)
        changed = (digests.get(p.name) != d)
        last = latest_run_for(p.name)
        
        if changed:
            print(f"🔄 Change detected: {p.name}")
            specs_changed += 1
        
        if changed or last is None:
            if last is None:
                print(f"🆕 First run for: {p.name}")
            
            if synth(p):
                git_push_if_enabled(f"aurora: spec run for {p.name}")
                digests[p.name] = d
                specs_processed += 1
    
    if specs_processed > 0:
        print(f"📊 Processed {specs_processed} specs ({specs_changed} changed)")
    
    return digests

def main():
    """Main orchestrator loop"""
    print("=" * 60)
    print("🌌 Aurora-X T07 Orchestrator Starting")
    print("=" * 60)
    print(f"📁 Spec directory: {SPEC_DIR}")
    print(f"⏱️  Poll interval: {POLL_SECS} seconds")
    print(f"🔀 Git auto-commit: {'ON' if GIT_AUTO else 'OFF'}")
    
    if GIT_AUTO:
        print(f"🌿 Git branch: {BRANCH}")
        print(f"📍 Git repo: {REPO_URL or 'Not set'}")
    
    print("=" * 60)
    
    # Initial digest computation
    digests = {}
    for p in list_specs():
        digests[p.name] = spec_digest(p)
        print(f"📄 Monitoring: {p.name} [{digests[p.name][:8]}...]")
    
    print(f"\n🚀 Starting continuous monitoring...")
    
    iteration = 0
    try:
        while True:
            iteration += 1
            print(f"\n--- Iteration {iteration} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
            
            # Run monitoring pass
            digests = run_once(digests)
            
            # Sleep until next iteration
            print(f"💤 Sleeping {POLL_SECS} seconds until next check...")
            time.sleep(POLL_SECS)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Orchestrator stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Orchestrator error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()