# PACK 04 - Unified Launcher & Supervisor System (4A - 4J)

Purpose
-------
This pack provides the unified launcher and supervisor stack:
- 4A Launcher: start/stop/dispatch modules
- 4B Supervisor: watchdog, autorestart, policies
- 4C Metrics integration
- 4D Log unifier
- 4E Cross-runtime orchestration
- 4F Health microservice
- 4G Hot-reload execution graph
- 4H Multi-pack coordinator
- 4I Launch manifest
- 4J Installer hooks

Safety
------
- Default dry-run behavior in install.sh
- Supervisor policies are conservative (no killing without operator consent)
- All persistent state under packs/pack04_launcher/data and live/

Quick Test
----------
Stage & dry-run:
  python3 installer/aurora_installer.py stage --pack pack04_launcher
  python3 installer/aurora_installer.py dry-run --pack pack04_launcher

Run tests:
  python3 -m pytest packs/pack04_launcher/tests -q
