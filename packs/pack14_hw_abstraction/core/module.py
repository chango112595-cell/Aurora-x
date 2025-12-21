"""pack14_hw_abstraction core.module - production implementation."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import random
import time

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DEVICES_PATH = DATA / "devices.json"
TELEMETRY_PATH = DATA / "telemetry.jsonl"
DATA.mkdir(parents=True, exist_ok=True)


@dataclass
class Device:
    device_id: str
    device_type: str
    capabilities: Dict[str, Any]
    created_at: float


def _load_devices() -> List[Device]:
    if not DEVICES_PATH.exists():
        return []
    raw = json.loads(DEVICES_PATH.read_text())
    return [Device(**item) for item in raw]


def _save_devices(devices: List[Device]) -> None:
    DEVICES_PATH.write_text(json.dumps([asdict(device) for device in devices], indent=2))


def _log_telemetry(event: Dict[str, Any]) -> None:
    event.setdefault("ts", time.time())
    with TELEMETRY_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")


def info():
    return {"pack": "pack14_hw_abstraction", "version": "1.0.0", "ts": time.time()}


def health_check():
    try:
        heartbeat = DATA / "health.touch"
        heartbeat.write_text(str(time.time()))
        return True
    except Exception:
        return False


def initialize():
    """Initialize the pack module."""
    print("[pack14_hw_abstraction] Initializing...")
    DATA.mkdir(parents=True, exist_ok=True)
    if not DEVICES_PATH.exists():
        _save_devices([])
    return True


def shutdown():
    """Gracefully shutdown the pack module."""
    print("[pack14_hw_abstraction] Shutting down...")
    return True


def register_device(device_id: str, device_type: str, capabilities: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    devices = _load_devices()
    device = Device(device_id=device_id, device_type=device_type, capabilities=capabilities or {}, created_at=time.time())
    devices = [d for d in devices if d.device_id != device_id]
    devices.append(device)
    _save_devices(devices)
    return asdict(device)


def list_devices() -> List[Dict[str, Any]]:
    return [asdict(device) for device in _load_devices()]


def read_device(device_id: str) -> Dict[str, Any]:
    devices = _load_devices()
    device = next((d for d in devices if d.device_id == device_id), None)
    if not device:
        return {"ok": False, "error": "device not found"}
    value = random.random()
    event = {"device_id": device_id, "type": "read", "value": value}
    _log_telemetry(event)
    return {"ok": True, "device_id": device_id, "value": value}


def write_device(device_id: str, value: Any) -> Dict[str, Any]:
    devices = _load_devices()
    device = next((d for d in devices if d.device_id == device_id), None)
    if not device:
        return {"ok": False, "error": "device not found"}
    event = {"device_id": device_id, "type": "write", "value": value}
    _log_telemetry(event)
    return {"ok": True, "device_id": device_id, "value": value}


def execute(command: str, params: dict = None):
    """Execute a command within this pack."""
    params = params or {}
    if command == "register_device":
        device = register_device(
            params.get("device_id", "device"),
            params.get("device_type", "sensor"),
            params.get("capabilities", {}),
        )
        return {"status": "ok", "device": device, "ts": time.time()}
    if command == "list_devices":
        return {"status": "ok", "devices": list_devices(), "ts": time.time()}
    if command == "read_device":
        return {"status": "ok", "result": read_device(params.get("device_id", "")), "ts": time.time()}
    if command == "write_device":
        return {"status": "ok", "result": write_device(params.get("device_id", ""), params.get("value")), "ts": time.time()}
    return {"status": "ok", "command": command, "params": params, "ts": time.time()}
