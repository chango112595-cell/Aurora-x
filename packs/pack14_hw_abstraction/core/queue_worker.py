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


def _process(request_path: Path) -> None:
    try:
        obj = json.loads(request_path.read_text())
        cmd = obj.get("cmd")
        payload = obj.get("payload", {})
        if cmd == "execute":
            out = execute(payload.get("task"), payload.get("args", {}))
        else:
            out = {"ok": False, "error": "unknown_cmd"}
        (RES / f"{request_path.name}.result.json").write_text(json.dumps(out))
    except Exception as exc:
        (RES / f"{request_path.name}.error.json").write_text(
            json.dumps({"error": str(exc), "tb": traceback.format_exc()})
        )
    finally:
        try:
            request_path.unlink()
        except Exception as exc:
            (RES / f"{request_path.name}.cleanup.error.json").write_text(
                json.dumps({"error": str(exc), "tb": traceback.format_exc()})
            )


def main_loop(poll: float = 0.2) -> None:
    while True:
        for request_path in list(REQ.iterdir()):
            if request_path.suffix == ".req":
                _process(request_path)
        time.sleep(poll)


if __name__ == "__main__":
    main_loop()
