"""IPC abstraction - production ready: uses pack05 ipc_queue if present"""
import json
import time
import uuid
from pathlib import Path

try:
    from packs.pack05_plugin_api.core.ipc_queue import push_request, poll_response  # type: ignore
    HAS_QUEUE = True
except Exception:
    HAS_QUEUE = False

ROOT = Path(__file__).resolve().parents[1]
REQ_DIR = ROOT / '..' / 'data' / 'queue' / 'requests'
RES_DIR = ROOT / '..' / 'data' / 'queue' / 'responses'
REQ_DIR.mkdir(parents=True, exist_ok=True)
RES_DIR.mkdir(parents=True, exist_ok=True)


def send_request(target: str, action: str, payload: dict = None):
    """Send an IPC request to another pack or service."""
    payload = payload or {}
    req_id = str(uuid.uuid4())
    request = {
        'id': req_id,
        'target': target,
        'action': action,
        'payload': payload,
        'timestamp': time.time(),
        'source': 'pack10_autonomy_engine'
    }

    if HAS_QUEUE:
        push_request(request)
    else:
        req_file = REQ_DIR / f"{req_id}.json"
        req_file.write_text(json.dumps(request))

    return req_id


def receive_response(req_id: str, timeout: float = 5.0):
    """Wait for and receive a response to a request."""
    if HAS_QUEUE:
        return poll_response(req_id, timeout)

    deadline = time.time() + timeout
    res_file = RES_DIR / f"{req_id}.json"

    while time.time() < deadline:
        if res_file.exists():
            response = json.loads(res_file.read_text())
            res_file.unlink()
            return response
        time.sleep(0.1)

    return None


def broadcast(event: str, data: dict = None):
    """Broadcast an event to all listeners."""
    data = data or {}
    event_data = {
        'event': event,
        'data': data,
        'timestamp': time.time(),
        'source': 'pack10_autonomy_engine'
    }
    event_file = REQ_DIR / f"broadcast_{int(time.time() * 1000)}.json"
    event_file.write_text(json.dumps(event_data))
    return True
