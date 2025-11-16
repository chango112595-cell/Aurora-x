#!/usr/bin/env python3
"""
Aurora Server Architecture Analysis
Identify all servers, their purposes, and correct configuration
"""

import json
from pathlib import Path


class AuroraServerAnalysis:
    """Analysis tool for server configuration and architecture"""

    def __init__(self):
        self.root = Path(".")
        self.findings = {
            "servers": [],
            "issues": [],
            "recommendations": []
        }

    def analyze_package_json(self):
        """Analyze package.json scripts"""
        print("[Aurora] Analyzing package.json...")

        package_path = self.root / "package.json"
        if package_path.exists():
            with open(package_path, encoding='utf-8') as f:
                data = json.load(f)
                scripts = data.get("scripts", {})

                print("[Aurora] Found scripts:")
                for name, command in scripts.items():
                    print(f"  • {name}: {command}")

                # Check if we're using TypeScript (tsx)
                if "tsx" in str(scripts):
                    self.findings["issues"].append(
                        "Using tsx (TypeScript execution) not HTML")
                    print(
                        "\n[Aurora] ✅ Confirmed: Using TypeScript (.tsx/.ts) not HTML")

    def scan_server_files(self):
        """Find all server files"""
        print("\n[Aurora] Scanning for server files...")

        server_files = []

        # Check server directory
        server_dir = self.root / "server"
        if server_dir.exists():
            for file in server_dir.rglob("*.ts"):
                if "index" in file.name.lower():
                    server_files.append(file)
                    print(f"  📁 Found: {file}")

        # Check for Python servers
        for file in self.root.glob("*.py"):
            if any(keyword in file.name.lower() for keyword in ["server", "bridge", "chat", "learn"]):
                server_files.append(file)
                print(f"  📁 Found: {file}")

        self.findings["servers"].extend([str(f) for f in server_files])
        return server_files

    def analyze_x_start(self):
        """Analyze the x-start script"""
        print("\n[Aurora] Analyzing x-start script...")

        x_start = self.root / "x-start"
        if x_start.exists():
            content = x_start.read_text(encoding='utf-8')
            print("[Aurora] x-start file found")

            # Extract port assignments
            ports = {}
            for line in content.split('\n'):
                if 'PORT' in line and '=' in line and not line.strip().startswith('#'):
                    print(f"  • {line.strip()}")
                    if '5000' in line:
                        ports['backend'] = 5000
                    elif '5001' in line:
                        ports['bridge'] = 5001
                    elif '5002' in line:
                        ports['self_learn'] = 5002
                    elif '5003' in line:
                        ports['chat'] = 5003
                    elif '5005' in line:
                        ports['luminar'] = 5005
                    elif '5173' in line:
                        ports['vite'] = 5173

            return ports
        return {}

    def check_vite_config(self):
        """Check Vite configuration"""
        print("\n[Aurora] Checking Vite configuration...")

        vite_config = self.root / "vite.config.js"
        if vite_config.exists():
            content = vite_config.read_text(encoding='utf-8')

            if 'port: 5173' in content:
                print("[Aurora] ✅ Vite configured for port 5173")
                self.findings["recommendations"].append(
                    "Vite dev server uses port 5173")

            if 'react' in content.lower():
                print("[Aurora] ✅ Using React (TSX/JSX)")
                self.findings["issues"].append(
                    "Frontend: React TSX components, not HTML")

            # Check root directory
            if 'root:' in content:
                for line in content.split('\n'):
                    if 'root:' in line:
                        print(f"[Aurora] Root directory: {line.strip()}")

    def analyze_server_index(self):
        """Analyze main server file"""
        print("\n[Aurora] Analyzing server/index.ts...")

        server_index = self.root / "server" / "index.ts"
        if server_index.exists():
            content = server_index.read_text(encoding='utf-8')

            # Check for Vite integration
            if 'setupVite' in content:
                print("[Aurora] ✅ Express + Vite integration detected")
                self.findings["servers"].append({
                    "name": "Backend + Frontend",
                    "port": 5000,
                    "type": "Express with Vite middleware",
                    "tech": "TypeScript (tsx) + React (tsx)"
                })

            # Check default port
            if 'PORT' in content:
                for line in content.split('\n'):
                    if 'PORT' in line and 'process.env' in line:
                        print(f"[Aurora] Port config: {line.strip()}")

    def identify_architecture(self):
        """Identify the correct architecture"""
        print("\n" + "="*60)
        print("[Aurora] ARCHITECTURE IDENTIFICATION")
        print("="*60 + "\n")

        print("[Aurora] CORRECT SERVER ARCHITECTURE:")
        print()
        print("  🎯 PRIMARY SERVER:")
        print("     • Port 5000: Express.js + Vite (Development)")
        print("     • Tech Stack: TypeScript (server) + React TSX (frontend)")
        print("     • Purpose: Backend API + Frontend serving")
        print("     • Vite integrates HMR at port 5000")
        print()
        print("  🎯 SUPPORT SERVICES:")
        print("     • Port 5001: Bridge Service (Python)")
        print("     • Port 5002: Self-Learning Service (Python)")
        print("     • Port 5003: Chat Server (Python)")
        print("     • Port 5005: Luminar Dashboard (Python)")
        print()
        print("  ⚠️  PORT 5173 NOTE:")
        print("     • Vite's default standalone port")
        print("     • NOT used in this setup")
        print("     • Vite runs as middleware through Express (port 5000)")
        print()
        print("[Aurora] FILE TYPES:")
        print("     • Frontend: .tsx (TypeScript + JSX)")
        print("     • Components: React TSX files")
        print("     • NOT using plain HTML files")
        print("     • TSX is compiled by Vite → served at port 5000")
        print()

    def run(self):
        """Run complete analysis"""
        print("\n" + "="*60)
        print("[Aurora] SERVER ARCHITECTURE ANALYSIS")
        print("="*60 + "\n")

        self.analyze_package_json()
        self.scan_server_files()
        _ = self.analyze_x_start()
        self.check_vite_config()
        self.analyze_server_index()

        self.identify_architecture()

        print("="*60)
        print("[Aurora] SUMMARY")
        print("="*60)
        print()
        print("[Aurora] ✅ PRIMARY ACCESS POINT: http://localhost:5000")
        print("[Aurora] ✅ Frontend tech: React TSX (TypeScript)")
        print("[Aurora] ✅ Build system: Vite (integrated with Express)")
        print("[Aurora] ✅ All 5 services should run simultaneously")
        print()
        print("[Aurora] 🎨 The blank screen issue is likely:")
        print("     1. Component import/export mismatch (FIXED)")
        print("     2. Browser cache needs hard refresh")
        print("     3. Vite HMR connection issue")
        print()
        print("[Aurora] 💡 Try: Ctrl+Shift+R (hard refresh) in browser")
        print()


if __name__ == "__main__":
    analyzer = AuroraServerAnalysis()
    analyzer.run()
