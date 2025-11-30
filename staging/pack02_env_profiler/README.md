# PACK 02 - Environment Profiler (Hybrid mode)

Purpose
-------
Detect device capabilities and choose best execution profile for Aurora.
Provides:
- device probing (OS, arch)
- safe performance tests (lightweight)
- optional deep benchmarks (on operator approval)
- gpu detection
- scoring engine that selects recommended execution mode
- export of environment/profile into live/environment/profile.json

Safety
------
- Default tests are low-intensity and safe for all devices.
- Deep stress tests run only if operator explicitly requests (`--deep`) and device score allows it.
- All operations are local-only. No network calls by default.
- Integrates with Section 0 installer for staging/activation/rollback.

Usage
-----
Dry-run:
  python3 installer/aurora_installer.py stage --pack pack02_env_profiler

Run safe probe locally:
  python3 packs/pack02_env_profiler/profiler/device_probe.py --safe

Run full hybrid (may run optional deep tests after permission):
  python3 packs/pack02_env_profiler/profiler/export_profile.py --auto-deep
