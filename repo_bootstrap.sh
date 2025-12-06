#!/usr/bin/env bash
set -euo pipefail

echo "=== Aurora Repo Bootstrap Starting ==="

ROOT="$(pwd)"

# -------------------------------------------------------------------
# Helper for writing files safely
# -------------------------------------------------------------------
write() {
  local path="$1"
  shift
  mkdir -p "$(dirname "$path")"
  cat > "$path" <<'EOF'
'"$@"'
EOF
}

# -------------------------------------------------------------------
# PACK TEMPLATE FUNCTION
# -------------------------------------------------------------------
make_pack() {
  local pack="$1"

  echo "Creating $pack..."

  mkdir -p "packs/$pack/core"
  mkdir -p "packs/$pack/tests"
  mkdir -p "packs/$pack/data"
  mkdir -p "packs/$pack/logs"

  # manifest.yaml
  cat > "packs/$pack/manifest.yaml" <<EOF
schema_version: aurora-manifest-v1
pack:
  id: $pack
  name: $pack
  version: "0.1.0"
  description: "$pack core"
  entrypoint:
    install: install.sh
    start: start.sh
    stop: stop.sh
    health: health_check.sh
  dependencies: []
  artifacts: []
  safety:
    dry_run_supported: true
    operator_approval_required: true
EOF

  # install.sh
  cat > "packs/$pack/install.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$ROOT/data" "$ROOT/logs"
echo "{\"installed_at\":\"$(date --iso-8601=seconds)\"}" > "$ROOT/data/installed.json"
echo "[install] done"
EOF

  # start.sh
  cat > "packs/$pack/start.sh" <<'EOF'
#!/usr/bin/env bash
ROOT="$(cd "$(dirname "$0")" && pwd)"
nohup python3 -u "$ROOT/core/queue_worker.py" >> "$ROOT/logs/pack.log" 2>&1 &
echo "[start] launched"
EOF

  # stop.sh
  cat > "packs/$pack/stop.sh" <<EOF
#!/usr/bin/env bash
pkill -f "$pack" || true
echo "[stop] requested"
EOF

  # health_check.sh
  cat > "packs/$pack/health_check.sh" <<'EOF'
#!/usr/bin/env bash
python3 - <<'PY' || { echo "health FAIL"; exit 2; }
from pathlib import Path; import time
p = Path(__file__).resolve().parents[1] / 'data'
p.mkdir(parents=True, exist_ok=True)
(p/"health.touch").write_text(str(time.time()))
print("ok")
PY
echo "health OK"
EOF

  # core/module.py
  cat > "packs/$pack/core/module.py" <<EOF
from pathlib import Path
import json, time

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)

def info():
    return {"pack": "$pack", "version": "0.1.0", "ts": time.time()}

def health_check():
    try:
        f = DATA / "health.touch"
        f.write_text(str(time.time()))
        return True
    except:
        return False

def initialize(**kwargs):
    (DATA/"state.json").write_text(json.dumps({"initialized":True}))
    return True

def shutdown():
    return True

def execute(task_name, args=None):
    args = args or {}
    if task_name == "noop":
        return {"ok":True}
    if task_name == "write_state":
        st = DATA/"state.json"
        cur = {}
        if st.exists():
            try: cur = json.loads(st.read_text())
            except: cur = {}
        cur[args.get("k","k")] = args.get("v",None)
        st.write_text(json.dumps(cur))
        return {"ok":True}
    return {"ok":False,"error":"unknown_task"}
EOF

  # core/ipc.py
  cat > "packs/$pack/core/ipc.py" <<'EOF'
import time, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ_DIR = ROOT/"data/queue/requests"
RES_DIR = ROOT/"data/queue/responses"
REQ_DIR.mkdir(parents=True, exist_ok=True)
RES_DIR.mkdir(parents=True, exist_ok=True)

def enqueue(plugin, cmd, payload=None):
    payload = payload or {}
    name = f"{plugin}-{int(time.time()*1000)}.req"
    (REQ_DIR/name).write_text(json.dumps({
        "plugin":plugin,"cmd":cmd,"payload":payload,"ts":time.time()
    }))
    return str(REQ_DIR/name)

def poll(req_name, timeout=2.0):
    rf = RES_DIR / (Path(req_name).name + ".result.json")
    start = time.time()
    while time.time() - start < timeout:
        if rf.exists():
            try:
                return json.loads(rf.read_text())
            except:
                return None
    return None
EOF

  # core/queue_worker.py
  cat > "packs/$pack/core/queue_worker.py" <<'EOF'
import time, json, traceback
from pathlib import Path
from .module import execute

ROOT = Path(__file__).resolve().parents[1]
REQ = ROOT/"data/queue/requests"
RES = ROOT/"data/queue/responses"
REQ.mkdir(parents=True, exist_ok=True)
RES.mkdir(parents=True, exist_ok=True)

def _process(f):
    try:
        obj = json.loads(f.read_text())
        cmd = obj.get("cmd")
        payload = obj.get("payload",{})
        if cmd == "execute":
            out = execute(payload.get("task"), payload.get("args",{}))
        else:
            out = {"ok":False,"error":"unknown_cmd"}
        (RES/(f.name+".result.json")).write_text(json.dumps(out))
    except Exception as e:
        (RES/(f.name+".error.json")).write_text(json.dumps({
            "error":str(e),"tb":traceback.format_exc()
        }))
    finally:
        try: f.unlink()
        except: pass

def main_loop(poll=0.2):
    while True:
        for f in list(REQ.iterdir()):
            if f.suffix == ".req":
                _process(f)
        time.sleep(poll)

if __name__ == "__main__":
    main_loop()
EOF

  # capabilities.json
  echo '{"fs.read": true, "fs.write": false, "plugin.install": true}' \
    > "packs/$pack/capabilities.json"

  # plugin_catalog.json
  echo '[{"id":"'"$pack"'.example","name":"Example","version":"0.1.0"}]' \
    > "packs/$pack/plugin_catalog.json"

  # tests/conftest.py
  cat > "packs/$pack/tests/conftest.py" <<'EOF'
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
EOF

  # tests/test_core.py
  cat > "packs/$pack/tests/test_core.py" <<EOF
def test_info():
    from core.module import info
    r = info()
    assert r.get("pack") == "$pack"
EOF

  chmod +x packs/$pack/*.sh
}

# -------------------------------------------------------------------
# CREATE PACKS 1–15
# -------------------------------------------------------------------
PACKS=(
  pack01_pack01
  pack02_env_profiler
  pack03_os_base
  pack04_launcher
  pack05_5E_capability_system
  pack05_5F_event_hooks
  pack05_5G_permissions_resolver
  pack05_5H_plugin_store
  pack05_5I_versioning_upgrades
  pack05_5J_state_persistence
  pack05_5K_diagnostics
  pack05_5L_test_framework
  pack05_plugin_api
  pack05_plugin_loader
  pack06_firmware_system
  pack07_secure_signing
  pack08_conversational_engine
  pack09_compute_layer
  pack10_autonomy_engine
  pack11_device_mesh
  pack12_toolforge
  pack13_runtime_2
  pack14_hw_abstraction
  pack15_intel_fabric
)

for pk in "${PACKS[@]}"; do
  make_pack "$pk"
done

# -------------------------------------------------------------------
# SUPPORTING FILES — RUNNERS, GENERATORS, MONITORING, SIGNING, ETC.
# -------------------------------------------------------------------

# run_pack_tests.py
cat > run_pack_tests.py <<'EOF'
#!/usr/bin/env python3
import subprocess, sys
from pathlib import Path

ROOT = Path.cwd()
packs = sorted([p for p in (ROOT/"packs").iterdir() if p.is_dir()])

fails = []
for p in packs:
    print(f"\n=== TEST {p.name} ===")
    rc = subprocess.run([sys.executable,"-m","pytest",str(p/"tests"),"-q"]).returncode
    if rc != 0:
        fails.append(p.name)

if fails:
    print("\nFAILED:", fails)
    sys.exit(1)
print("\nALL PACKS OK")
EOF
chmod +x run_pack_tests.py

# installer
mkdir -p installer
cat > installer/aurora_installer.py <<'EOF'
#!/usr/bin/env python3
import argparse, subprocess, sys
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("action", choices=["stage","dry-run","install"])
p.add_argument("--pack", required=True)
a = p.parse_args()

pack = Path("packs")/a.pack
if not pack.exists():
    print("Missing pack"); sys.exit(2)

if a.action=="stage":
    (pack/"data").mkdir(parents=True, exist_ok=True)
    (pack/"data"/"staged.txt").write_text("staged")
elif a.action=="dry-run":
    h = pack/"health_check.sh"
    if h.exists(): subprocess.call(["bash",str(h)])
elif a.action=="install":
    (pack/"data"/"installed.txt").write_text("installed")
print("done")
EOF
chmod +x installer/aurora_installer.py

# docs
mkdir -p docs/scripts docs/docs/packs
cat > docs/scripts/gen_docs.py <<'EOF'
#!/usr/bin/env python3
import glob, yaml, os
out = "docs/docs/packs"
os.makedirs(out, exist_ok=True)
for m in glob.glob("packs/*/manifest.yaml"):
    name = os.path.basename(os.path.dirname(m))
    try:
        data = yaml.safe_load(open(m))
        t = data["pack"]["name"]
    except:
        t = name
    open(f"{out}/{name}.md","w").write(f"# {t}\n\nGenerated doc for {name}\n")
print("docs OK")
EOF
chmod +x docs/scripts/gen_docs.py

# tools - gen_pack_graph.py (don't overwrite existing luminar_nexus_v2.py)
cat > tools/gen_pack_graph.py <<'EOF'
#!/usr/bin/env python3
from pathlib import Path
import yaml

lines=["digraph packs {"]
for p in Path("packs").glob("*"):
    m = p/"manifest.yaml"
    if not m.exists(): continue
    name=p.name
    lines.append(f'"{name}";')
    try:
        data=yaml.safe_load(open(m))
        deps=data.get("pack",{}).get("dependencies",[])
        for d in deps:
            lines.append(f'"{name}" -> "{d.get("pack_id")}";')
    except: pass
lines.append("}")
open("tools/pack_graph.dot","w").write("\n".join(lines))
print("ok")
EOF
chmod +x tools/gen_pack_graph.py

cat > tools/load_gen.py <<'EOF'
#!/usr/bin/env python3
import argparse, requests, threading, time

p=argparse.ArgumentParser()
p.add_argument("--url", default="http://localhost:5000/health")
p.add_argument("--clients", type=int, default=5)
p.add_argument("--rps", type=float, default=1.0)
a=p.parse_args()

def worker():
    for _ in range(int(a.rps*10)):
        try: print("code",requests.get(a.url).status_code)
        except Exception as e: print("err",e)
        time.sleep(1/a.rps)

threads=[]
for _ in range(a.clients):
    t=threading.Thread(target=worker)
    t.start()
    threads.append(t)
for t in threads: t.join()
EOF
chmod +x tools/load_gen.py

# monitoring
mkdir -p monitoring
cat > monitoring/prometheus.yml <<'EOF'
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: aurora
    static_configs:
      - targets: ['localhost:8000']
EOF

# ops
mkdir -p ops
cat > ops/run_all_deploy.sh <<'EOF'
#!/usr/bin/env bash
set -e
for p in $(ls packs); do
  echo "-- $p --"
  python3 installer/aurora_installer.py stage --pack $p || true
  python3 installer/aurora_installer.py dry-run --pack $p || true
  python3 installer/aurora_installer.py install --pack $p || true
  bash packs/$p/health_check.sh || true
done
EOF
chmod +x ops/run_all_deploy.sh

# sign tools
mkdir -p sign_tools
cat > sign_tools/sha256_sign.py <<'EOF'
#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("--in",dest="fin",required=True)
p.add_argument("--out",dest="fout",required=True)
a=p.parse_args()
b=Path(a.fin).read_bytes()
h=hashlib.sha256(b).hexdigest()
Path(a.fout).write_text(json.dumps({"file":a.fin,"sha256":h}))
print("signed")
EOF
chmod +x sign_tools/sha256_sign.py

# webui backend
mkdir -p aurora_webui/backend
cat > aurora_webui/backend/app.py <<'EOF'
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
app = FastAPI()
@app.get("/api/health")
def h(): return {"ok":True}
@app.get("/api/packs")
def p(): return {"packs":[d for d in os.listdir("packs") if d.startswith("pack")]}
EOF

cat > aurora_webui/backend/Dockerfile <<'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install fastapi uvicorn
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","80"]
EOF

echo "=== Aurora Repo Bootstrap Complete ==="