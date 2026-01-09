#!/usr/bin/env python3
"""
Aurora-X WASM Installer
Sets up local Pyodide-based WASM runtime for browser execution.
"""

import os
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path
from typing import Dict, Optional


class WASMInstaller:
    """WASM platform installer for Aurora-X"""
    
    def __init__(self, install_dir: Optional[str] = None):
        self.installers_dir = Path(__file__).parent
        self.pyodide_dir = self.installers_dir / "pyodide"
        self.start_script = self.installers_dir / "start-wasm-host.sh"
        
    def detect_environment(self) -> Dict[str, bool]:
        """Detect available WASM development tools"""
        return {
            "python_available": self._check_python(),
            "http_server_available": self._check_http_server(),
            "pyodide_present": self._check_pyodide(),
        }
    
    def _check_python(self) -> bool:
        """Check if Python is available"""
        return sys.executable is not None
    
    def _check_http_server(self) -> bool:
        """Check if Python HTTP server module is available"""
        try:
            import http.server
            return True
        except ImportError:
            return False
    
    def _check_pyodide(self) -> bool:
        """Check if Pyodide assets are present"""
        required_files = [
            "pyodide.js",
            "pyodide.wasm",
            "python_stdlib.zip"
        ]
        
        for file in required_files:
            if not (self.pyodide_dir / file).exists():
                return False
        return True
    
    def download_pyodide(self, version: str = "0.24.1") -> bool:
        """Download Pyodide distribution"""
        print(f"[INFO] Downloading Pyodide {version}...")
        
        pyodide_url = f"https://github.com/pyodide/pyodide/releases/download/{version}/pyodide-{version}.tar.bz2"
        
        self.pyodide_dir.mkdir(parents=True, exist_ok=True)
        archive_path = self.pyodide_dir / f"pyodide-{version}.tar.bz2"
        
        try:
            # Download archive
            print(f"[INFO] Downloading from {pyodide_url}...")
            urllib.request.urlretrieve(pyodide_url, archive_path)
            
            # Extract archive
            print("[INFO] Extracting Pyodide...")
            import tarfile
            with tarfile.open(archive_path, "r:bz2") as tar:
                # Extract only the files we need
                members = [
                    m for m in tar.getmembers()
                    if m.name in [
                        f"pyodide-{version}/pyodide.js",
                        f"pyodide-{version}/pyodide.wasm",
                        f"pyodide-{version}/python_stdlib.zip"
                    ]
                ]
                
                for member in members:
                    member.name = os.path.basename(member.name)
                    tar.extract(member, self.pyodide_dir)
            
            # Clean up archive
            archive_path.unlink()
            
            print("[OK] Pyodide downloaded and extracted")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to download Pyodide: {e}")
            print("[INFO] You can manually download Pyodide from:")
            print("       https://github.com/pyodide/pyodide/releases")
            print(f"       And place files in: {self.pyodide_dir}")
            return False
    
    def setup_pyodide(self, auto_download: bool = False) -> bool:
        """Set up Pyodide runtime"""
        if self._check_pyodide():
            print("[OK] Pyodide assets already present")
            return True
        
        if auto_download:
            return self.download_pyodide()
        else:
            print("[INFO] Pyodide assets not found")
            print(f"[INFO] Place the following files in {self.pyodide_dir}:")
            print("  - pyodide.js")
            print("  - pyodide.wasm")
            print("  - python_stdlib.zip")
            print("\n[INFO] Or run with --download to auto-download")
            return False
    
    def start_server(self, port: int = 8123) -> bool:
        """Start local HTTP server for WASM runtime"""
        if not self._check_pyodide():
            print("[ERROR] Pyodide assets not found. Run setup first.")
            return False
        
        if self.start_script.exists():
            try:
                os.chmod(self.start_script, 0o755)
                print(f"[INFO] Starting WASM server on port {port}...")
                print(f"[INFO] Open http://localhost:{port} in your browser")
                print("[INFO] Press Ctrl+C to stop")
                
                # Update port in script if different
                if port != 8123:
                    content = self.start_script.read_text()
                    content = content.replace("8123", str(port))
                    self.start_script.write_text(content)
                
                # Run the server
                subprocess.run(
                    ["bash", str(self.start_script)],
                    cwd=str(self.installers_dir)
                )
                return True
                
            except KeyboardInterrupt:
                print("\n[INFO] Server stopped")
                return True
            except Exception as e:
                print(f"[ERROR] Failed to start server: {e}")
                return False
        else:
            # Fallback: use Python's built-in server
            try:
                import http.server
                import socketserver
                
                os.chdir(self.installers_dir)
                handler = http.server.SimpleHTTPRequestHandler
                httpd = socketserver.TCPServer(("", port), handler)
                
                print(f"[INFO] Starting HTTP server on port {port}...")
                print(f"[INFO] Open http://localhost:{port} in your browser")
                print("[INFO] Press Ctrl+C to stop")
                
                httpd.serve_forever()
                return True
                
            except KeyboardInterrupt:
                print("\n[INFO] Server stopped")
                return True
            except Exception as e:
                print(f"[ERROR] Failed to start server: {e}")
                return False
    
    def install(self, download_pyodide: bool = False) -> bool:
        """Set up WASM runtime"""
        return self.setup_pyodide(auto_download=download_pyodide)


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Aurora-X WASM Installer")
    parser.add_argument(
        "action",
        choices=["setup", "start", "check"],
        nargs="?",
        default="check",
        help="Action to perform (default: check)"
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Auto-download Pyodide if not present"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8123,
        help="HTTP server port (default: 8123)"
    )
    
    args = parser.parse_args()
    
    installer = WASMInstaller()
    
    if args.action == "check":
        env = installer.detect_environment()
        print("WASM Runtime Environment:")
        print(f"  Python available: {env['python_available']}")
        print(f"  HTTP server available: {env['http_server_available']}")
        print(f"  Pyodide present: {env['pyodide_present']}")
        return 0
    
    elif args.action == "setup":
        success = installer.install(download_pyodide=args.download)
        return 0 if success else 1
    
    elif args.action == "start":
        success = installer.start_server(port=args.port)
        return 0 if success else 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
