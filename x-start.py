#!/usr/bin/env python3
"""
Aurora Universal Start Command - Self-Analyzing & Self-Configuring
Analyzes the system using Aurora's own detection capabilities and auto-configures everything.
Works on Windows, Linux, macOS, Android, iOS, Embedded - ANY platform.
"""

from __future__ import annotations

import contextlib
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)

IS_WINDOWS = platform.system() == "Windows"
BOOTSTRAP_STATE = ROOT / ".aurora" / "bootstrap_state.json"

AURORA_HOST = os.getenv("AURORA_HOST", "localhost")
AURORA_PORT = os.getenv("AURORA_PORT", "5000")
AURORA_BRIDGE_HOST = os.getenv("AURORA_BRIDGE_HOST", AURORA_HOST)
AURORA_BRIDGE_PORT = os.getenv("AURORA_BRIDGE_PORT", "5001")
AURORA_NEXUS_HOST = os.getenv("AURORA_NEXUS_HOST", AURORA_HOST)
AURORA_NEXUS_PORT = os.getenv("AURORA_NEXUS_PORT", "5002")
LUMINAR_HOST = os.getenv("LUMINAR_HOST", AURORA_HOST)
LUMINAR_PORT = os.getenv("LUMINAR_PORT", "8000")


class SystemAnalyzer:
    """Uses Aurora's own detection to analyze the system"""

    def __init__(self):
        self.platform_system = platform.system()
        self.platform_machine = platform.machine()
        self.python_version = None
        self.python_cmd = None
        self.node_version = None
        self.npm_cmd = None
        self.capabilities = {}

    def analyze(self) -> dict:
        """Analyze the system and return capabilities"""
        print("\n" + "=" * 80)
        print("🔍 AURORA SYSTEM ANALYSIS")
        print("=" * 80)

        # Detect platform
        platform_info = {
            "system": self.platform_system,
            "machine": self.platform_machine,
            "platform": platform.platform(),
        }
        print(f"\n📱 Platform: {platform_info['system']} {platform_info['machine']}")

        # Detect Python
        python_info = self._detect_python()
        print(f"🐍 Python: {python_info['version'] or 'NOT FOUND'}")
        if python_info["cmd"]:
            print(f"   Command: {python_info['cmd']}")

        # Detect Node.js
        node_info = self._detect_node()
        print(f"📦 Node.js: {node_info['version'] or 'NOT FOUND'}")
        if node_info["npm_cmd"]:
            print(f"   npm: {node_info['npm_cmd']}")

        # Detect hardware capabilities (using Aurora's detector if available)
        hardware_info = self._detect_hardware()
        hw_info = hardware_info
        print(f"💻 Hardware: {hw_info['cpu_cores']} cores, " f"{hw_info['memory_gb']:.1f}GB RAM")
        print(f"   Capability Score: {hardware_info['capability_score']}/100")

        # Check existing environments
        venv_info = self._check_venv()
        print(f"📁 Virtual Environment: {'Found' if venv_info['exists'] else 'Not Found'}")

        node_modules_info = self._check_node_modules()
        print(f"📦 Node Modules: {'Found' if node_modules_info['exists'] else 'Not Found'}")

        analysis = {
            "platform": platform_info,
            "python": python_info,
            "node": node_info,
            "hardware": hardware_info,
            "venv": venv_info,
            "node_modules": node_modules_info,
        }

        self.capabilities = analysis
        print("=" * 80 + "\n")

        return analysis

    def _detect_python(self) -> dict:
        """Detect Python installation"""
        candidates = ["python", "python3", "py"] if IS_WINDOWS else ["python3", "python"]

        # Check system Python first
        for cmd in candidates:
            try:
                result = subprocess.run(
                    [cmd, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    version = result.stdout.strip()
                    return {"version": version, "cmd": cmd, "available": True}
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue

        # Check venv Python
        if IS_WINDOWS:
            venv_python = ROOT / ".venv" / "Scripts" / "python.exe"
        else:
            venv_python = ROOT / ".venv" / "bin" / "python"

        if venv_python.exists():
            try:
                result = subprocess.run(
                    [str(venv_python), "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    version = result.stdout.strip()
                    return {
                        "version": version,
                        "cmd": str(venv_python),
                        "available": True,
                        "in_venv": True,
                    }
            except Exception:
                pass

        return {"version": None, "cmd": None, "available": False}

    def _detect_node(self) -> dict:
        """Detect Node.js installation"""
        npm_cmd = shutil.which("npm")
        node_cmd = shutil.which("node")

        if node_cmd:
            try:
                result = subprocess.run(
                    [node_cmd, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    version = result.stdout.strip()
                    return {
                        "version": version,
                        "cmd": node_cmd,
                        "npm_cmd": npm_cmd,
                        "available": True,
                    }
            except Exception:
                pass

        return {"version": None, "cmd": None, "npm_cmd": None, "available": False}

    def _detect_hardware(self) -> dict:
        """Detect hardware capabilities (using Aurora's detector if available)"""
        try:
            # Try to use Aurora's hardware detector
            sys.path.insert(0, str(ROOT))
            from aurora_nexus_v3.modules.hardware_detector import HardwareDetector

            detector = HardwareDetector(None)
            profile = detector.detect()
            return {
                "cpu_cores": profile.cpu.cores_logical,
                "memory_gb": profile.memory.total_mb / 1024,
                "capability_score": profile.capability_score,
                "gpu_available": profile.gpu_available,
            }
        except Exception:
            # Fallback to basic detection
            try:
                import psutil

                cpu_count = psutil.cpu_count()
                memory = psutil.virtual_memory()
                return {
                    "cpu_cores": cpu_count or 1,
                    "memory_gb": memory.total / (1024**3),
                    "capability_score": 50,  # Default score
                    "gpu_available": False,
                }
            except ImportError:
                # psutil not available, use platform module
                import multiprocessing

                cpu_count = multiprocessing.cpu_count()
                return {
                    "cpu_cores": cpu_count or 1,
                    "memory_gb": 1.0,  # Unknown
                    "capability_score": 25,
                    "gpu_available": False,
                }
            except Exception:
                return {
                    "cpu_cores": 1,
                    "memory_gb": 1.0,
                    "capability_score": 25,
                    "gpu_available": False,
                }

    def _check_venv(self) -> dict:
        """Check if virtual environment exists"""
        venv_dir = ROOT / ".venv"
        exists = venv_dir.exists()
        return {"exists": exists, "path": str(venv_dir) if exists else None}

    def _check_node_modules(self) -> dict:
        """Check if node_modules exists"""
        node_modules = ROOT / "node_modules"
        exists = node_modules.exists()
        return {"exists": exists, "path": str(node_modules) if exists else None}


class EnvironmentConfigurator:
    """Auto-configures environment based on system analysis"""

    def __init__(self, analysis: dict):
        self.analysis = analysis
        self.python_cmd = None
        self.npm_cmd = None

    def configure(self) -> bool:
        """Configure environment based on analysis"""
        print("\n" + "=" * 80)
        print("⚙️  AUTO-CONFIGURING ENVIRONMENT")
        print("=" * 80)

        # Configure Python
        python_ok = self._configure_python()
        if not python_ok:
            print("\n❌ Python setup failed. Cannot continue.")
            return False

        # Configure Node.js
        node_ok = self._configure_node()
        if not node_ok:
            print("\n⚠️  Node.js not available. Some services will not start.")

        print("=" * 80 + "\n")
        return True

    def _configure_python(self) -> bool:
        """Configure Python environment"""
        python_info = self.analysis["python"]

        if not python_info["available"]:
            print("\n❌ Python not found!")
            print("   Please install Python 3.8+ from https://www.python.org/")
            return False

        # Use detected Python command
        self.python_cmd = python_info["cmd"]

        # Create venv if needed
        venv_info = self.analysis["venv"]
        if not venv_info["exists"]:
            print("\n📦 Creating Python virtual environment...")
            try:
                subprocess.run(
                    [self.python_cmd, "-m", "venv", str(ROOT / ".venv")],
                    check=True,
                    timeout=60,
                )
                # Update Python command to venv Python
                if IS_WINDOWS:
                    self.python_cmd = str(ROOT / ".venv" / "Scripts" / "python.exe")
                else:
                    self.python_cmd = str(ROOT / ".venv" / "bin" / "python")
                print("   ✅ Virtual environment created")
            except Exception as e:
                print(f"   ⚠️  Failed to create venv: {e}")
                print("   Continuing with system Python...")

        # Verify pip
        print("   🔍 Verifying pip...")
        try:
            result = subprocess.run(
                [self.python_cmd, "-m", "pip", "--version"],
                capture_output=True,
                timeout=10,
            )
            if result.returncode != 0:
                print("   ⚠️  pip not working, upgrading...")
                subprocess.run(
                    [self.python_cmd, "-m", "pip", "install", "--upgrade", "pip"],
                    check=True,
                    timeout=120,
                )
        except Exception as e:
            print(f"   ⚠️  pip check failed: {e}")

        # Install requirements
        requirements = ROOT / "requirements.txt"
        if requirements.exists():
            print("   📦 Installing Python dependencies...")
            try:
                subprocess.run(
                    [self.python_cmd, "-m", "pip", "install", "-r", str(requirements)],
                    check=True,
                    timeout=600,
                )
                print("   ✅ Dependencies installed")
            except Exception as e:
                print(f"   ⚠️  Dependency installation failed: {e}")
                print("   Continuing anyway...")

        os.environ["AURORA_PYTHON"] = self.python_cmd
        return True

    def _configure_node(self) -> bool:
        """Configure Node.js environment"""
        node_info = self.analysis["node"]

        if not node_info["available"]:
            print("\n⚠️  Node.js not found!")
            print("   Some services (Backend API, Frontend) will not start.")
            print("   Install from https://nodejs.org/ to enable full functionality.")
            return False

        self.npm_cmd = node_info["npm_cmd"]

        # Install node_modules if needed
        node_modules_info = self.analysis["node_modules"]
        if not node_modules_info["exists"]:
            print("\n📦 Installing Node.js dependencies...")
            try:
                subprocess.run(
                    [self.npm_cmd, "install"],
                    check=True,
                    timeout=600,
                )
                print("   ✅ Node dependencies installed")
            except Exception as e:
                print(f"   ⚠️  Node dependency installation failed: {e}")
                return False

        return True


def read_manifest_counts() -> dict[str, int]:
    """Read manifest counts"""
    manifest_dir = ROOT / "manifests"
    result = {"tiers": 0, "aems": 0, "modules": 0}
    files = {
        "tiers": manifest_dir / "tiers.manifest.json",
        "aems": manifest_dir / "executions.manifest.json",
        "modules": manifest_dir / "modules.manifest.json",
    }
    for key, path in files.items():
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            entries = (
                data.get(key)
                or data.get("tiers")
                or data.get("executions")
                or data.get("modules")
                or []
            )
            if isinstance(entries, list):
                result[key] = len(entries)
        except Exception:
            continue
    return result


def check_port(port_num: int) -> bool:
    """Check if port is in use"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.5)
    try:
        result = sock.connect_ex(("127.0.0.1", port_num))
        sock.close()
        return result == 0
    except Exception:
        with contextlib.suppress(Exception):
            sock.close()
        return False


LOG_DIR = ROOT / "logs" / "x-start"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_HANDLES: list = []


def start_process(cmd, name: str, is_shell: bool = False) -> subprocess.Popen | None:
    """Start a process in the background"""
    log_path = LOG_DIR / f"{name.lower().replace(' ', '_')}.log"
    log_handle = log_path.open("a", encoding="utf-8")
    LOG_HANDLES.append(log_handle)

    kwargs = {
        "stdout": log_handle,
        "stderr": log_handle,
    }

    if IS_WINDOWS:
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        if is_shell:
            kwargs["shell"] = True
    else:
        kwargs["start_new_session"] = True

    try:
        return subprocess.Popen(cmd, **kwargs)
    except Exception as exc:
        print(f"   [WARN] Failed to start {name}: {exc}")
        return None


def start_service(name: str, cmd, port: int) -> None:
    """Start a service if port is available"""
    if check_port(port):
        print(f"   [OK] {name} already running on port {port}")
        return
    start_process(cmd, name=name, is_shell=isinstance(cmd, str))


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "🚀" * 40)
    print("AURORA UNIVERSAL START - SELF-ANALYZING & SELF-CONFIGURING")
    print("🚀" * 40)

    # Phase 0: System Analysis
    analyzer = SystemAnalyzer()
    analysis = analyzer.analyze()

    # Phase 1: Auto-Configure Environment
    configurator = EnvironmentConfigurator(analysis)
    if not configurator.configure():
        print("\n❌ Environment configuration failed. Exiting.")
        sys.exit(1)

    python_cmd = configurator.python_cmd
    npm_cmd = configurator.npm_cmd

    # Phase 2: Display Aurora Capabilities
    counts = read_manifest_counts()
    print("\n" + "=" * 80)
    print("🌟 AURORA CAPABILITIES")
    print("=" * 80)
    print(f"   {counts['tiers']} Tiers | {counts['aems']} AEMs | {counts['modules']} Modules")
    print(f"   Platform: {analysis['platform']['system']} {analysis['platform']['machine']}")
    hw = analysis["hardware"]
    print(f"   Hardware: {hw['cpu_cores']} cores, {hw['memory_gb']:.1f}GB RAM")
    print(f"   Capability Score: {analysis['hardware']['capability_score']}/100")
    print("=" * 80 + "\n")

    # Phase 3: Start Services
    print("\n" + "=" * 80)
    print("🚀 STARTING AURORA SERVICES")
    print("=" * 80)

    print("\n[WEB] 1. Starting Backend API + Frontend (port 5000)...")
    if npm_cmd:
        start_service(
            "Backend API + Frontend",
            "npm run dev" if IS_WINDOWS else [npm_cmd, "run", "dev"],
            5000,
        )
    else:
        print("   [SKIP] npm not available")
    time.sleep(2)

    print("\n[WEB] 2. Starting Aurora Bridge (port 5001)...")
    start_service("Aurora Bridge", [python_cmd, "-m", "aurora_x.bridge.service"], 5001)
    time.sleep(1)

    print("\n[WEB] 3. Starting Aurora Nexus V3 (port 5002)...")
    start_service(
        "Aurora Nexus V3",
        [python_cmd, str(ROOT / "aurora_nexus_v3" / "main.py")],
        5002,
    )
    time.sleep(2)

    print("\n[WEB] 4. Starting Luminar Nexus V2 (port 8000)...")
    start_service(
        "Luminar Nexus V2",
        [python_cmd, str(ROOT / "tools" / "luminar_nexus_v2.py"), "serve"],
        8000,
    )

    # Phase 4: Health Check
    print("\n" + "=" * 80)
    print("🏥 HEALTH CHECK")
    print("=" * 80)
    time.sleep(6)

    services = [
        ("Backend API + Frontend", 5000),
        ("Aurora Bridge", 5001),
        ("Aurora Nexus V3", 5002),
        ("Luminar Nexus V2", 8000),
    ]

    running = 0
    for name, port in services:
        is_running = check_port(port)
        status = "[✅] RUNNING" if is_running else "[⚠️] OFFLINE"
        print(f"   {name:30} Port {port:5} {status}")
        if is_running:
            running += 1

    print("\n" + "=" * 80)
    print("📊 AURORA SYSTEM STATUS")
    print("=" * 80)
    print(f"\n[POWER] Services Online: {running}/{len(services)}")

    if running >= 3:
        print("\n✅ Aurora runtime services are online.")
    else:
        print("\n⚠️  Some services are still starting or failed to launch.")

    print("\n[WEB] ACCESS POINTS:")
    print(f"   - Frontend:      http://{AURORA_HOST}:{AURORA_PORT}")
    print(f"   - Bridge API:    http://{AURORA_BRIDGE_HOST}:{AURORA_BRIDGE_PORT}")
    print(f"   - Nexus V3 API:  http://{AURORA_NEXUS_HOST}:{AURORA_NEXUS_PORT}")
    print(f"   - Luminar V2:    http://{LUMINAR_HOST}:{LUMINAR_PORT}")
    print("\n" + "=" * 80 + "\n")
