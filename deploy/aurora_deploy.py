#!/usr/bin/env python3
"""aurora_deploy.py - lightweight deploy tool for Aurora packs and services

Usage:
  python3 aurora_deploy.py deploy --pack pack06_firmware_system --node local
  python3 aurora_deploy.py status
  python3 aurora_deploy.py rollback --tag <previous-tag>
"""
import argparse, subprocess, json, sys, time
from pathlib import Path

PACKS_DIR = Path('packs')
LOG = Path('deploy/logs/deploy.log')
LOG.parent.mkdir(parents=True, exist_ok=True)

def sh(cmd):
    print('>', cmd)
    r = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    existing = LOG.read_text() if LOG.exists() else ''
    LOG.write_text(existing + f"\n$ {cmd}\n" + (r.stdout or '') + (r.stderr or ''))
    return r

def deploy_pack(pack, node='local'):
    p = PACKS_DIR / pack
    if not p.exists():
        print('Pack not found', pack); return 2
    print('Staging', pack)
    sh(f'python3 installer/aurora_installer.py stage --pack {pack}')
    print('Dry-run')
    sh(f'python3 installer/aurora_installer.py dry-run --pack {pack}')
    print('Install')
    sh(f'python3 installer/aurora_installer.py install --pack {pack}')
    print('Health check')
    sh(f'bash packs/{pack}/health_check.sh')
    return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['deploy','status','rollback'])
    parser.add_argument('--pack', default=None)
    parser.add_argument('--node', default='local')
    parser.add_argument('--tag', default=None)
    args = parser.parse_args()
    if args.action == 'deploy':
        if not args.pack:
            print('pack is required for deploy'); sys.exit(1)
        sys.exit(deploy_pack(args.pack, args.node))
    elif args.action == 'status':
        print('Deploy status: see deploy/logs/deploy.log')
    elif args.action == 'rollback':
        print('Rollback requested', args.tag)
if __name__ == '__main__':
    main()