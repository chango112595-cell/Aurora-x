#!/usr/bin/env python3
"""
Aurora Docker Healer - Autonomous Docker Issue Resolution
Tier 53: Docker Infrastructure Mastery
"""

import subprocess
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class AuroraDockerHealer:
    """Aurora's autonomous Docker diagnostic and healing system"""

    def __init__(self):
        self.workspace = Path(__file__).parent
        self.log_file = self.workspace / "aurora_docker_healing.log"
        self.issues_found = []
        self.fixes_applied = []

    def log(self, message: str, level: str = "INFO"):
        """Log Aurora's Docker healing activities"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "agent": "AURORA_DOCKER_HEALER"
        }

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        icon = "🌟" if level == "INFO" else "⚠️" if level == "WARNING" else "❌"
        print(f"{icon} [{level}] {message}")

    def check_docker_desktop_running(self) -> bool:
        """Check if Docker Desktop is running"""
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                    "Get-Process | Where-Object {$_.ProcessName -eq 'Docker Desktop'}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return "Docker Desktop" in result.stdout
        except Exception as e:
            self.log(f"Error checking Docker Desktop process: {e}", "ERROR")
            return False

    def check_docker_daemon(self) -> bool:
        """Check if Docker daemon is accessible"""
        try:
            result = subprocess.run(
                ["docker", "version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            self.log(f"Docker daemon not accessible: {e}", "WARNING")
            return False

    def start_docker_desktop(self) -> bool:
        """Attempt to start Docker Desktop"""
        try:
            self.log("Attempting to start Docker Desktop...", "INFO")

            # Try to find Docker Desktop executable
            docker_paths = [
                r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
                r"C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe"
            ]

            for path in docker_paths:
                if Path(path).exists():
                    subprocess.Popen([path], shell=True)
                    self.log(f"Docker Desktop started from: {path}", "INFO")
                    return True

            self.log(
                "Docker Desktop executable not found in standard locations", "WARNING")
            return False

        except Exception as e:
            self.log(f"Failed to start Docker Desktop: {e}", "ERROR")
            return False

    def wait_for_docker_ready(self, timeout: int = 60) -> bool:
        """Wait for Docker daemon to be ready"""
        self.log(
            f"Waiting for Docker daemon to be ready (timeout: {timeout}s)...", "INFO")

        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_docker_daemon():
                elapsed = int(time.time() - start_time)
                self.log(f"Docker daemon is ready! (took {elapsed}s)", "INFO")
                return True

            time.sleep(2)
            print(".", end="", flush=True)

        print()
        self.log("Docker daemon did not become ready in time", "ERROR")
        return False

    def diagnose_docker_issues(self) -> Dict[str, Any]:
        """Comprehensive Docker diagnostics"""
        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "docker_desktop_running": False,
            "docker_daemon_accessible": False,
            "wsl2_status": "unknown",
            "issues": [],
            "recommendations": []
        }

        self.log("Starting comprehensive Docker diagnostics...", "INFO")

        # Check 1: Docker Desktop process
        if self.check_docker_desktop_running():
            diagnosis["docker_desktop_running"] = True
            self.log("✅ Docker Desktop process is running", "INFO")
        else:
            diagnosis["docker_desktop_running"] = False
            diagnosis["issues"].append("Docker Desktop is not running")
            diagnosis["recommendations"].append(
                "Start Docker Desktop application")
            self.log("❌ Docker Desktop is not running", "WARNING")

        # Check 2: Docker daemon
        if self.check_docker_daemon():
            diagnosis["docker_daemon_accessible"] = True
            self.log("✅ Docker daemon is accessible", "INFO")
        else:
            diagnosis["docker_daemon_accessible"] = False
            diagnosis["issues"].append("Docker daemon is not accessible")
            diagnosis["recommendations"].append(
                "Wait for Docker Desktop to fully initialize")
            self.log("❌ Docker daemon is not accessible", "WARNING")

        # Check 3: WSL2 status (for Windows)
        try:
            result = subprocess.run(
                ["powershell", "-Command", "wsl --status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                diagnosis["wsl2_status"] = "running"
                self.log("✅ WSL2 is available", "INFO")
            else:
                diagnosis["wsl2_status"] = "not_available"
                diagnosis["issues"].append(
                    "WSL2 may not be properly configured")
        except Exception:
            diagnosis["wsl2_status"] = "unknown"

        # Check 4: Docker version
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                diagnosis["docker_version"] = result.stdout.strip()
                self.log(f"Docker version: {result.stdout.strip()}", "INFO")
        except Exception:
            diagnosis["issues"].append("Docker CLI not found or not in PATH")

        return diagnosis

    def autonomous_heal(self) -> bool:
        """Aurora's autonomous Docker healing process"""
        print("\n" + "=" * 80)
        print("🌟 AURORA DOCKER HEALER - AUTONOMOUS DIAGNOSTIC & REPAIR".center(80))
        print("=" * 80 + "\n")

        # Phase 1: Diagnosis
        diagnosis = self.diagnose_docker_issues()

        print("\n" + "=" * 80)
        print("📊 DIAGNOSIS RESULTS")
        print("=" * 80)
        print(
            f"Docker Desktop Running: {'✅' if diagnosis['docker_desktop_running'] else '❌'}")
        print(
            f"Docker Daemon Accessible: {'✅' if diagnosis['docker_daemon_accessible'] else '❌'}")
        print(f"WSL2 Status: {diagnosis['wsl2_status']}")

        if diagnosis["issues"]:
            print(f"\n⚠️  Issues Found: {len(diagnosis['issues'])}")
            for issue in diagnosis["issues"]:
                print(f"   • {issue}")

        # Phase 2: Autonomous Healing
        if not diagnosis["docker_desktop_running"]:
            print("\n" + "=" * 80)
            print("🔧 PHASE 2: AUTONOMOUS HEALING")
            print("=" * 80 + "\n")

            self.log("Aurora will attempt to start Docker Desktop...", "INFO")

            if self.start_docker_desktop():
                self.fixes_applied.append("Started Docker Desktop")

                # Wait for Docker to be ready
                if self.wait_for_docker_ready(timeout=90):
                    self.fixes_applied.append(
                        "Docker daemon is now accessible")
                    self.log("✅ Docker is now fully operational!", "INFO")

                    # Verify fix
                    print("\n" + "=" * 80)
                    print("🔍 VERIFICATION")
                    print("=" * 80)
                    final_check = self.diagnose_docker_issues()

                    if final_check["docker_daemon_accessible"]:
                        print("\n✅ Docker healing SUCCESSFUL!")
                        return True
                    else:
                        print("\n⚠️  Docker started but daemon still not accessible")
                        print("Please wait a few more seconds and try again")
                        return False
                else:
                    self.log(
                        "Docker Desktop started but daemon not ready yet", "WARNING")
                    print(
                        "\n⚠️  Docker Desktop is starting (this may take 30-60 seconds)")
                    print("Please run this script again in a moment")
                    return False
            else:
                print("\n❌ Could not automatically start Docker Desktop")
                print("\n📋 MANUAL STEPS REQUIRED:")
                print("   1. Manually start Docker Desktop from Start Menu")
                print("   2. Wait for 'Docker Desktop is running' notification")
                print("   3. Run this script again or reload VS Code")
                return False

        elif not diagnosis["docker_daemon_accessible"]:
            print("\n⚠️  Docker Desktop is running but daemon not accessible yet")
            print("This usually means Docker is still initializing...")

            if self.wait_for_docker_ready(timeout=60):
                print("\n✅ Docker daemon is now ready!")
                return True
            else:
                print("\n⚠️  Docker is taking longer than expected to initialize")
                print("\n📋 RECOMMENDATIONS:")
                print("   1. Check Docker Desktop dashboard for errors")
                print("   2. Try restarting Docker Desktop")
                print("   3. Check Windows Services for 'com.docker.service'")
                return False

        else:
            print("\n✅ Docker is already fully operational!")
            print("No healing required.")
            return True

    def generate_report(self) -> str:
        """Generate healing report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "agent": "AURORA_DOCKER_HEALER",
            "issues_found": len(self.issues_found),
            "fixes_applied": self.fixes_applied,
            "status": "healed" if self.check_docker_daemon() else "needs_attention"
        }

        print("\n" + "=" * 80)
        print("📊 AURORA DOCKER HEALING REPORT")
        print("=" * 80)
        print(f"Timestamp: {report['timestamp']}")
        print(f"Fixes Applied: {len(self.fixes_applied)}")

        if self.fixes_applied:
            for fix in self.fixes_applied:
                print(f"   ✅ {fix}")

        print(
            f"\nFinal Status: {'🟢 OPERATIONAL' if report['status'] == 'healed' else '🟡 NEEDS ATTENTION'}")
        print("=" * 80 + "\n")

        return json.dumps(report, indent=2)


def main():
    """Aurora autonomously heals Docker issues"""
    healer = AuroraDockerHealer()

    success = healer.autonomous_heal()
    healer.generate_report()

    if success:
        print("\n🎉 Aurora has successfully healed Docker!")
        print("You can now use Docker and Dev Containers.")
        return 0
    else:
        print("\n⚠️  Manual intervention may be required.")
        print("See recommendations above.")
        return 1


if __name__ == "__main__":
    exit(main())
