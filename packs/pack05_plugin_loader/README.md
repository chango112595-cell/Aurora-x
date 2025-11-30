# PACK05 - Sandboxed Plugin Loader (5B)

Purpose
-------
Provides a secure, best-effort sandbox runtime for plugin packages.
- Creates per-plugin sandbox workdirs inside pack VFS (uses PACK 3 vfs)
- Applies soft resource limits (via `resource`) where available
- Provides isolation manager to stage and run plugin entrypoints under supervision
- Provides a small policy/jail system (whitelist paths, deny syscalls hints)

Safety
------
- Non-privileged operations only; does not perform chroot or kernel-level namespace changes.
- Uses soft limits and monitoring. Dangerous operations are gated and require operator approval.
- Plugins are validated and staged; execution is performed by PACK 4 supervisor via hypervisor.

Quick test
----------
Stage & dry-run:
  python3 installer/aurora_installer.py stage --pack pack05_plugin_loader
  python3 installer/aurora_installer.py dry-run --pack pack05_plugin_loader

Run unit tests:
  python3 -m pytest packs/pack05_plugin_loader/tests -q
