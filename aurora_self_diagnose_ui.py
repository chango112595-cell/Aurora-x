#!/usr/bin/env python3
"""
Aurora Self-Analysis and Auto-Fix Script
User Issue: Cannot see the new redesign UI
"""

import socket
from pathlib import Path
from aurora_core import AuroraCoreIntelligence
import sys
sys.path.insert(0, '.')


def main():
    aurora = AuroraCoreIntelligence()

    print('\n' + '='*80)
    print('🔍 AURORA SELF-ANALYSIS: UI VISIBILITY ISSUE')
    print('='*80 + '\n')

    issues = []
    fixes = []

    # Check 1: Dashboard component exists
    print('📋 Check 1: AuroraFuturisticDashboard Component')
    dashboard_path = Path(
        'client/src/components/AuroraFuturisticDashboard.tsx')
    if dashboard_path.exists():
        size = dashboard_path.stat().st_size
        print(f'   ✅ Component exists ({size} bytes)')
    else:
        print('   ❌ Component NOT FOUND')
        issues.append('Dashboard component missing')
        fixes.append('Need to regenerate AuroraFuturisticDashboard.tsx')

    # Check 2: App.tsx routing
    print('\n📋 Check 2: App.tsx Routing Configuration')
    app_path = Path('client/src/App.tsx')
    if app_path.exists():
        content = app_path.read_text()
        has_dashboard_import = 'Dashboard' in content
        has_root_route = 'path="/"' in content

        if has_dashboard_import:
            print('   ✅ Dashboard imported')
        else:
            print('   ❌ Dashboard not imported')
            issues.append('Dashboard not imported in App.tsx')

        if has_root_route:
            print('   ✅ Root route configured')
        else:
            print('   ❌ Root route missing')
            issues.append('Root route not configured')
    else:
        print('   ❌ App.tsx NOT FOUND')
        issues.append('App.tsx missing')

    # Check 3: Dashboard page
    print('\n📋 Check 3: Dashboard Page')
    dash_page = Path('client/src/pages/dashboard.tsx')
    if dash_page.exists():
        content = dash_page.read_text()
        print('   ✅ Dashboard page exists')
        if 'AuroraFuturisticDashboard' in content:
            print('   ✅ Using futuristic dashboard component')
        else:
            print('   ⚠️  Not using futuristic component')
            issues.append('Dashboard page not using futuristic component')
    else:
        print('   ❌ Dashboard page NOT FOUND')
        issues.append('Dashboard page missing')

    # Check 4: Services running
    print('\n📋 Check 4: Services Status')
    ports_to_check = {
        5000: 'Backend/Frontend',
        5173: 'Vite Dev Server'
    }

    for port, name in ports_to_check.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result == 0:
                print(f'   ✅ Port {port} ({name}): RUNNING')
            else:
                print(f'   ❌ Port {port} ({name}): NOT RESPONDING')
                issues.append(f'{name} not running on port {port}')
        except Exception as e:
            print(f'   ❌ Port {port} ({name}): ERROR - {e}')
            issues.append(f'{name} check failed')

    # Check 5: Browser cache issue
    print('\n📋 Check 5: Frontend Build')
    vite_config = Path('client/vite.config.ts')
    if vite_config.exists():
        print('   ✅ Vite config exists')
    else:
        print('   ❌ Vite config missing')

    # Summary
    print('\n' + '='*80)
    print('📊 ANALYSIS SUMMARY')
    print('='*80)

    if issues:
        print(f'\n❌ Found {len(issues)} issue(s):')
        for i, issue in enumerate(issues, 1):
            print(f'   {i}. {issue}')

        print('\n🔧 AURORA AUTO-FIX RECOMMENDATIONS:')
        print('   1. Clear browser cache (Ctrl+Shift+Delete)')
        print('   2. Hard refresh browser (Ctrl+Shift+R or Ctrl+F5)')
        print('   3. Check browser console for errors (F12)')
        print('   4. Verify you are visiting http://localhost:5000')
        print('   5. Try visiting http://localhost:5000/dashboard directly')
        print('')
        print('🎯 Most Likely Issue: Browser cache showing old UI')
        print('   Solution: Force refresh with Ctrl+Shift+R')
    else:
        print('\n✅ All checks passed!')
        print('   UI should be visible at http://localhost:5000')
        print('')
        print('🎯 If still not visible:')
        print('   1. Clear browser cache completely')
        print('   2. Try incognito/private browsing mode')
        print('   3. Check browser console (F12) for JavaScript errors')

    print('\n' + '='*80)
    print('✨ AURORA SELF-ANALYSIS COMPLETE')
    print('='*80 + '\n')

    return len(issues)


if __name__ == '__main__':
    exit(main())
