# PACK 03 - Aurora OS Base (Section 3A)

This section implements the Aurora OS Core:
- Virtual filesystem (vfs.py)
- Namespace registry (namespace.py)
- Lightweight scheduler (scheduler.py)
- Process abstraction (process_abstraction.py)

Integration:
- Works with Section 0 installer for staging/activate/rollback.
- Will export services under live/pack03_os_base after activation.

Runbook (quick):
- Stage: python3 installer/aurora_installer.py stage --pack pack03_os_base
- Dry-run: python3 installer/aurora_installer.py dry-run --pack pack03_os_base
- Install: python3 installer/aurora_installer.py install --pack pack03_os_base
- Test: python3 -m pytest packs/pack03_os_base/tests -q
