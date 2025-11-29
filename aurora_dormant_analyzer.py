#!/usr/bin/env python3
"""Aurora Dormant Systems Analyzer - Lists all 241 dormant systems"""

import json


def main():
    print('[AURORA] Analyzing 241 Dormant Systems')
    print('=' * 70)

    with open('AURORA_COMPLETE_SYSTEM_ANALYSIS.json', 'r') as f:
        data = json.load(f)

    orchestrators = data.get('orchestrators', [])
    autonomous = data.get('autonomous_systems', [])
    daemons = data.get('daemon_systems', [])

    print(f'\n📋 ORCHESTRATION SYSTEMS: {len(orchestrators)}')
    print('-' * 70)
    for i, system in enumerate(orchestrators, 1):
        print(f'{i}. {system["file"]}')
        print(
            f'   Size: {system.get("size", 0)} bytes | Classes: {len(system.get("classes", []))}')

    print(f'\n🤖 AUTONOMOUS SYSTEMS: {len(autonomous)}')
    print('-' * 70)
    for i, system in enumerate(autonomous, 1):
        print(f'{i}. {system["file"]}')
        print(f'   Size: {system.get("size", 0)} bytes')

    print(f'\n⚙️  DAEMON/MONITORING SYSTEMS: {len(daemons)}')
    print('-' * 70)
    for i, system in enumerate(daemons, 1):
        print(f'{i}. {system["file"]}')

    total = len(orchestrators) + len(autonomous) + len(daemons)
    print(f'\n' + '=' * 70)
    print(f'[AURORA] Total Dormant Systems: {total}')
    print('=' * 70)


if __name__ == '__main__':
    main()
