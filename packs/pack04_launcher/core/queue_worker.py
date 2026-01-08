import json
import time
import traceback
from pathlib import Path

from .module import execute

ROOT = Path(__file__).resolve().parents[1]
REQ = ROOT / "data/queue/requests"
RES = ROOT / "data/queue/responses"
REQ.mkdir(parents=True, exist_ok=True)
RES.mkdir(parents=True, exist_ok=True)


def _process(f):
    try:
        obj = json.loads(f.read_text())
        cmd = obj.get("cmd")
        payload = obj.get("payload", {})
        if cmd == "execute":
            out = execute(payload.get("task"), payload.get("args", {}))
        else:
            out = {"ok": False, "error": "unknown_cmd"}
        (RES / (f.name + ".result.json")).write_text(json.dumps(out))
    except Exception as e:
        (RES / (f.name + ".error.json")).write_text(
            json.dumps({"error": str(e), "tb": traceback.format_exc()})
        )
    finally:
        try:
            f.unlink()
        except:
            pass


def main_loop(poll=0.2):
    while True:
        for f in list(REQ.iterdir()):
            if f.suffix == ".req":
                _process(f)
        time.sleep(poll)


if __name__ == "__main__":
    main_loop()
