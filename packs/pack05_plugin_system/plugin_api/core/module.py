from pathlib import Path
import json, time

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)

def info():
    return {"pack": "pack05_plugin_api", "version": "0.1.0", "ts": time.time()}

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