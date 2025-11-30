# PACK 01 - Unified Process Core

Purpose:
- Core orchestrator for Aurora: event bus, lifecycle manager, logging, state store.
- Provides pack-level entrypoints: install, start, stop, health.
- Integrates with Section 0 installer (staging/activate/rollback).

Security & Safety:
- Install supports `--dry-run`. Default operations are non-destructive.
- No network services opened by default.
- All logs and state are stored under this pack folder.

Usage (developer):
- Dry-run staging:
  python3 installer/aurora_installer.py stage --pack pack01_pack01
- Install/activate (operator approval required):
  python3 installer/aurora_installer.py install --pack pack01_pack01
- Start locally:
  bash packs/pack01_pack01/start.sh
- Run tests:
  bash packs/pack01_pack01/tests/test_health.sh
