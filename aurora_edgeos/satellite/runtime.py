"""Satellite platform adapter for Aurora EdgeOS.

Production-ready satellite runtime with comprehensive orbital mechanics,
payload control, and space systems monitoring.
"""

from __future__ import annotations

import logging
import math
import random
import threading
import time
from collections import deque
from typing import Any

from aurora_edgeos.core.edge_core import AuroraEdgeCore
from aurora_edgeos.hal.actuator import Actuator
from aurora_edgeos.hal.sensor import Sensor

logger = logging.getLogger(__name__)


class SatelliteRuntime:
    """Satellite platform runtime for spacecraft control and monitoring."""

    def __init__(self, device_id: str | None = None, config: dict[str, Any] | None = None):
        self.core = AuroraEdgeCore(device_type="satellite", device_id=device_id, config=config)
        self.config = config or {}
        
        # Orbital parameters
        self._orbit_altitude_km = 400.0  # Low Earth Orbit default
        self._orbital_period_min = 90.0  # ~90 minutes for LEO
        self._inclination_deg = 51.6  # ISS-like inclination
        self._true_anomaly_deg = 0.0  # Position in orbit
        
        # Satellite state
        self._battery_pct = 100.0
        self._solar_power_w = 0.0
        self._temp_c = -40.0
        self._attitude_roll_deg = 0.0
        self._attitude_pitch_deg = 0.0
        self._attitude_yaw_deg = 0.0
        
        # Payload state
        self._payload_active = False
        self._antenna_deployed = True
        self._solar_panels_deployed = True
        
        # Telemetry history
        self._telemetry_history = deque(maxlen=1000)
        
        # Sensors
        self._sensors = {
            "orbit_altitude_km": Sensor("orbit_altitude_km", self._read_altitude),
            "battery_pct": Sensor("battery_pct", self._read_battery),
            "temp_c": Sensor("temp_c", self._read_temp),
            "solar_power_w": Sensor("solar_power_w", self._read_solar_power),
            "attitude_roll_deg": Sensor("attitude_roll_deg", self._read_roll),
            "attitude_pitch_deg": Sensor("attitude_pitch_deg", self._read_pitch),
            "attitude_yaw_deg": Sensor("attitude_yaw_deg", self._read_yaw),
            "radiation_level_sv": Sensor("radiation_level_sv", lambda: round(random.uniform(0.001, 0.01), 4)),
            "magnetic_field_nt": Sensor("magnetic_field_nt", lambda: round(random.uniform(20000, 50000), 1)),
            "earth_visible_pct": Sensor("earth_visible_pct", self._read_earth_visibility),
        }
        
        # Actuators
        self._actuators = {
            "reaction_wheels": Actuator("reaction_wheels", self._set_reaction_wheels),
            "magnetorquers": Actuator("magnetorquers", self._set_magnetorquers),
            "thrusters": Actuator("thrusters", self._set_thrusters),
            "payload": Actuator("payload", self._set_payload),
            "antenna": Actuator("antenna", self._set_antenna),
            "solar_panels": Actuator("solar_panels", self._set_solar_panels),
        }
        
        # Telemetry collection thread
        self._telemetry_thread = None
        self._telemetry_running = False
        self._mission_start_time = None

    def _read_altitude(self) -> float:
        """Read current orbital altitude"""
        return round(self._orbit_altitude_km, 2)

    def _read_battery(self) -> float:
        """Read battery level"""
        return round(self._battery_pct, 1)

    def _read_temp(self) -> float:
        """Read temperature"""
        return round(self._temp_c, 1)

    def _read_solar_power(self) -> float:
        """Read solar power generation"""
        return round(self._solar_power_w, 1)

    def _read_roll(self) -> float:
        """Read roll attitude"""
        return round(self._attitude_roll_deg, 1)

    def _read_pitch(self) -> float:
        """Read pitch attitude"""
        return round(self._attitude_pitch_deg, 1)

    def _read_yaw(self) -> float:
        """Read yaw attitude"""
        return round(self._attitude_yaw_deg, 1)

    def _read_earth_visibility(self) -> float:
        """Calculate Earth visibility percentage"""
        # Simplified: based on altitude and position
        # Higher altitude = more Earth visible
        visibility = min(100.0, (self._orbit_altitude_km / 1000.0) * 25.0)
        return round(visibility, 1)

    def _set_reaction_wheels(self, command: dict[str, float]) -> bool:
        """Set reaction wheel speeds (x, y, z in rad/s)"""
        # Reaction wheels control attitude
        if "x" in command:
            self._attitude_roll_deg = max(-180.0, min(180.0, self._attitude_roll_deg + command["x"] * 10.0))
        if "y" in command:
            self._attitude_pitch_deg = max(-180.0, min(180.0, self._attitude_pitch_deg + command["y"] * 10.0))
        if "z" in command:
            self._attitude_yaw_deg = max(-180.0, min(180.0, self._attitude_yaw_deg + command["z"] * 10.0))
        return True

    def _set_magnetorquers(self, command: dict[str, float]) -> bool:
        """Set magnetorquer currents (x, y, z in Amperes)"""
        # Magnetorquers use Earth's magnetic field for attitude control
        self.config["magnetorquer_currents"] = command
        return True

    def _set_thrusters(self, command: dict[str, float]) -> bool:
        """Fire thrusters (delta_v in m/s)"""
        delta_v = command.get("delta_v", 0.0)
        if delta_v > 0:
            # Thrusters change orbital parameters
            # Simplified: increase altitude with positive delta_v
            self._orbit_altitude_km = min(2000.0, self._orbit_altitude_km + delta_v * 0.001)
            logger.info(f"[Satellite] Thrusters fired: delta_v={delta_v} m/s")
        return True

    def _set_payload(self, active: bool) -> bool:
        """Activate/deactivate payload"""
        self._payload_active = bool(active)
        logger.info(f"[Satellite] Payload {'activated' if active else 'deactivated'}")
        return True

    def _set_antenna(self, deployed: bool) -> bool:
        """Deploy/retract antenna"""
        self._antenna_deployed = bool(deployed)
        logger.info(f"[Satellite] Antenna {'deployed' if deployed else 'retracted'}")
        return True

    def _set_solar_panels(self, deployed: bool) -> bool:
        """Deploy/retract solar panels"""
        self._solar_panels_deployed = bool(deployed)
        if deployed:
            # Solar panels generate power
            self._solar_power_w = 500.0  # Simplified
        else:
            self._solar_power_w = 0.0
        logger.info(f"[Satellite] Solar panels {'deployed' if deployed else 'retracted'}")
        return True

    def _update_orbital_mechanics(self):
        """Update orbital mechanics based on current state"""
        # Simulate orbital motion
        # Advance true anomaly based on orbital period
        time_step_sec = 1.0
        degrees_per_sec = 360.0 / (self._orbital_period_min * 60.0)
        self._true_anomaly_deg = (self._true_anomaly_deg + degrees_per_sec * time_step_sec) % 360.0
        
        # Simulate solar power generation (depends on sun angle)
        if self._solar_panels_deployed:
            # Simplified: power varies with orbital position
            sun_angle_factor = abs(math.cos(math.radians(self._true_anomaly_deg)))
            self._solar_power_w = 500.0 * sun_angle_factor
        else:
            self._solar_power_w = 0.0
        
        # Battery management
        if self._solar_power_w > 0:
            # Charging
            charge_rate = (self._solar_power_w / 1000.0) * 0.1  # 0.1% per 100W per second
            self._battery_pct = min(100.0, self._battery_pct + charge_rate)
        else:
            # Discharging (payload and systems consume power)
            discharge_rate = 0.01 if self._payload_active else 0.005  # % per second
            self._battery_pct = max(0.0, self._battery_pct - discharge_rate)
        
        # Temperature simulation (varies with sun exposure)
        base_temp = -40.0
        sun_heating = sun_angle_factor * 50.0  # Up to 50C heating in sunlight
        self._temp_c = base_temp + sun_heating

    def _telemetry_collector(self):
        """Background thread to collect telemetry data"""
        while self._telemetry_running:
            try:
                self._update_orbital_mechanics()
                
                telemetry = {
                    "ts": time.time(),
                    "device_id": self.core.device_id,
                    "sensors": self.read_sensors(),
                    "state": {
                        "payload_active": self._payload_active,
                        "antenna_deployed": self._antenna_deployed,
                        "solar_panels_deployed": self._solar_panels_deployed,
                        "orbital_position": {
                            "altitude_km": self._orbit_altitude_km,
                            "true_anomaly_deg": self._true_anomaly_deg,
                            "inclination_deg": self._inclination_deg,
                        },
                        "attitude": {
                            "roll": self._attitude_roll_deg,
                            "pitch": self._attitude_pitch_deg,
                            "yaw": self._attitude_yaw_deg,
                        },
                    },
                }
                self._telemetry_history.append(telemetry)
                
                # Send telemetry via comm layer
                self.core.comm.send_telemetry(telemetry)
                
            except Exception as e:
                logger.error(f"[Satellite] Telemetry collection error: {e}")
            
            time.sleep(1.0)  # Collect every second

    def start(self) -> None:
        """Start the satellite runtime"""
        self.core.start()
        self._telemetry_running = True
        self._telemetry_thread = threading.Thread(target=self._telemetry_collector, daemon=True)
        self._telemetry_thread.start()
        self._mission_start_time = time.time()
        logger.info(f"[Satellite] Runtime started for device {self.core.device_id}")

    def stop(self) -> None:
        """Stop the satellite runtime"""
        self._telemetry_running = False
        if self._payload_active:
            self._set_payload(False)
        self.core.stop()
        logger.info(f"[Satellite] Runtime stopped")

    def health_check(self) -> dict[str, Any]:
        """Perform health check"""
        health = {
            "ok": True,
            "device_type": self.core.device_type,
            "device_id": self.core.device_id,
            "ts": time.time(),
            "battery_pct": self._battery_pct,
            "temp_c": self._temp_c,
            "solar_power_w": self._solar_power_w,
            "orbit_altitude_km": self._orbit_altitude_km,
            "telemetry_count": len(self._telemetry_history),
        }
        
        # Check for warnings
        warnings = []
        if self._battery_pct < 20:
            warnings.append("Low battery")
        if self._battery_pct < 10:
            warnings.append("Critical battery level")
        if abs(self._temp_c) > 60:
            warnings.append("Extreme temperature")
        if not self._solar_panels_deployed and self._battery_pct < 50:
            warnings.append("Solar panels retracted with low battery")
        
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
            "payload_active": self._payload_active,
            "antenna_deployed": self._antenna_deployed,
            "solar_panels_deployed": self._solar_panels_deployed,
            "magnetorquer_currents": self.config.get("magnetorquer_currents", {}),
        }

    def send_command(self, command: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Process satellite command"""
        payload = payload or {}
        result = {
            "status": "accepted",
            "command": command,
            "device_id": self.core.device_id,
            "ts": time.time(),
        }
        
        try:
            if command == "activate_payload":
                success = self._actuators["payload"].activate(True)
                result["status"] = "success" if success else "failed"
                
            elif command == "deactivate_payload":
                success = self._actuators["payload"].activate(False)
                result["status"] = "success" if success else "failed"
                
            elif command == "deploy_antenna":
                success = self._actuators["antenna"].activate(True)
                result["status"] = "success" if success else "failed"
                
            elif command == "retract_antenna":
                success = self._actuators["antenna"].activate(False)
                result["status"] = "success" if success else "failed"
                
            elif command == "deploy_solar_panels":
                success = self._actuators["solar_panels"].activate(True)
                result["status"] = "success" if success else "failed"
                
            elif command == "retract_solar_panels":
                success = self._actuators["solar_panels"].activate(False)
                result["status"] = "success" if success else "failed"
                
            elif command == "set_reaction_wheels":
                success = self._actuators["reaction_wheels"].activate(payload)
                result["status"] = "success" if success else "failed"
                
            elif command == "set_magnetorquers":
                success = self._actuators["magnetorquers"].activate(payload)
                result["status"] = "success" if success else "failed"
                
            elif command == "fire_thrusters":
                success = self._actuators["thrusters"].activate(payload)
                result["status"] = "success" if success else "failed"
                result["new_altitude_km"] = self._orbit_altitude_km
                
            elif command == "get_telemetry":
                result["telemetry"] = list(self._telemetry_history)[-100:]  # Last 100 readings
                result["status"] = "success"
                
            elif command == "get_orbital_elements":
                result["orbital_elements"] = {
                    "altitude_km": self._orbit_altitude_km,
                    "period_min": self._orbital_period_min,
                    "inclination_deg": self._inclination_deg,
                    "true_anomaly_deg": self._true_anomaly_deg,
                }
                result["status"] = "success"
                
            else:
                result["status"] = "unknown_command"
                result["error"] = f"Unknown command: {command}"
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            logger.error(f"[Satellite] Command error: {e}")
        
        return result

    def get_statistics(self) -> dict[str, Any]:
        """Get runtime statistics"""
        mission_time = 0.0
        if self._mission_start_time:
            mission_time = time.time() - self._mission_start_time
        
        return {
            "device_id": self.core.device_id,
            "device_type": self.core.device_type,
            "mission_time_seconds": mission_time,
            "orbits_completed": int(mission_time / (self._orbital_period_min * 60.0)),
            "telemetry_points": len(self._telemetry_history),
            "sensor_count": len(self._sensors),
            "actuator_count": len(self._actuators),
            "current_state": {
                "altitude_km": self._orbit_altitude_km,
                "battery_pct": self._battery_pct,
                "temp_c": self._temp_c,
                "payload_active": self._payload_active,
            },
        }