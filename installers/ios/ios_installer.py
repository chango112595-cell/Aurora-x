#!/usr/bin/env python3
"""
Aurora-X iOS Installer
Creates SwiftUI wrapper app for iOS devices.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional


class iOSInstaller:
    """iOS platform installer for Aurora-X"""
    
    def __init__(self, install_dir: Optional[str] = None):
        self.install_dir = Path(install_dir) if install_dir else Path.home() / "aurora-x-ios"
        self.installers_dir = Path(__file__).parent
        self.wrapper_script = self.installers_dir / "create-ios-wrapper.sh"
        
    def detect_environment(self) -> Dict[str, bool]:
        """Detect available iOS development tools"""
        return {
            "xcode_available": self._check_xcode(),
            "swift_available": self._check_swift(),
            "cocoapods_available": self._check_cocoapods(),
        }
    
    def _check_xcode(self) -> bool:
        """Check if Xcode is available"""
        try:
            result = subprocess.run(
                ["xcodebuild", "-version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _check_swift(self) -> bool:
        """Check if Swift compiler is available"""
        try:
            result = subprocess.run(
                ["swift", "--version"],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _check_cocoapods(self) -> bool:
        """Check if CocoaPods is available"""
        try:
            result = subprocess.run(
                ["pod", "--version"],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def create_wrapper(self, base_url: Optional[str] = None, api_key: Optional[str] = None) -> bool:
        """Create iOS wrapper app using the shell script"""
        if not self.wrapper_script.exists():
            print(f"[ERROR] iOS wrapper script not found: {self.wrapper_script}")
            return False
        
        try:
            # Make script executable
            os.chmod(self.wrapper_script, 0o755)
            
            # Run the wrapper creation script
            result = subprocess.run(
                ["bash", str(self.wrapper_script)],
                cwd=str(self.installers_dir),
                check=True
            )
            
            wrapper_dir = self.installers_dir / "AuroraXWebWrapper"
            
            if wrapper_dir.exists():
                print(f"[OK] iOS wrapper created at: {wrapper_dir}")
                
                # Update ContentView.swift with provided URL/API key if given
                if base_url or api_key:
                    self._update_content_view(wrapper_dir, base_url, api_key)
                
                print("\n[INFO] Next steps:")
                print("1. Open AuroraXWebWrapper/ in Xcode")
                print("2. Create a new iOS app project")
                print("3. Replace default files with generated Swift files")
                print("4. Configure signing and build")
                
                return True
            else:
                print("[ERROR] Wrapper directory was not created")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] iOS wrapper creation failed: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            return False
    
    def _update_content_view(self, wrapper_dir: Path, base_url: Optional[str], api_key: Optional[str]):
        """Update ContentView.swift with custom URL and API key"""
        content_view = wrapper_dir / "AuroraXWebWrapper" / "ContentView.swift"
        
        if not content_view.exists():
            print("[WARNING] ContentView.swift not found, skipping update")
            return
        
        try:
            content = content_view.read_text()
            
            if base_url:
                # Update base URL
                import re
                content = re.sub(
                    r'private let baseURL = URL\(string: "[^"]+"\)!',
                    f'private let baseURL = URL(string: "{base_url}")!',
                    content
                )
            
            if api_key:
                # Update API key
                import re
                content = re.sub(
                    r'private let apiKey: String\? = nil',
                    f'private let apiKey: String? = "{api_key}"',
                    content
                )
            
            content_view.write_text(content)
            print("[OK] Updated ContentView.swift with custom configuration")
            
        except Exception as e:
            print(f"[WARNING] Failed to update ContentView.swift: {e}")
    
    def install(self, base_url: Optional[str] = None, api_key: Optional[str] = None) -> bool:
        """Install/create iOS wrapper app"""
        env = self.detect_environment()
        
        if not env["xcode_available"] and not env["swift_available"]:
            print("[WARNING] Xcode/Swift not detected")
            print("[INFO] You can still create the wrapper template")
            print("[INFO] Install Xcode from the App Store for full development")
        
        return self.create_wrapper(base_url=base_url, api_key=api_key)


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Aurora-X iOS Installer")
    parser.add_argument(
        "--base-url",
        help="Aurora server base URL (e.g., https://aurora.example.com)"
    )
    parser.add_argument(
        "--api-key",
        help="API key for authenticated access"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check available iOS development tools"
    )
    
    args = parser.parse_args()
    
    installer = iOSInstaller()
    
    if args.check:
        env = installer.detect_environment()
        print("iOS Development Environment:")
        print(f"  Xcode available: {env['xcode_available']}")
        print(f"  Swift available: {env['swift_available']}")
        print(f"  CocoaPods available: {env['cocoapods_available']}")
        return 0
    
    success = installer.install(base_url=args.base_url, api_key=args.api_key)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
