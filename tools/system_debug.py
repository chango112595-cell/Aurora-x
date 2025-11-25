#!/usr/bin/env python3
"""Aurora-X System Debug - Check all components."""
import json
import subprocess
import sys
from pathlib import Path


def header(text):
    """Print section header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print("=" * 60)


def check_python_environment():
    """Check Python and dependencies."""
    header("Python Environment")
    print(f"Python: {sys.version}")

    critical_imports = ["fastapi", "uvicorn", "pytest", "sqlite3"]

    for module in critical_imports:
        try:
            __import__(module)
            print(f"[OK] {module}")
        except ImportError:
            print(f"[ERROR] {module} - MISSING")


def check_node_environment():
    """Check Node.js and npm."""
    header("Node.js Environment")

    try:
        node_version = subprocess.check_output(["node", "--version"], text=True).strip()
        print(f"[OK] Node.js: {node_version}")
    except Exception as e:
        print(f"[ERROR] Node.js: {e}")

    try:
        npm_version = subprocess.check_output(["npm", "--version"], text=True).strip()
        print(f"[OK] npm: {npm_version}")
    except Exception as e:
        print(f"[ERROR] npm: {e}")


def check_file_structure():
    """Check critical directories and files."""
    header("File Structure")

    critical_paths = [
        "aurora_x/",
        "aurora_x/main.py",
        "aurora_x/serve.py",
        "aurora_x/bridge/service.py",
        "server/index.ts",
        "server/routes.ts",
        "specs/",
        "runs/",
        "data/",
        "tools/",
    ]

    for path_str in critical_paths:
        path = Path(path_str)
        if path.exists():
            print(f"[OK] {path_str}")
        else:
            print(f"[ERROR] {path_str} - MISSING")


def check_database():
    """Check database health."""
    header("Database")

    db_path = Path("data/corpus.db")
    if not db_path.exists():
        print(f"[ERROR] Database not found: {db_path}")
        return

    print(f"[OK] Database exists: {db_path}")

    try:
        import sqlite3

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"[DATA] Tables: {[t[0] for t in tables]}")

        # Check corpus entries
        cursor.execute("SELECT COUNT(*) FROM corpus")
        count = cursor.fetchone()[0]
        print(f"[EMOJI] Corpus entries: {count}")

        conn.close()
    except Exception as e:
        print(f"[ERROR] Database error: {e}")


def check_ports():
    """Check if critical ports are available."""
    header("Port Status")

    import socket

    ports = {5000: "Main web server", 5001: "Bridge service"}

    for port, desc in ports.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("0.0.0.0", port))
            sock.close()
            print(f"[OK] Port {port} available - {desc}")
        except OSError:
            print(f"[WARN]  Port {port} in use - {desc}")


def check_processes():
    """Check running Aurora processes."""
    header("Running Processes")

    try:
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)

        aurora_procs = [
            line for line in result.stdout.split("\n") if "aurora" in line.lower() or "bridge" in line.lower()
        ]

        if aurora_procs:
            print("[SCAN] Aurora-related processes:")
            for proc in aurora_procs[:10]:  # Limit output
                print(f"  {proc[:100]}")
        else:
            print("ℹ️  No Aurora processes currently running")
    except Exception as e:
        print(f"[ERROR] Process check failed: {e}")


def check_bridge_service():
    """Check Bridge service health."""
    header("Bridge Service")

    try:
        import requests

        response = requests.get("http://127.0.0.1:5001/healthz", timeout=2)
        if response.status_code == 200:
            data = response.json()
            print("[OK] Bridge is healthy")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
        else:
            print(f"[WARN]  Bridge responded with status {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Bridge not accessible: {e}")


def check_web_server():
    """Check main web server."""
    header("Main Web Server")

    try:
        import requests

        response = requests.get("http://127.0.0.1:5000/healthz", timeout=2)
        if response.status_code == 200:
            data = response.json()
            print("[OK] Web server is healthy")
            print(f"   Status: {data.get('status')}")
            print(f"   Components: {data.get('components')}")
        else:
            print(f"[WARN]  Server responded with status {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Web server not accessible: {e}")


def check_specs():
    """Check spec files."""
    header("Spec Files")

    specs_dir = Path("specs")
    if not specs_dir.exists():
        print("[ERROR] Specs directory not found")
        return

    spec_files = list(specs_dir.glob("*.md"))
    print(f"[EMOJI] Total spec files: {len(spec_files)}")

    if spec_files:
        print("Recent specs:")
        for spec in sorted(spec_files, key=lambda p: p.stat().st_mtime, reverse=True)[:5]:
            print(f"  - {spec.name}")


def check_runs():
    """Check run directories."""
    header("Run Directories")

    runs_dir = Path("runs")
    if not runs_dir.exists():
        print("[ERROR] Runs directory not found")
        return

    run_dirs = [d for d in runs_dir.iterdir() if d.is_dir() and d.name.startswith("run-")]
    print(f"[EMOJI] Total runs: {len(run_dirs)}")

    latest_link = runs_dir / "latest"
    if latest_link.exists():
        target = latest_link.resolve()
        print(f"[LINK] Latest run: {target.name}")
    else:
        print("[WARN]  No 'latest' symlink")


def check_progress():
    """Check progress tracking."""
    header("Progress Tracking")

    progress_file = Path("progress.json")
    if not progress_file.exists():
        print("[ERROR] progress.json not found")
        return

    try:
        data = json.loads(progress_file.read_text())
        phases = data.get("phases", [])
        print("[OK] Progress file loaded")
        print(f"   Phases: {len(phases)}")

        for phase in phases[:3]:
            print(f"   {phase.get('id')} - {phase.get('name')}")
    except Exception as e:
        print(f"[ERROR] Error reading progress: {e}")


def check_git():
    """Check Git status."""
    header("Git Repository")

    try:
        branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
        print(f"[EMOJI] Current branch: {branch}")

        status = subprocess.check_output(["git", "status", "--short"], text=True)
        if status:
            lines = status.strip().split("\n")
            print(f"[EMOJI] Modified files: {len(lines)}")
        else:
            print("[OK] Working directory clean")
    except Exception as e:
        print(f"[ERROR] Git check failed: {e}")


def main():
    """Run all diagnostics."""
    print("\n" + "=" * 60)
    print("  [EMOJI] AURORA-X SYSTEM DIAGNOSTICS")
    print("=" * 60)

    check_python_environment()
    check_node_environment()
    check_file_structure()
    check_database()
    check_ports()
    check_processes()
    check_bridge_service()
    check_web_server()
    check_specs()
    check_runs()
    check_progress()
    check_git()

    header("Summary")
    print("[OK] Diagnostics complete")
    print("[EMOJI] Review any [ERROR] or [WARN]  items above")
    print("[EMOJI] Log saved to: tools/system_debug.log")


if __name__ == "__main__":
    main()
