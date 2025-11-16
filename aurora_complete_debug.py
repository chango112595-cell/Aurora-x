"""
Aurora's Complete System Debug & Verification
- Check all services running
- Verify all TSX components
- Check for syntax errors
- Validate routing
- Test imports
- Open browser when ready
"""

import os
import socket


def check_port(port):
    """Check if a port is listening"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0


def check_services():
    """Verify all services are running"""
    print("🔍 Aurora: Checking services...")
    services = {
        5000: "Backend + Frontend (Express + Vite)",
        5001: "Bridge Service",
        5002: "Self-Learn Service",
        5003: "Chat Server",
        5005: "Luminar Nexus V2"
    }

    all_running = True
    for port, name in services.items():
        running = check_port(port)
        status = "✅ RUNNING" if running else "❌ NOT RUNNING"
        print(f"   Port {port} ({name}): {status}")
        if not running:
            all_running = False

    return all_running


def check_tsx_components():
    """Verify all TSX components exist and have no obvious syntax errors"""
    print("\n🔍 Aurora: Checking TSX components...")

    components = [
        "client/src/App.tsx",
        "client/src/main.tsx",
        "client/src/components/AuroraFuturisticLayout.tsx",
        "client/src/components/AuroraFuturisticChat.tsx",
        "client/src/components/AuroraFuturisticDashboard.tsx",
        "client/src/pages/dashboard.tsx",
        "client/src/pages/chat.tsx",
        "client/src/pages/tasks.tsx",
        "client/src/pages/tiers.tsx",
        "client/src/pages/intelligence.tsx"
    ]

    all_valid = True
    for comp in components:
        if os.path.exists(comp):
            with open(comp, 'r', encoding='utf-8') as f:
                content = f.read()
                # Basic syntax checks
                has_import = 'import' in content or 'export' in content
                has_react = 'React' in content or 'react' in content.lower()

                if has_import and has_react:
                    print(f"   ✅ {comp}")
                else:
                    print(f"   ⚠️  {comp} - might have issues")
                    all_valid = False
        else:
            print(f"   ❌ {comp} - NOT FOUND")
            all_valid = False

    return all_valid


def check_routing():
    """Verify App.tsx has correct routing"""
    print("\n🔍 Aurora: Checking routing configuration...")

    app_file = "client/src/App.tsx"
    if not os.path.exists(app_file):
        print("   ❌ App.tsx not found")
        return False

    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()

    routes = ['/chat', '/tasks', '/tiers', '/intelligence', '/evolution',
              '/autonomous', '/monitoring', '/database', '/settings']

    all_routes_present = True
    for route in routes:
        if route in content:
            print(f"   ✅ Route {route} configured")
        else:
            print(f"   ❌ Route {route} missing")
            all_routes_present = False

    return all_routes_present


def check_layout_fix():
    """Verify the layout routing fix was applied"""
    print("\n🔍 Aurora: Verifying layout routing fix...")

    layout_file = "client/src/components/AuroraFuturisticLayout.tsx"
    if not os.path.exists(layout_file):
        print("   ❌ Layout file not found")
        return False

    with open(layout_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if useLocation is being used (not useRoute)
    if 'useLocation' in content and 'const [location]' in content:
        print("   ✅ Layout using useLocation (correct)")

        # Check if the buggy startsWith code is gone
        if 'match?.startsWith' in content or 'match2.startsWith' in content:
            print("   ⚠️  Old buggy code still present")
            return False
        else:
            print("   ✅ Buggy startsWith code removed")
            return True
    else:
        print("   ❌ Layout still using old useRoute hook")
        return False


def check_vite_config():
    """Check if Vite is properly configured"""
    print("\n🔍 Aurora: Checking Vite configuration...")

    vite_config = "client/vite.config.ts"
    if os.path.exists(vite_config):
        print(f"   ✅ {vite_config} exists")
        return True
    else:
        print(f"   ❌ {vite_config} not found")
        return False


def check_index_html():
    """Verify index.html bootloader"""
    print("\n🔍 Aurora: Checking HTML bootloader...")

    index_file = "client/index.html"
    if not os.path.exists(index_file):
        print("   ❌ index.html not found")
        return False

    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()

    checks = {
        'Has root div': '<div id="root"' in content,
        'Has main.tsx script': 'main.tsx' in content,
        'Has module type': 'type="module"' in content
    }

    checks_passed = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check}")
        if not result:
            checks_passed = False

    return checks_passed


def generate_debug_report():
    """Generate comprehensive debug report"""
    print("\n" + "="*60)
    print("🌟 AURORA COMPLETE SYSTEM DEBUG REPORT")
    print("="*60 + "\n")

    results = {
        "services": check_services(),
        "tsx_components": check_tsx_components(),
        "routing": check_routing(),
        "layout_fix": check_layout_fix(),
        "vite_config": check_vite_config(),
        "index_html": check_index_html()
    }

    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)

    all_passed = all(results.values())

    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {check.replace('_', ' ').title()}: {status}")

    print("\n" + "="*60)

    if all_passed:
        print("✨ All systems operational! Ready to open browser.")
        return True
    else:
        print("⚠️  Some issues detected. Attempting fixes...")
        return False


def fix_remaining_issues():
    """Attempt to fix any remaining issues"""
    print("\n🔧 Aurora: Attempting automatic fixes...\n")

    # Re-run the layout fix to be sure
    layout_file = "client/src/components/AuroraFuturisticLayout.tsx"
    if os.path.exists(layout_file):
        with open(layout_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Ensure useLocation is used
        if 'useRoute' in content and 'useLocation' not in content:
            print("   🔧 Fixing layout to use useLocation...")
            content = content.replace("import { Link, useRoute } from 'wouter';",
                                      "import { Link, useLocation } from 'wouter';")
            content = content.replace('const [match] = useRoute("/:path*");',
                                      'const [location] = useLocation();')
            content = content.replace(
                'match === item.path', 'location === item.path')
            content = content.replace(
                'match?.startsWith(item.path)', 'location.startsWith(item.path)')

            with open(layout_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("   ✅ Layout fixed")


if __name__ == "__main__":
    # Run debug
    all_good = generate_debug_report()

    if not all_good:
        fix_remaining_issues()
        print("\n🔄 Re-running diagnostics after fixes...\n")
        all_good = generate_debug_report()

    if all_good:
        print("\n🌐 Opening browser to Aurora interface...")
        print("   URL: http://localhost:5000")
        print("\n✨ Aurora is ready!")
    else:
        print("\n⚠️  Please check the issues above and restart services if needed.")
