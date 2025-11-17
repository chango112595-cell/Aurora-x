#!/usr/bin/env python3
"""
Aurora Deep System Investigation
Using all autonomous skills to diagnose the actual problem
"""

import json
import socket
import subprocess
from pathlib import Path


class AuroraDeepInvestigation:
    def __init__(self):
        self.root = Path(".")
        self.issues = []
        self.facts = []

    def fact(self, message):
        """Record a fact"""
        print(f"[Aurora] 🔍 {message}")
        self.facts.append(message)

    def issue(self, message):
        """Record an issue"""
        print(f"[Aurora] ⚠️  {message}")
        self.issues.append(message)

    def check_what_is_actually_running(self):
        """Check what's ACTUALLY running right now"""
        print("\n" + "=" * 60)
        print("[Aurora] INVESTIGATING ACTUAL RUNNING PROCESSES")
        print("=" * 60 + "\n")

        try:
            # Check node processes
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    'Get-Process node -ErrorAction SilentlyContinue | Select-Object Id,Path,@{Name="Port";Expression={(Get-NetTCPConnection -OwningProcess $_.Id -ErrorAction SilentlyContinue).LocalPort}} | Format-Table -AutoSize',
                ],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            if result.stdout.strip():
                self.fact(f"Node processes found:\n{result.stdout}")
            else:
                self.issue("NO Node.js processes running!")
                self.issue("npm run dev is NOT running!")
        except Exception as e:
            self.issue(f"Cannot check node processes: {e}")

    def check_python_servers(self):
        """Check which Python servers are running"""
        print("\n[Aurora] Checking Python server processes...")

        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "Get-Process python* -ErrorAction SilentlyContinue | Select-Object Id,Path,CommandLine | Format-List",
                ],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            if result.stdout.strip():
                self.fact(f"Python processes:\n{result.stdout[:1000]}")
            else:
                self.issue("NO Python server processes found!")
        except Exception as e:
            self.issue(f"Cannot check Python processes: {e}")

    def check_port_listeners(self):
        """Check what's listening on each port"""
        print("\n[Aurora] Checking port listeners...")

        ports = [5000, 5001, 5002, 5003, 5005, 5173]

        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(("localhost", port))

            if result == 0:
                # Port is open - find what's using it
                try:
                    cmd_result = subprocess.run(
                        [
                            "powershell",
                            "-Command",
                            f"Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | Select-Object OwningProcess | ForEach-Object {{ Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue | Select-Object ProcessName,Path }}",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        check=False,
                    )
                    if cmd_result.stdout.strip():
                        self.fact(f"Port {port}: LISTENING - {cmd_result.stdout.strip()}")
                    else:
                        self.fact(f"Port {port}: LISTENING (process unknown)")
                except Exception:
                    self.fact(f"Port {port}: LISTENING")
            else:
                self.issue(f"Port {port}: NOT LISTENING")

            sock.close()

    def check_package_json_script(self):
        """Check what 'npm run dev' actually does"""
        print("\n[Aurora] Analyzing package.json dev script...")

        try:
            with open("package.json", encoding="utf-8") as f:
                data = json.load(f)
                dev_script = data.get("scripts", {}).get("dev", "")

                self.fact(f"Dev script: {dev_script}")

                if "tsx" in dev_script and "server/index.ts" in dev_script:
                    self.fact("Dev script should start TypeScript server")

                    # Check if server/index.ts exists
                    if Path("server/index.ts").exists():
                        self.fact("server/index.ts EXISTS")
                    else:
                        self.issue("server/index.ts MISSING!")
                else:
                    self.issue(f"Unexpected dev script format: {dev_script}")
        except Exception as e:
            self.issue(f"Cannot read package.json: {e}")

    def check_vite_setup(self):
        """Check if Vite is properly configured"""
        print("\n[Aurora] Checking Vite setup...")

        # Check server/vite.ts
        vite_setup = Path("server/vite.ts")
        if vite_setup.exists():
            self.fact("server/vite.ts EXISTS")
            content = vite_setup.read_text(encoding="utf-8")

            if "setupVite" in content:
                self.fact("setupVite function found")
            if "createServer" in content:
                self.fact("Vite createServer found")
        else:
            self.issue("server/vite.ts MISSING!")

        # Check vite.config
        if Path("vite.config.js").exists():
            self.fact("vite.config.js EXISTS")
        else:
            self.issue("vite.config.js MISSING!")

    def check_frontend_files(self):
        """Check if frontend files exist"""
        print("\n[Aurora] Checking frontend structure...")

        client_src = Path("client/src")

        if not client_src.exists():
            self.issue("client/src directory MISSING!")
            return

        # Check critical files
        critical_files = ["client/src/main.tsx", "client/src/App.tsx", "client/src/index.css", "client/index.html"]

        for file_path in critical_files:
            if Path(file_path).exists():
                self.fact(f"{file_path} EXISTS")
            else:
                self.issue(f"{file_path} MISSING!")

    def check_browser_console_simulation(self):
        """Try to fetch from port 5000 and see what we get"""
        print("\n[Aurora] Simulating browser request to port 5000...")

        try:
            import urllib.request

            with urllib.request.urlopen("http://localhost:5000", timeout=5) as response:
                content = response.read().decode("utf-8")

                if "<!DOCTYPE html>" in content or "<html" in content:
                    self.fact("Port 5000 IS serving HTML!")

                    # Check for common issues
                    if "runtime-error" in content:
                        self.issue("Runtime error plugin detected in HTML")

                    if '<script type="module"' in content:
                        self.fact("Vite module script tags found")

                    if 'src="/src/main.tsx"' in content or 'src="/@' in content:
                        self.fact("Vite entry point found in HTML")
                    else:
                        self.issue("Vite entry point NOT found in HTML!")

                    # Save snippet for analysis
                    snippet = content[:2000]
                    print("\n[Aurora] HTML snippet from port 5000:")
                    print("-" * 60)
                    print(snippet)
                    print("-" * 60)

                else:
                    self.issue("Port 5000 NOT serving HTML!")

        except Exception as e:
            self.issue(f"Cannot fetch from port 5000: {e}")

    def check_component_imports(self):
        """Check if our new components have issues"""
        print("\n[Aurora] Checking component structure...")

        app_tsx = Path("client/src/App.tsx")
        if app_tsx.exists():
            content = app_tsx.read_text(encoding="utf-8")

            # Check imports
            imports = ["AuroraFuturisticLayout", "Dashboard", "ChatPage", "Tasks", "Tiers", "Intelligence"]

            for imp in imports:
                if f"import {imp}" in content or f"import.*{imp}" in content:
                    self.fact(f"App.tsx imports {imp}")
                else:
                    self.issue(f"App.tsx MISSING import: {imp}")

    def analyze_x_start_execution(self):
        """Check if x-start actually worked"""
        print("\n[Aurora] Analyzing x-start execution...")

        # The fact that we can check ports means x-start ran
        # But did all services start?

        expected_services = {
            5000: "Backend+Frontend (npm)",
            5001: "Bridge (Python)",
            5002: "Self-Learn (Python)",
            5003: "Chat (Python)",
            5005: "Luminar (Python)",
        }

        print("\n[Aurora] Expected vs Actual:")
        for port, service in expected_services.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            is_running = sock.connect_ex(("localhost", port)) == 0
            sock.close()

            if is_running:
                self.fact(f"✓ Port {port} ({service}) - RUNNING")
            else:
                self.issue(f"✗ Port {port} ({service}) - NOT RUNNING")

    def run_diagnosis(self):
        """Run complete diagnosis"""
        print("\n" + "=" * 60)
        print("[Aurora] AUTONOMOUS DEEP SYSTEM INVESTIGATION")
        print("[Aurora] Using all diagnostic skills")
        print("=" * 60)

        self.check_what_is_actually_running()
        self.check_python_servers()
        self.check_port_listeners()
        self.analyze_x_start_execution()
        self.check_package_json_script()
        self.check_vite_setup()
        self.check_frontend_files()
        self.check_browser_console_simulation()
        self.check_component_imports()

        # Final analysis
        print("\n" + "=" * 60)
        print("[Aurora] AUTONOMOUS ANALYSIS COMPLETE")
        print("=" * 60 + "\n")

        print(f"[Aurora] Facts discovered: {len(self.facts)}")
        print(f"[Aurora] Issues found: {len(self.issues)}")

        if self.issues:
            print("\n[Aurora] ⚠️  CRITICAL ISSUES:")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")

        print("\n[Aurora] 🎯 ROOT CAUSE HYPOTHESIS:")

        # Analyze the evidence
        has_port_5000 = any("Port 5000" in f and "LISTENING" in f for f in self.facts)
        has_html = any("serving HTML" in f for f in self.facts)
        has_vite_entry = any("Vite entry point found" in f for f in self.facts)

        if not has_port_5000:
            print("  → Port 5000 is NOT running")
            print("  → npm run dev failed to start or crashed")
            print("  → SOLUTION: Check if Node.js process died after x-start")
        elif not has_html:
            print("  → Port 5000 is open but not serving HTML")
            print("  → Server might be running but Vite not integrated")
            print("  → SOLUTION: Check server/vite.ts integration")
        elif not has_vite_entry:
            print("  → HTML is served but Vite entry point missing")
            print("  → Frontend code not being loaded")
            print("  → SOLUTION: Check client/index.html and main.tsx")
        else:
            print("  → All systems appear functional")
            print("  → Issue is likely in React component rendering")
            print("  → SOLUTION: Check browser console for JS errors")

        print("\n[Aurora] 💡 NEXT STEPS:")
        print("  1. Check browser console (F12) for JavaScript errors")
        print("  2. Verify all node processes are still running")
        print("  3. Check Vite HMR connection in browser console")
        print("  4. Test if specific component is failing to render")
        print()


if __name__ == "__main__":
    aurora = AuroraDeepInvestigation()
    aurora.run_diagnosis()
