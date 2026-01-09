#!/usr/bin/env bash
set -e
for p in $(ls packs); do
  echo "-- $p --"
  python3 installer/aurora_installer.py stage --pack $p || true
  python3 installer/aurora_installer.py dry-run --pack $p || true
  python3 installer/aurora_installer.py install --pack $p || true
  bash packs/$p/health_check.sh || true
done
