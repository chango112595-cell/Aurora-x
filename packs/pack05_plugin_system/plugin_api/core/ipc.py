import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ_DIR = ROOT / "data/queue/requests"
RES_DIR = ROOT / "data/queue/responses"
REQ_DIR.mkdir(parents=True, exist_ok=True)
RES_DIR.mkdir(parents=True, exist_ok=True)


def enqueue(plugin, cmd, payload=None):
    payload = payload or {}
    name = f"{plugin}-{int(time.time() * 1000)}.req"
    (REQ_DIR / name).write_text(
        json.dumps({"plugin": plugin, "cmd": cmd, "payload": payload, "ts": time.time()})
    )
    return str(REQ_DIR / name)


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
