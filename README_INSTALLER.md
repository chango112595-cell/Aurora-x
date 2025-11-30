README_INSTALLER.md

How to use the Aurora hybrid installer (Section 0):

1) Create pack skeletons:
   ./scripts/create_packs_structure.sh

2) Inspect packs/pack01...pack15 and populate each with real files
   (install.sh, start.sh, stop.sh, health_check.sh)

3) Stage a pack (dry-run):
   python3 installer/aurora_installer.py stage --pack pack01_pack01

4) Install (activate) with operator approval:
   python3 installer/aurora_installer.py install --pack pack01_pack01

5) Rollback:
   python3 installer/aurora_installer.py rollback --pack pack01_pack01

Notes:
- Default behavior is dry-run/staging only. Nothing is moved into live/ until you run install (activation).
- Use READMEs inside each pack for pack-specific install instructions.
