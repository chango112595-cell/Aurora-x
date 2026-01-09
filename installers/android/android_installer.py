#!/usr/bin/env python3
"""
Aurora-X Android Installer
Supports both Termux (development) and APK wrapper (production) installation methods.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional


class AndroidInstaller:
    """Android platform installer for Aurora-X"""
    
    def __init__(self, install_dir: Optional[str] = None):
        self.install_dir = Path(install_dir) if install_dir else Path.home() / "aurora-x"
        self.repo_url = os.environ.get("AURORA_REPO_URL", "https://github.com/chango112595-cell/Aurora-x")
        self.installers_dir = Path(__file__).parent
        
    def detect_environment(self) -> Dict[str, bool]:
        """Detect available Android installation methods"""
        return {
            "termux_available": self._check_termux(),
            "adb_available": self._check_adb(),
            "capacitor_available": self._check_capacitor(),
        }
    
    def _check_termux(self) -> bool:
        """Check if Termux is available"""
        try:
            result = subprocess.run(
                ["termux-info"],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _check_adb(self) -> bool:
        """Check if ADB (Android Debug Bridge) is available"""
        try:
            result = subprocess.run(
                ["adb", "version"],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _check_capacitor(self) -> bool:
        """Check if Capacitor CLI is available"""
        try:
            result = subprocess.run(
                ["npx", "cap", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def install_termux(self) -> bool:
        """Install Aurora-X via Termux (development method)"""
        termux_script = self.installers_dir / "termux-install.sh"
        
        if not termux_script.exists():
            print(f"[ERROR] Termux install script not found: {termux_script}")
            return False
        
        try:
            # Make script executable
            os.chmod(termux_script, 0o755)
            
            # Run the installation script
            result = subprocess.run(
                ["bash", str(termux_script)],
                cwd=str(self.installers_dir),
                check=True
            )
            
            print("[OK] Termux installation completed")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Termux installation failed: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] Unexpected error during Termux installation: {e}")
            return False
    
    def build_apk_wrapper(self, output_dir: Optional[str] = None) -> bool:
        """Build APK wrapper using Capacitor (production method)"""
        if not self._check_capacitor():
            print("[ERROR] Capacitor CLI not found. Install with: npm i -g @capacitor/cli")
            return False
        
        apk_dir = self.installers_dir / "apk-wrapper"
        output_path = Path(output_dir) if output_dir else apk_dir / "build"
        
        try:
            # Check if Capacitor project exists, if not initialize it
            if not (apk_dir / "package.json").exists():
                print("[INFO] Initializing Capacitor project...")
                subprocess.run(
                    ["npm", "init", "-y"],
                    cwd=str(apk_dir),
                    check=True
                )
                
                subprocess.run(
                    ["npm", "install", "@capacitor/core", "@capacitor/cli"],
                    cwd=str(apk_dir),
                    check=True
                )
                
                subprocess.run(
                    ["npx", "cap", "init"],
                    cwd=str(apk_dir),
                    check=True
                )
            
            # Add Android platform
            subprocess.run(
                ["npx", "cap", "add", "android"],
                cwd=str(apk_dir),
                check=True
            )
            
            print(f"[OK] APK wrapper project ready at: {apk_dir}")
            print("[INFO] Open Android Studio to build signed APK:")
            print(f"      cd {apk_dir} && npx cap open android")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] APK wrapper build failed: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] Unexpected error during APK build: {e}")
            return False
    
    def install(self, method: str = "auto") -> bool:
        """Install Aurora-X on Android using the best available method"""
        env = self.detect_environment()
        
        if method == "auto":
            if env["termux_available"]:
                method = "termux"
            elif env["capacitor_available"]:
                method = "apk"
            else:
                print("[ERROR] No suitable installation method found")
                print("[INFO] Available methods:")
                print("  - Termux: Install Termux app from F-Droid")
                print("  - APK: Install Node.js and Capacitor CLI")
                return False
        
        if method == "termux":
            return self.install_termux()
        elif method == "apk":
            return self.build_apk_wrapper()
        else:
            print(f"[ERROR] Unknown installation method: {method}")
            return False


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Aurora-X Android Installer")
    parser.add_argument(
        "method",
        choices=["termux", "apk", "auto"],
        nargs="?",
        default="auto",
        help="Installation method (default: auto-detect)"
    )
    parser.add_argument(
        "--install-dir",
        help="Installation directory (default: ~/aurora-x)"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check available installation methods"
    )
    
    args = parser.parse_args()
    
    installer = AndroidInstaller(install_dir=args.install_dir)
    
    if args.check:
        env = installer.detect_environment()
        print("Android Installation Environment:")
        print(f"  Termux available: {env['termux_available']}")
        print(f"  ADB available: {env['adb_available']}")
        print(f"  Capacitor available: {env['capacitor_available']}")
        return 0
    
    success = installer.install(method=args.method)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
