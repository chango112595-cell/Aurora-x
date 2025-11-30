#!/usr/bin/env bash
set -euo pipefail
python3 packs/pack02_env_profiler/profiler/export_profile.py --dry
test -f profile_tmp.json
python3 - <<'PY'
import json
p=json.load(open("profile_tmp.json"))
assert "probe" in p
print("export test OK")
PY
