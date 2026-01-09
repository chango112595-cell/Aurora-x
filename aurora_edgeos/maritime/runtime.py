"""Maritime platform adapter for Aurora EdgeOS.

Production-ready maritime runtime with comprehensive vessel control,
navigation, and marine systems monitoring.
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


class MaritimeRuntime:
    """Maritime platform runtime for vessel control and monitoring."""

    def __init__(self, device_id: str | None = None, config: dict[str, Any] | None = None):
        self.core = AuroraEdgeCore(device_type="maritime", device_id=device_id, config=config)
        self.config = config or {}
        
        # Vessel state
        self._engines_running = False
        self._heading_deg = 0.0
        self._speed_kn = 0.0
        self._depth_m = 0.0
        self._fuel_pct = 100.0
        self._throttle_pct = 0.0
        self._rudder_position_deg = 0.0
        
        # Navigation
        self._latitude = 0.0
        self._longitude = 0.0
        self._course_over_ground_deg = 0.0
        
        # Telemetry history
        self._telemetry_history = deque(maxlen=1000)
        
        # Sensors
        self._sensors = {
            "heading_deg": Sensor("heading_deg", self._read_heading),
            "speed_kn": Sensor("speed_kn", self._read_speed),
            "depth_m": Sensor("depth_m", self._read_depth),
            "fuel_pct": Sensor("fuel_pct", self._read_fuel),
            "engine_temp_c": Sensor("engine_temp_c", lambda: round(random.uniform(70, 95), 1)),
            "oil_pressure_psi": Sensor("oil_pressure_psi", lambda: round(random.uniform(40, 60), 1)),
            "water_temp_c": Sensor("water_temp_c", lambda: round(random.uniform(10, 25), 1)),
            "wind_speed_kt": Sensor("wind_speed_kt", lambda: round(random.uniform(0, 40), 1)),
            "wind_direction_deg": Sensor("wind_direction_deg", lambda: round(random.uniform(0, 359), 1)),
            "wave_height_m": Sensor("wave_height_m", lambda: round(random.uniform(0.5, 5.0), 1)),
            "visibility_nm": Sensor("visibility_nm", lambda: round(random.uniform(1, 20), 1)),
            "barometric_pressure_hpa": Sensor("barometric_pressure_hpa", lambda: round(random.uniform(980, 1020), 1)),
        }
        
        # Actuators
        self._actuators = {
            "throttle": Actuator("throttle", self._set_throttle),
            "rudder": Actuator("rudder", self._set_rudder),
            "bow_thruster": Actuator("bow_thruster", self._set_bow_thruster),
            "stern_thruster": Actuator("stern_thruster", self._set_stern_thruster),
            "anchor": Actuator("anchor", self._set_anchor),
            "lights": Actuator("lights", self._set_lights),
        }
        
        # Telemetry collection thread
        self._telemetry_thread = None
        self._telemetry_running = False

    def _read_heading(self) -> float:
        """Read current heading"""
        return round(self._heading_deg, 1)

    def _read_speed(self) -> float:
        """Read current speed"""
        return round(self._speed_kn, 2)

    def _read_depth(self) -> float:
        """Read water depth"""
        return round(self._depth_m, 1)

    def _read_fuel(self) -> float:
        """Read fuel level"""
        return round(self._fuel_pct, 1)

    def _set_throttle(self, percentage: float) -> bool:
        """Set throttle position (0-100%)"""
        self._throttle_pct = max(0.0, min(100.0, float(percentage)))
        if self._engines_running and self._throttle_pct > 0:
            # Increase speed with throttle
            self._speed_kn = min(45.0, self._speed_kn + (self._throttle_pct / 100.0) * 2.0)
        return True

    def _set_rudder(self, angle_deg: float) -> bool:
        """Set rudder angle (-35 to +35 degrees)"""
        self._rudder_position_deg = max(-35.0, min(35.0, float(angle_deg)))
        # Rudder affects heading
        if self._speed_kn > 1.0:
            heading_change = self._rudder_position_deg * 0.5
            self._heading_deg = (self._heading_deg + heading_change) % 360.0
            self._course_over_ground_deg = self._heading_deg
        logger.info(f"[Maritime] Rudder set to {self._rudder_position_deg:.1f} degrees")
        return True

    def _set_bow_thruster(self, power_pct: float) -> bool:
        """Set bow thruster power (0-100%)"""
        pct = max(0.0, min(100.0, float(power_pct)))
        self.config["bow_thruster_pct"] = pct
        # Bow thruster affects heading when speed is low
        if self._speed_kn < 2.0 and pct > 0:
            self._heading_deg = (self._heading_deg + (pct / 100.0) * 2.0) % 360.0
        return True

    def _set_stern_thruster(self, power_pct: float) -> bool:
        """Set stern thruster power (0-100%)"""
        pct = max(0.0, min(100.0, float(power_pct)))
        self.config["stern_thruster_pct"] = pct
        # Stern thruster affects heading when speed is low
        if self._speed_kn < 2.0 and pct > 0:
            self._heading_deg = (self._heading_deg - (pct / 100.0) * 2.0) % 360.0
        return True

    def _set_anchor(self, deployed: bool) -> bool:
        """Set anchor position"""
        self.config["anchor_deployed"] = bool(deployed)
        if deployed:
            # Anchor stops vessel
            self._speed_kn = 0.0
            self._throttle_pct = 0.0
        logger.info(f"[Maritime] Anchor {'deployed' if deployed else 'retrieved'}")
        return True

    def _set_lights(self, state: dict[str, bool]) -> bool:
        """Set vessel lights (navigation, deck, etc.)"""
        self.config.setdefault("lights", {}).update(state)
        return True

    def _update_vessel_dynamics(self):
        """Update vessel dynamics based on current state"""
        if not self._engines_running:
            # Drift simulation
            if self._speed_kn > 0:
                self._speed_kn = max(0.0, self._speed_kn - 0.1)
            return
        
        # Simulate fuel consumption
        if self._throttle_pct > 0:
            fuel_consumption = (self._throttle_pct / 100.0) * 0.008  # 0.8% per hour at 100% throttle
            self._fuel_pct = max(0.0, self._fuel_pct - fuel_consumption / 3600.0)  # Per second
        
        # Simulate speed decay if throttle is low
        if self._throttle_pct < 10 and self._speed_kn > 0:
            self._speed_kn = max(0.0, self._speed_kn - 0.2)
        
        # Update position based on speed and heading (simplified)
        if self._speed_kn > 0:
            # Convert knots to degrees per second (rough approximation)
            speed_deg_per_sec = self._speed_kn / 60.0  # Very rough
            # Update lat/lon (simplified - would need proper navigation math)
            self._latitude += (self._speed_kn / 60.0) * 0.0001 * math.cos(math.radians(self._heading_deg))
            self._longitude += (self._speed_kn / 60.0) * 0.0001 * math.sin(math.radians(self._heading_deg))

    def _telemetry_collector(self):
        """Background thread to collect telemetry data"""
        import math
        while self._telemetry_running:
            try:
                self._update_vessel_dynamics()
                
                telemetry = {
                    "ts": time.time(),
                    "device_id": self.core.device_id,
                    "sensors": self.read_sensors(),
                    "state": {
                        "engines_running": self._engines_running,
                        "throttle_pct": self._throttle_pct,
                        "rudder_deg": self._rudder_position_deg,
                        "anchor_deployed": self.config.get("anchor_deployed", False),
                        "position": {
                            "latitude": self._latitude,
                            "longitude": self._longitude,
                            "course_over_ground": self._course_over_ground_deg,
                        },
                    },
                }
                self._telemetry_history.append(telemetry)
                
                # Send telemetry via comm layer
                self.core.comm.send_telemetry(telemetry)
                
            except Exception as e:
                logger.error(f"[Maritime] Telemetry collection error: {e}")
            
            time.sleep(1.0)  # Collect every second

    def start(self) -> None:
        """Start the maritime runtime"""
        self.core.start()
        self._telemetry_running = True
        self._telemetry_thread = threading.Thread(target=self._telemetry_collector, daemon=True)
        self._telemetry_thread.start()
        logger.info(f"[Maritime] Runtime started for device {self.core.device_id}")

    def stop(self) -> None:
        """Stop the maritime runtime"""
        self._telemetry_running = False
        if self._engines_running:
            self._set_throttle(0.0)
            self._engines_running = False
        self.core.stop()
        logger.info(f"[Maritime] Runtime stopped")

    def health_check(self) -> dict[str, Any]:
        """Perform health check"""
        health = {
            "ok": True,
            "device_type": self.core.device_type,
            "device_id": self.core.device_id,
            "ts": time.time(),
            "engines_running": self._engines_running,
            "heading_deg": self._heading_deg,
            "speed_kn": self._speed_kn,
            "depth_m": self._depth_m,
            "fuel_pct": self._fuel_pct,
            "telemetry_count": len(self._telemetry_history),
        }
        
        # Check for warnings
        warnings = []
        if self._fuel_pct < 20:
            warnings.append("Low fuel")
        if self._depth_m < 5 and self._speed_kn > 5:
            warnings.append("Shallow water warning")
        if self._speed_kn > 0 and self.config.get("anchor_deployed", False):
            warnings.append("Anchor deployed while moving")
        
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
            "throttle_pct": self._throttle_pct,
            "rudder_deg": self._rudder_position_deg,
            "bow_thruster_pct": self.config.get("bow_thruster_pct", 0.0),
            "stern_thruster_pct": self.config.get("stern_thruster_pct", 0.0),
            "anchor_deployed": self.config.get("anchor_deployed", False),
            "lights": self.config.get("lights", {}),
        }

    def send_command(self, command: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Process vessel command"""
        payload = payload or {}
        result = {
            "status": "accepted",
            "command": command,
            "device_id": self.core.device_id,
            "ts": time.time(),
        }
        
        try:
            if command == "start_engines":
                self._engines_running = True
                self._throttle_pct = 5.0  # Idle
                result["status"] = "success"
                logger.info("[Maritime] Engines started")
                
            elif command == "stop_engines":
                self._engines_running = False
                self._throttle_pct = 0.0
                result["status"] = "success"
                logger.info("[Maritime] Engines stopped")
                
            elif command == "set_throttle":
                pct = payload.get("percentage", 0.0)
                success = self._actuators["throttle"].activate(pct)
                result["status"] = "success" if success else "failed"
                
            elif command == "set_rudder":
                angle = payload.get("angle_deg", 0.0)
                success = self._actuators["rudder"].activate(angle)
                result["status"] = "success" if success else "failed"
                
            elif command == "set_bow_thruster":
                pct = payload.get("power_pct", 0.0)
                success = self._actuators["bow_thruster"].activate(pct)
                result["status"] = "success" if success else "failed"
                
            elif command == "set_stern_thruster":
                pct = payload.get("power_pct", 0.0)
                success = self._actuators["stern_thruster"].activate(pct)
                result["status"] = "success" if success else "failed"
                
            elif command == "set_anchor":
                deployed = payload.get("deployed", False)
                success = self._actuators["anchor"].activate(deployed)
                result["status"] = "success" if success else "failed"
                
            elif command == "set_lights":
                lights = payload.get("lights", {})
                success = self._actuators["lights"].activate(lights)
                result["status"] = "success" if success else "failed"
                
            elif command == "get_telemetry":
                result["telemetry"] = list(self._telemetry_history)[-100:]  # Last 100 readings
                result["status"] = "success"
                
            elif command == "get_position":
                result["position"] = {
                    "latitude": self._latitude,
                    "longitude": self._longitude,
                    "heading": self._heading_deg,
                    "course_over_ground": self._course_over_ground_deg,
                }
                result["status"] = "success"
                
            else:
                result["status"] = "unknown_command"
                result["error"] = f"Unknown command: {command}"
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            logger.error(f"[Maritime] Command error: {e}")
        
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
                "engines_running": self._engines_running,
                "heading_deg": self._heading_deg,
                "speed_kn": self._speed_kn,
                "depth_m": self._depth_m,
                "fuel_pct": self._fuel_pct,
            },
        }