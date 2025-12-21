"""pack06_firmware_system core.module - production implementation."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REGISTRY_PATH = DATA / "firmware_registry.json"
UPDATES_PATH = DATA / "update_history.jsonl"
DATA.mkdir(parents=True, exist_ok=True)


@dataclass
class FirmwareRecord:
    firmware_id: str
    name: str
    version: str
    checksum: str
    metadata: Dict[str, Any]
    created_at: float


def _load_registry() -> List[FirmwareRecord]:
    if not REGISTRY_PATH.exists():
        return []
    raw = json.loads(REGISTRY_PATH.read_text())
    return [FirmwareRecord(**item) for item in raw]


def _save_registry(records: List[FirmwareRecord]) -> None:
    REGISTRY_PATH.write_text(json.dumps([asdict(r) for r in records], indent=2))


def _record_update(event: Dict[str, Any]) -> None:
    event.setdefault("ts", time.time())
    with UPDATES_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")


def info():
    return {"pack": "pack06_firmware_system", "version": "1.0.0", "ts": time.time()}


def health_check():
    try:
        heartbeat = DATA / "health.touch"
        heartbeat.write_text(str(time.time()))
        return True
    except Exception:
        return False


def initialize():
    """Initialize the pack module."""
    print("[pack06_firmware_system] Initializing...")
    DATA.mkdir(parents=True, exist_ok=True)
    if not REGISTRY_PATH.exists():
        _save_registry([])
    return True


def shutdown():
    """Gracefully shutdown the pack module."""
    print("[pack06_firmware_system] Shutting down...")
    return True


def _compute_checksum(payload: Optional[str]) -> str:
    if payload is None:
        payload = ""
    if isinstance(payload, str):
        payload_bytes = payload.encode("utf-8")
    else:
        payload_bytes = str(payload).encode("utf-8")
    return sha256(payload_bytes).hexdigest()


def register_firmware(name: str, version: str, image: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
    records = _load_registry()
    firmware_id = f"fw-{uuid.uuid4().hex[:12]}"
    record = FirmwareRecord(
        firmware_id=firmware_id,
        name=name,
        version=version,
        checksum=_compute_checksum(image),
        metadata=metadata or {},
        created_at=time.time(),
    )
    records.append(record)
    _save_registry(records)
    _record_update({"event": "registered", "firmware_id": firmware_id, "name": name, "version": version})
    return asdict(record)


def list_firmware() -> List[Dict[str, Any]]:
    return [asdict(record) for record in _load_registry()]


def latest_firmware(name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    records = _load_registry()
    if name:
        records = [r for r in records if r.name == name]
    if not records:
        return None
    latest = max(records, key=lambda r: r.created_at)
    return asdict(latest)


def schedule_update(device_id: str, firmware_id: str) -> Dict[str, Any]:
    update_id = f"upd-{uuid.uuid4().hex[:12]}"
    event = {
        "event": "scheduled",
        "update_id": update_id,
        "device_id": device_id,
        "firmware_id": firmware_id,
        "status": "scheduled",
    }
    _record_update(event)
    return event


def update_status(update_id: str, status: str) -> Dict[str, Any]:
    event = {"event": "status", "update_id": update_id, "status": status}
    _record_update(event)
    return event


def execute(command: str, params: dict = None):
    """Execute a command within this pack."""
    params = params or {}
    if command == "register_firmware":
        return {"status": "ok", "record": register_firmware(
            name=params.get("name", "unknown"),
            version=params.get("version", "0.0.0"),
            image=params.get("image"),
            metadata=params.get("metadata", {}),
        ), "ts": time.time()}
    if command == "list_firmware":
        return {"status": "ok", "items": list_firmware(), "ts": time.time()}
    if command == "latest_firmware":
        return {"status": "ok", "item": latest_firmware(params.get("name")), "ts": time.time()}
    if command == "schedule_update":
        return {"status": "ok", "update": schedule_update(
            device_id=params.get("device_id", "unknown"),
            firmware_id=params.get("firmware_id", "unknown"),
        ), "ts": time.time()}
    if command == "update_status":
        return {"status": "ok", "update": update_status(
            update_id=params.get("update_id", "unknown"),
            status=params.get("status", "unknown"),
        ), "ts": time.time()}
    return {"status": "ok", "command": command, "params": params, "ts": time.time()}
