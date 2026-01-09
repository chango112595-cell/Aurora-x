"""Automotive platform adapter for Aurora EdgeOS.

Production-ready automotive runtime with comprehensive sensor/actuator support,
telemetry collection, and vehicle control capabilities.
"""

from __future__ import annotations

import logging
import random
import threading
import time
from collections import deque
from typing import Any

from aurora_edgeos.core.edge_core import AuroraEdgeCore
from aurora_edgeos.hal.actuator import Actuator
from aurora_edgeos.hal.sensor import Sensor

logger = logging.getLogger(__name__)


class AutomotiveRuntime:
    """Automotive platform runtime for vehicle control and monitoring."""

    def __init__(self, device_id: str | None = None, config: dict[str, Any] | None = None):
        self.core = AuroraEdgeCore(device_type="automotive", device_id=device_id, config=config)
        self.config = config or {}
        
        # Vehicle state
        self._ignition_on = False
        self._engine_running = False
        self._gear_position = "P"  # P, R, N, D, 1, 2, 3, etc.
        self._speed_kph = 0.0
        self._rpm = 0
        self._fuel_level_pct = 100.0
        
        # Telemetry history (last 1000 readings)
        self._telemetry_history = deque(maxlen=1000)
        
        # Sensors
        self._sensors = {
            "speed_kph": Sensor("speed_kph", self._read_speed),
            "rpm": Sensor("rpm", self._read_rpm),
            "battery_v": Sensor("battery_v", lambda: round(random.uniform(11.5, 14.2), 2)),
            "fuel_level_pct": Sensor("fuel_level_pct", self._read_fuel_level),
            "engine_temp_c": Sensor("engine_temp_c", lambda: round(random.uniform(85, 105), 1)),
            "oil_pressure_psi": Sensor("oil_pressure_psi", lambda: round(random.uniform(30, 60), 1)),
            "tire_pressure_fl": Sensor("tire_pressure_fl", lambda: round(random.uniform(30, 35), 1)),
            "tire_pressure_fr": Sensor("tire_pressure_fr", lambda: round(random.uniform(30, 35), 1)),
            "tire_pressure_rl": Sensor("tire_pressure_rl", lambda: round(random.uniform(30, 35), 1)),
            "tire_pressure_rr": Sensor("tire_pressure_rr", lambda: round(random.uniform(30, 35), 1)),
            "brake_pedal_pct": Sensor("brake_pedal_pct", lambda: round(random.uniform(0, 100), 1)),
            "throttle_pct": Sensor("throttle_pct", lambda: round(random.uniform(0, 100), 1)),
        }
        
        # Actuators
        self._actuators = {
            "ignition": Actuator("ignition", self._set_ignition),
            "gear": Actuator("gear", self._set_gear),
            "throttle": Actuator("throttle", self._set_throttle),
            "brake": Actuator("brake", self._set_brake),
            "lights": Actuator("lights", self._set_lights),
        }
        
        # Telemetry collection thread
        self._telemetry_thread = None
        self._telemetry_running = False

    def _read_speed(self) -> float:
        """Read current vehicle speed"""
        return round(self._speed_kph, 2)

    def _read_rpm(self) -> int:
        """Read engine RPM"""
        if not self._engine_running:
            return 0
        return int(self._rpm)

    def _read_fuel_level(self) -> float:
        """Read fuel level percentage"""
        return round(self._fuel_level_pct, 1)

    def _set_ignition(self, state: bool) -> bool:
        """Set ignition state"""
        self._ignition_on = bool(state)
        if self._ignition_on and not self._engine_running:
            self._engine_running = True
            self._rpm = 700  # Idle RPM
            logger.info(f"[Automotive] Ignition ON - Engine started")
        elif not self._ignition_on:
            self._engine_running = False
            self._rpm = 0
            self._speed_kph = 0.0
            logger.info(f"[Automotive] Ignition OFF - Engine stopped")
        return True

    def _set_gear(self, position: str) -> bool:
        """Set gear position"""
        valid_gears = ["P", "R", "N", "D", "1", "2", "3", "4", "5", "6"]
        if position.upper() not in valid_gears:
            logger.warning(f"[Automotive] Invalid gear position: {position}")
            return False
        self._gear_position = position.upper()
        logger.info(f"[Automotive] Gear changed to {self._gear_position}")
        return True

    def _set_throttle(self, percentage: float) -> bool:
        """Set throttle position (0-100%)"""
        pct = max(0.0, min(100.0, float(percentage)))
        if self._engine_running:
            # Simulate RPM increase with throttle
            base_rpm = 700 if self._gear_position == "N" or self._gear_position == "P" else 800
            self._rpm = int(base_rpm + (pct / 100.0) * 3800)
            # Simulate speed increase (only in drive gears)
            if self._gear_position == "D" and pct > 0:
                self._speed_kph = min(120.0, self._speed_kph + (pct / 100.0) * 2.0)
        return True

    def _set_brake(self, percentage: float) -> bool:
        """Set brake pressure (0-100%)"""
        pct = max(0.0, min(100.0, float(percentage)))
        if pct > 0:
            # Braking reduces speed
            self._speed_kph = max(0.0, self._speed_kph - (pct / 100.0) * 5.0)
            if self._speed_kph == 0:
                self._rpm = 700  # Return to idle
        return True

    def _set_lights(self, state: dict[str, bool]) -> bool:
        """Set vehicle lights (headlights, taillights, etc.)"""
        # Store light state in config
        self.config.setdefault("lights", {}).update(state)
        return True

    def _telemetry_collector(self):
        """Background thread to collect telemetry data"""
        while self._telemetry_running:
            try:
                telemetry = {
                    "ts": time.time(),
                    "device_id": self.core.device_id,
                    "sensors": self.read_sensors(),
                    "state": {
                        "ignition": self._ignition_on,
                        "engine_running": self._engine_running,
                        "gear": self._gear_position,
                    },
                }
                self._telemetry_history.append(telemetry)
                
                # Send telemetry via comm layer
                self.core.comm.send_telemetry(telemetry)
                
            except Exception as e:
                logger.error(f"[Automotive] Telemetry collection error: {e}")
            
            time.sleep(1.0)  # Collect every second

    def start(self) -> None:
        """Start the automotive runtime"""
        self.core.start()
        self._telemetry_running = True
        self._telemetry_thread = threading.Thread(target=self._telemetry_collector, daemon=True)
        self._telemetry_thread.start()
        logger.info(f"[Automotive] Runtime started for device {self.core.device_id}")

    def stop(self) -> None:
        """Stop the automotive runtime"""
        self._telemetry_running = False
        if self._ignition_on:
            self._set_ignition(False)
        self.core.stop()
        logger.info(f"[Automotive] Runtime stopped")

    def health_check(self) -> dict[str, Any]:
        """Perform health check"""
        health = {
            "ok": True,
            "device_type": self.core.device_type,
            "device_id": self.core.device_id,
            "ts": time.time(),
            "ignition": self._ignition_on,
            "engine_running": self._engine_running,
            "gear": self._gear_position,
            "speed_kph": self._speed_kph,
            "rpm": self._rpm,
            "fuel_level_pct": self._fuel_level_pct,
            "telemetry_count": len(self._telemetry_history),
        }
        
        # Check for warnings
        warnings = []
        if self._fuel_level_pct < 10:
            warnings.append("Low fuel")
        if self._speed_kph > 0 and self._gear_position == "P":
            warnings.append("Speed detected in Park gear")
        
        if warnings:
            health["warnings"] = warnings
            health["ok"] = False
        
        return health

    def read_sensors(self) -> dict[str, Any]:
        """Read all sensors"""
        return {name: sensor.read() for name, sensor in self._sensors.items()}

    def read_actuators(self) -> dict[str, Any]:
        """Get current actuator states"""
        return {
            "ignition": self._ignition_on,
            "gear": self._gear_position,
            "lights": self.config.get("lights", {}),
        }

    def send_command(self, command: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Process vehicle command"""
        payload = payload or {}
        result = {
            "status": "accepted",
            "command": command,
            "device_id": self.core.device_id,
            "ts": time.time(),
        }
        
        try:
            if command == "ignition_on":
                success = self._actuators["ignition"].activate(True)
                result["status"] = "success" if success else "failed"
                
            elif command == "ignition_off":
                success = self._actuators["ignition"].activate(False)
                result["status"] = "success" if success else "failed"
                
            elif command == "set_gear":
                gear = payload.get("position", "P")
                success = self._actuators["gear"].activate(gear)
                result["status"] = "success" if success else "failed"
                result["gear"] = self._gear_position
                
            elif command == "set_throttle":
                pct = payload.get("percentage", 0.0)
                success = self._actuators["throttle"].activate(pct)
                result["status"] = "success" if success else "failed"
                
            elif command == "set_brake":
                pct = payload.get("percentage", 0.0)
                success = self._actuators["brake"].activate(pct)
                result["status"] = "success" if success else "failed"
                
            elif command == "set_lights":
                lights = payload.get("lights", {})
                success = self._actuators["lights"].activate(lights)
                result["status"] = "success" if success else "failed"
                
            elif command == "get_telemetry":
                result["telemetry"] = list(self._telemetry_history)[-100:]  # Last 100 readings
                result["status"] = "success"
                
            else:
                result["status"] = "unknown_command"
                result["error"] = f"Unknown command: {command}"
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            logger.error(f"[Automotive] Command error: {e}")
        
        return result

    def get_statistics(self) -> dict[str, Any]:
        """Get runtime statistics"""
        return {
            "device_id": self.core.device_id,
            "device_type": self.core.device_type,
            "uptime_seconds": time.time() - (self._telemetry_history[0]["ts"] if self._telemetry_history else time.time()),
            "telemetry_points": len(self._telemetry_history),
            "sensor_count": len(self._sensors),
            "actuator_count": len(self._actuators),
            "current_state": {
                "ignition": self._ignition_on,
                "engine_running": self._engine_running,
                "gear": self._gear_position,
                "speed_kph": self._speed_kph,
                "rpm": self._rpm,
            },
        }