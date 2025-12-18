# PACK 05 - Plugin API Core (5A)

Purpose
-------
Provides the core Plugin API for Aurora:
- plugin metadata and registry
- standard plugin manifest schema
- non-executing loader (loads metadata, validates)
- permission model scaffold

Safety
------
- Plugins are never auto-executed by this pack.
- Loader only validates and stages plugin artifacts inside pack VFS.
- Execution is performed by Supervisor (PACK 4) and sandboxed by PACK 3.

Quick run
---------
Stage & dry-run:
  python3 installer/aurora_installer.py stage --pack pack05_plugin_api
  python3 installer/aurora_installer.py dry-run --pack pack05_plugin_api

Run unit tests:
  python3 -m pytest packs/pack05_plugin_api/tests -q
