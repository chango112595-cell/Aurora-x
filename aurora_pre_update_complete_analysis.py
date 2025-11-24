#!/usr/bin/env python3
"""
AURORA PRE-UPDATE COMPLETE ANALYSIS
Comprehensive analysis of EVERYTHING before updating entire system:
- Frontend (React/TypeScript)
- Backend (Python/Flask)
- All ports and services
- All orchestration systems
- All autonomous systems
- Database connections
- API endpoints
- Configuration files
- Dependencies
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from collections import defaultdict
import re


class AuroraPreUpdateAnalyzer:
    def __init__(self):
        self.root = Path(__file__).parent
        self.analysis = {
            'frontend': {},
            'backend': {},
            'ports': {},
            'services': {},
            'orchestrators': {},
            'autonomous_systems': {},
            'dependencies': {},
            'configuration': {},
            'api_endpoints': {},
            'issues_found': [],
            'recommendations': [],
            'update_plan': []
        }

    def analyze_frontend(self):
        """Analyze entire frontend structure"""
        print("\n[EMOJI] ANALYZING FRONTEND...")
        print("=" * 70)

        frontend_paths = [
            self.root / "frontend",
            self.root / "src",
            self.root / "aurora_x" / "frontend"
        ]

        frontend_dir = None
        for path in frontend_paths:
            if path.exists():
                frontend_dir = path
                break

        if not frontend_dir:
            print("  [WARN] Frontend directory not found")
            self.analysis['issues_found'].append(
                "Frontend directory not found")
            return

        print(f"  [EMOJI] Frontend location: {frontend_dir.relative_to(self.root)}")

        # Check package.json
        package_json = self.root / "package.json"
        if package_json.exists():
            with open(package_json, encoding='utf-8') as f:
                pkg_data = json.load(f)
                self.analysis['frontend']['package'] = pkg_data

                # Check dependencies
                deps = pkg_data.get('dependencies', {})
                dev_deps = pkg_data.get('devDependencies', {})

                print(f"  [PACKAGE] Dependencies: {len(deps)}")
                print(f"  [EMOJI] DevDependencies: {len(dev_deps)}")

                # Check for React/TypeScript
                if 'react' in deps:
                    print(f"  ⚛️  React: {deps['react']}")
                if 'typescript' in dev_deps:
                    print(f"  [EMOJI] TypeScript: {dev_deps['typescript']}")
                if 'vite' in dev_deps:
                    print(f"  [POWER] Vite: {dev_deps['vite']}")

                # Check scripts
                scripts = pkg_data.get('scripts', {})
                print(f"  [EMOJI] Scripts: {', '.join(scripts.keys())}")

                self.analysis['frontend']['dependencies'] = deps
                self.analysis['frontend']['scripts'] = scripts

        # Check TypeScript config
        tsconfig = self.root / "tsconfig.json"
        if tsconfig.exists():
            print("  [OK] TypeScript config found")
            with open(tsconfig, encoding='utf-8') as f:
                ts_data = json.load(f)
                self.analysis['frontend']['typescript'] = ts_data

        # Check Vite config
        vite_configs = ["vite.config.ts", "vite.config.js"]
        for config_name in vite_configs:
            vite_config = self.root / config_name
            if vite_config.exists():
                print(f"  [POWER] Vite config: {config_name}")
                content = vite_config.read_text(encoding='utf-8')
                # Extract port from Vite config
                port_match = re.search(r'port:\s*(\d+)', content)
                if port_match:
                    port = int(port_match.group(1))
                    print(f"     Port configured: {port}")
                    self.analysis['frontend']['vite_port'] = port
                break

        # Scan frontend files
        extensions = ['.tsx', '.ts', '.jsx', '.js']
        frontend_files = []
        for ext in extensions:
            frontend_files.extend(frontend_dir.rglob(f'*{ext}'))

        print(f"  [EMOJI] Frontend files: {len(frontend_files)}")

        # Check for main entry points
        entry_points = ['main.tsx', 'main.ts',
                        'index.tsx', 'index.ts', 'App.tsx', 'App.ts']
        found_entries = []
        for entry in entry_points:
            if (frontend_dir / entry).exists() or (frontend_dir / 'src' / entry).exists():
                found_entries.append(entry)

        if found_entries:
            print(f"  [EMOJI] Entry points: {', '.join(found_entries)}")

        self.analysis['frontend']['file_count'] = len(frontend_files)
        self.analysis['frontend']['entry_points'] = found_entries

    def analyze_backend(self):
        """Analyze entire backend structure"""
        print("\n[EMOJI] ANALYZING BACKEND...")
        print("=" * 70)

        # Find Python files
        python_files = list(self.root.rglob('*.py'))
        python_files = [f for f in python_files if 'venv' not in str(
            f) and 'node_modules' not in str(f)]

        print(f"  [EMOJI] Python files: {len(python_files)}")

        # Find Flask/FastAPI applications
        backend_servers = []
        for py_file in python_files:
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                if 'Flask' in content and 'app = Flask' in content:
                    backend_servers.append({
                        'file': str(py_file.relative_to(self.root)),
                        'framework': 'Flask',
                        'type': 'main_app'
                    })
                elif 'FastAPI' in content and 'app = FastAPI' in content:
                    backend_servers.append({
                        'file': str(py_file.relative_to(self.root)),
                        'framework': 'FastAPI',
                        'type': 'main_app'
                    })
            except:
                continue

        print(f"  [WEB] Backend servers found: {len(backend_servers)}")
        for server in backend_servers:
            print(f"     • {server['file']} ({server['framework']})")

        self.analysis['backend']['servers'] = backend_servers
        self.analysis['backend']['file_count'] = len(python_files)

        # Check requirements
        req_files = ['requirements.txt', 'pyproject.toml', 'setup.py']
        for req_file in req_files:
            req_path = self.root / req_file
            if req_path.exists():
                print(f"  [EMOJI] Dependencies: {req_file}")
                if req_file == 'requirements.txt':
                    deps = req_path.read_text(
                        encoding='utf-8').strip().split('\n')
                    deps = [d.strip() for d in deps if d.strip()
                            and not d.startswith('#')]
                    print(f"     {len(deps)} packages")
                    self.analysis['backend']['dependencies'] = deps

        # Check for aurora_core
        aurora_core_paths = [
            self.root / "aurora_core.py",
            self.root / "tools" / "aurora_core.py"
        ]

        for core_path in aurora_core_paths:
            if core_path.exists():
                print(f"  [BRAIN] Aurora Core: {core_path.relative_to(self.root)}")
                size = core_path.stat().st_size / 1024
                print(f"     Size: {size:.1f}KB")
                self.analysis['backend']['aurora_core'] = {
                    'path': str(core_path.relative_to(self.root)),
                    'size': size
                }
                break

    def analyze_ports(self):
        """Analyze all port configurations"""
        print("\n[EMOJI] ANALYZING PORTS...")
        print("=" * 70)

        port_configs = defaultdict(list)

        # Check x-start
        x_start = self.root / "x-start"
        if x_start.exists():
            content = x_start.read_text(encoding='utf-8')
            ports = re.findall(r'(?:port|Port)\s*[=:]\s*(\d+)', content)
            ports.extend(re.findall(
                r'(?:localhost|127\.0\.0\.1):(\d+)', content))

            unique_ports = sorted(set(int(p) for p in ports))
            print(f"  [EMOJI] x-start configured ports: {unique_ports}")

            for port in unique_ports:
                port_configs[port].append('x-start')

            self.analysis['ports']['x_start'] = unique_ports

        # Check vite config
        vite_port = self.analysis['frontend'].get('vite_port')
        if vite_port:
            port_configs[vite_port].append('vite.config')

        # Check Python files for port definitions
        for py_file in self.root.rglob('*.py'):
            if 'venv' in str(py_file) or 'node_modules' in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                # Look for port definitions
                port_patterns = [
                    r'port\s*=\s*(\d+)',
                    r'PORT\s*=\s*(\d+)',
                    r'\.run\([^)]*port\s*=\s*(\d+)',
                    r'--port["\s]+(\d+)',
                ]

                for pattern in port_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for port in matches:
                        port_num = int(port)
                        if 3000 <= port_num <= 9999:  # Reasonable port range
                            port_configs[port_num].append(
                                str(py_file.relative_to(self.root)))
            except:
                continue

        # Consolidate and report
        print(f"\n  [DATA] PORT CONFIGURATION MAP:")
        for port in sorted(port_configs.keys()):
            sources = port_configs[port]
            print(f"     Port {port}: {len(sources)} sources")
            for source in sources[:3]:  # Show first 3 sources
                print(f"        - {source}")
            if len(sources) > 3:
                print(f"        ... and {len(sources) - 3} more")

        self.analysis['ports']['all_ports'] = dict(port_configs)

        # Check for port conflicts
        conflicts = {port: sources for port,
                     sources in port_configs.items() if len(sources) > 2}
        if conflicts:
            print(f"\n  [WARN]  Potential port conflicts: {len(conflicts)}")
            for port, sources in conflicts.items():
                print(
                    f"     Port {port}: {len(sources)} different configurations")
                self.analysis['issues_found'].append(
                    f"Port {port} has {len(sources)} different configurations")

    def analyze_services(self):
        """Analyze all service definitions"""
        print("\n⚙️ ANALYZING SERVICES...")
        print("=" * 70)

        services = []

        # Check x-start for service list
        x_start = self.root / "x-start"
        if x_start.exists():
            content = x_start.read_text(encoding='utf-8')

            # Extract service start commands
            service_patterns = [
                r'print\(".*Starting ([^"]+)"',
                r'# \d+\. Start ([^\n]+)',
            ]

            for pattern in service_patterns:
                matches = re.findall(pattern, content)
                services.extend(matches)

        services = list(set(services))
        print(f"  [EMOJI] Services defined: {len(services)}")
        for service in services:
            print(f"     • {service}")

        self.analysis['services']['list'] = services
        self.analysis['services']['count'] = len(services)

    def analyze_orchestrators(self):
        """Quick check of orchestration systems"""
        print("\n[TARGET] ANALYZING ORCHESTRATION SYSTEMS...")
        print("=" * 70)

        # Key orchestrators
        key_orchestrators = [
            'tools/ultimate_api_manager.py',
            'tools/luminar_nexus.py',
            'tools/luminar_nexus_v2.py',
            'aurora_autonomous_monitor.py',
            'activate_aurora_core.py'
        ]

        found_orchestrators = []
        for orch in key_orchestrators:
            orch_path = self.root / orch
            if orch_path.exists():
                size = orch_path.stat().st_size / 1024
                found_orchestrators.append({
                    'file': orch,
                    'size': size,
                    'exists': True
                })
                print(f"  [OK] {orch} ({size:.1f}KB)")
            else:
                print(f"  [ERROR] {orch} (not found)")
                self.analysis['issues_found'].append(
                    f"Orchestrator not found: {orch}")

        self.analysis['orchestrators']['key_systems'] = found_orchestrators

    def analyze_configuration(self):
        """Analyze configuration files"""
        print("\n⚙️ ANALYZING CONFIGURATION FILES...")
        print("=" * 70)

        config_files = [
            'package.json',
            'tsconfig.json',
            'vite.config.ts',
            'vite.config.js',
            '.env',
            '.env.local',
            'requirements.txt',
            'pyproject.toml',
            'alembic.ini'
        ]

        found_configs = []
        for config in config_files:
            config_path = self.root / config
            if config_path.exists():
                found_configs.append(config)
                print(f"  [OK] {config}")
            else:
                print(f"  [WARN]  {config} (not found)")

        self.analysis['configuration']['files'] = found_configs

    def check_current_state(self):
        """Check what's currently running"""
        print("\n[SCAN] CHECKING CURRENT STATE...")
        print("=" * 70)

        # Check if services are running on ports
        import socket

        ports_to_check = [5000, 5001, 5002, 5003, 5005, 5173]
        running_services = []

        for port in ports_to_check:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            try:
                result = sock.connect_ex(('127.0.0.1', port))
                if result == 0:
                    running_services.append(port)
                    print(f"  [OK] Port {port}: RUNNING")
                else:
                    print(f"  [WARN]  Port {port}: not running")
            except:
                print(f"  [ERROR] Port {port}: error checking")
            finally:
                sock.close()

        self.analysis['services']['running'] = running_services
        self.analysis['services']['expected'] = ports_to_check

    def generate_update_plan(self):
        """Generate comprehensive update plan"""
        print("\n" + "=" * 70)
        print("[EMOJI] GENERATING UPDATE PLAN")
        print("=" * 70)

        # Frontend updates
        print("\n1️⃣  FRONTEND UPDATES:")
        frontend_updates = []

        if self.analysis['frontend'].get('dependencies'):
            print("  • Update npm dependencies")
            frontend_updates.append("npm update")

        if self.analysis['frontend'].get('vite_port'):
            print("  • Verify Vite port configuration")
            frontend_updates.append("verify_vite_config")

        if self.analysis['frontend'].get('entry_points'):
            print("  • Check entry point integrity")
            frontend_updates.append("verify_entry_points")

        self.analysis['update_plan'].append({
            'category': 'frontend',
            'updates': frontend_updates
        })

        # Backend updates
        print("\n2️⃣  BACKEND UPDATES:")
        backend_updates = []

        if self.analysis['backend'].get('dependencies'):
            print("  • Update Python dependencies")
            backend_updates.append("pip_update")

        if self.analysis['backend'].get('aurora_core'):
            print("  • Verify Aurora Core integration")
            backend_updates.append("verify_aurora_core")

        for server in self.analysis['backend'].get('servers', []):
            print(f"  • Verify {server['file']}")
            backend_updates.append(f"verify_{server['file']}")

        self.analysis['update_plan'].append({
            'category': 'backend',
            'updates': backend_updates
        })

        # Port configuration updates
        print("\n3️⃣  PORT CONFIGURATION:")
        port_updates = []

        if self.analysis['issues_found']:
            print("  • Resolve port conflicts")
            port_updates.append("resolve_port_conflicts")

        print("  • Standardize port configuration")
        port_updates.append("standardize_ports")

        self.analysis['update_plan'].append({
            'category': 'ports',
            'updates': port_updates
        })

        # Orchestration updates
        print("\n4️⃣  ORCHESTRATION SYSTEMS:")
        orch_updates = []

        print("  • Verify Ultimate API Manager")
        orch_updates.append("verify_ultimate_api_manager")

        print("  • Verify Luminar Nexus")
        orch_updates.append("verify_luminar_nexus")

        print("  • Activate all autonomous systems")
        orch_updates.append("activate_autonomous_systems")

        self.analysis['update_plan'].append({
            'category': 'orchestration',
            'updates': orch_updates
        })

        # Recommendations
        print("\n" + "=" * 70)
        print("[IDEA] RECOMMENDATIONS")
        print("=" * 70)

        recommendations = [
            "1. Stop all running services before updating",
            "2. Backup current configuration files",
            "3. Update frontend dependencies (npm)",
            "4. Update backend dependencies (pip)",
            "5. Verify all port configurations are consistent",
            "6. Test each service individually after update",
            "7. Run full system test with x-start",
            "8. Verify orchestration systems are coordinating",
        ]

        for rec in recommendations:
            print(f"  {rec}")
            self.analysis['recommendations'].append(rec)

    def save_analysis(self):
        """Save complete analysis to JSON"""
        output_file = self.root / "AURORA_PRE_UPDATE_ANALYSIS.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis, f, indent=2)

        print(f"\n[EMOJI] Complete analysis saved: {output_file}")

        # Save summary
        summary_file = self.root / "AURORA_PRE_UPDATE_SUMMARY.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("AURORA PRE-UPDATE ANALYSIS SUMMARY\n")
            f.write("=" * 70 + "\n\n")

            f.write(
                f"Frontend Files: {self.analysis['frontend'].get('file_count', 0)}\n")
            f.write(
                f"Backend Files: {self.analysis['backend'].get('file_count', 0)}\n")
            f.write(
                f"Configured Ports: {len(self.analysis['ports'].get('all_ports', {}))}\n")
            f.write(f"Services: {self.analysis['services'].get('count', 0)}\n")
            f.write(
                f"Running Services: {len(self.analysis['services'].get('running', []))}\n")
            f.write(f"Issues Found: {len(self.analysis['issues_found'])}\n\n")

            if self.analysis['issues_found']:
                f.write("ISSUES:\n")
                for issue in self.analysis['issues_found']:
                    f.write(f"  - {issue}\n")
                f.write("\n")

            f.write("RECOMMENDATIONS:\n")
            for rec in self.analysis['recommendations']:
                f.write(f"  {rec}\n")

        print(f"[EMOJI] Summary saved: {summary_file}")

    def run_complete_analysis(self):
        """Run all analysis steps"""
        print("=" * 70)
        print("[STAR] AURORA PRE-UPDATE COMPLETE ANALYSIS")
        print("=" * 70)
        print("\nAnalyzing EVERYTHING before system update...\n")

        self.analyze_frontend()
        self.analyze_backend()
        self.analyze_ports()
        self.analyze_services()
        self.analyze_orchestrators()
        self.analyze_configuration()
        self.check_current_state()
        self.generate_update_plan()
        self.save_analysis()

        print("\n" + "=" * 70)
        print("[OK] PRE-UPDATE ANALYSIS COMPLETE")
        print("=" * 70)
        print("\n[TARGET] Aurora is ready to update the entire system")
        print("   All configurations analyzed and documented")
        print("   Update plan generated and saved")
        print("\n[EMOJI] Review these files before proceeding:")
        print("   • AURORA_PRE_UPDATE_ANALYSIS.json (detailed)")
        print("   • AURORA_PRE_UPDATE_SUMMARY.txt (summary)")

        return self.analysis


if __name__ == '__main__':
    analyzer = AuroraPreUpdateAnalyzer()
    analysis = analyzer.run_complete_analysis()
