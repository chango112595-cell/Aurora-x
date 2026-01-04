"""Maritime platform adapter for Aurora EdgeOS."""
from __future__ import annotations

from typing import Any, Dict
import random
import time

from aurora_edgeos.core.edge_core import AuroraEdgeCore
from aurora_edgeos.hal.sensor import Sensor


class MaritimeRuntime:
    def __init__(self, device_id: str | None = None, config: Dict[str, Any] | None = None):
        self.core = AuroraEdgeCore(device_type="maritime", device_id=device_id, config=config)
        self._sensors = {
            "heading_deg": Sensor("heading_deg", lambda: round(random.uniform(0, 359.9), 1)),
            "speed_kn": Sensor("speed_kn", lambda: round(random.uniform(0, 45), 2)),
            "depth_m": Sensor("depth_m", lambda: round(random.uniform(1, 200), 1)),
        }

    def start(self) -> None:
        self.core.start()

    def stop(self) -> None:
        self.core.stop()

    def health_check(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "device_type": self.core.device_type,
            "device_id": self.core.device_id,
            "ts": time.time(),
        }

    def read_sensors(self) -> Dict[str, Any]:
        return {name: sensor.read() for name, sensor in self._sensors.items()}

    def send_command(self, command: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        payload = payload or {}
        return {
            "status": "accepted",
            "command": command,
            "payload": payload,
            "device_id": self.core.device_id,
            "ts": time.time(),
        }
