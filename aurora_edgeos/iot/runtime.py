"""IoT platform adapter for Aurora EdgeOS."""
from __future__ import annotations

from typing import Any, Dict
import random
import time

from aurora_edgeos.core.edge_core import AuroraEdgeCore
from aurora_edgeos.hal.sensor import Sensor


class IoTRuntime:
    def __init__(self, device_id: str | None = None, config: Dict[str, Any] | None = None):
        self.core = AuroraEdgeCore(device_type="iot", device_id=device_id, config=config)
        self._sensors = {
            "temp_c": Sensor("temp_c", lambda: round(random.uniform(15, 35), 1)),
            "humidity_pct": Sensor("humidity_pct", lambda: round(random.uniform(20, 90), 1)),
            "battery_pct": Sensor("battery_pct", lambda: round(random.uniform(10, 100), 1)),
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
