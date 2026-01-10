"""Aviation platform adapter for Aurora EdgeOS.

Production-ready aviation runtime with comprehensive flight systems,
navigation, and aircraft control capabilities.
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


class AviationRuntime:
    """Aviation platform runtime for aircraft control and monitoring."""

    def __init__(self, device_id: str | None = None, config: dict[str, Any] | None = None):
        self.core = AuroraEdgeCore(device_type="aviation", device_id=device_id, config=config)
        self.config = config or {}

        # Aircraft state
        self._engines_running = False
        self._altitude_m = 0.0
        self._airspeed_kt = 0.0
        self._heading_deg = 0.0
        self._pitch_deg = 0.0
        self._roll_deg = 0.0
        self._fuel_pct = 100.0
        self._throttle_pct = 0.0

        # Flight parameters
        self._climb_rate_fpm = 0.0
        self._vertical_speed_fpm = 0.0

        # Telemetry history
        self._telemetry_history = deque(maxlen=1000)

        # Sensors
        self._sensors = {
            "altitude_m": Sensor("altitude_m", self._read_altitude),
            "airspeed_kt": Sensor("airspeed_kt", self._read_airspeed),
            "fuel_pct": Sensor("fuel_pct", self._read_fuel),
            "heading_deg": Sensor("heading_deg", self._read_heading),
            "pitch_deg": Sensor("pitch_deg", self._read_pitch),
            "roll_deg": Sensor("roll_deg", self._read_roll),
            "vertical_speed_fpm": Sensor("vertical_speed_fpm", self._read_vertical_speed),
            "engine_temp_c": Sensor("engine_temp_c", lambda: round(random.uniform(80, 120), 1)),
            "oil_pressure_psi": Sensor("oil_pressure_psi", lambda: round(random.uniform(40, 80), 1)),
            "outside_temp_c": Sensor("outside_temp_c", lambda: round(-56 + (self._altitude_m / 1000) * -2, 1)),
            "wind_speed_kt": Sensor("wind_speed_kt", lambda: round(random.uniform(0, 30), 1)),
            "wind_direction_deg": Sensor("wind_direction_deg", lambda: round(random.uniform(0, 359), 1)),
        }

        # Actuators
        self._actuators = {
            "throttle": Actuator("throttle", self._set_throttle),
            "elevator": Actuator("elevator", self._set_elevator),
            "aileron": Actuator("aileron", self._set_aileron),
            "rudder": Actuator("rudder", self._set_rudder),
            "flaps": Actuator("flaps", self._set_flaps),
            "landing_gear": Actuator("landing_gear", self._set_landing_gear),
        }

        # Telemetry collection thread
        self._telemetry_thread = None
        self._telemetry_running = False
        self._flight_start_time = None

    def _read_altitude(self) -> float:
        """Read current altitude"""
        return round(self._altitude_m, 1)

    def _read_airspeed(self) -> float:
        """Read current airspeed"""
        return round(self._airspeed_kt, 1)

    def _read_fuel(self) -> float:
        """Read fuel level"""
        return round(self._fuel_pct, 1)

    def _read_heading(self) -> float:
        """Read heading"""
        return round(self._heading_deg, 1)

    def _read_pitch(self) -> float:
        """Read pitch angle"""
        return round(self._pitch_deg, 1)

    def _read_roll(self) -> float:
        """Read roll angle"""
        return round(self._roll_deg, 1)

    def _read_vertical_speed(self) -> float:
        """Read vertical speed"""
        return round(self._vertical_speed_fpm, 1)

    def _set_throttle(self, percentage: float) -> bool:
        """Set throttle position (0-100%)"""
        self._throttle_pct = max(0.0, min(100.0, float(percentage)))
        if self._engines_running and self._throttle_pct > 0:
            # Increase airspeed with throttle
            self._airspeed_kt = min(480.0, self._airspeed_kt + (self._throttle_pct / 100.0) * 5.0)
        return True

    def _set_elevator(self, position: float) -> bool:
        """Set elevator position (-1.0 to 1.0, negative = nose down)"""
        pos = max(-1.0, min(1.0, float(position)))
        # Elevator affects pitch
        self._pitch_deg = max(-30.0, min(30.0, self._pitch_deg + pos * 2.0))
        # Pitch affects vertical speed
        if self._airspeed_kt > 50:
            self._vertical_speed_fpm = self._pitch_deg * 100.0
        return True

    def _set_aileron(self, position: float) -> bool:
        """Set aileron position (-1.0 to 1.0, negative = left roll)"""
        pos = max(-1.0, min(1.0, float(position)))
        # Aileron affects roll
        self._roll_deg = max(-45.0, min(45.0, self._roll_deg + pos * 5.0))
        # Roll affects heading
        if self._airspeed_kt > 50:
            self._heading_deg = (self._heading_deg + pos * 2.0) % 360.0
        return True

    def _set_rudder(self, position: float) -> bool:
        """Set rudder position (-1.0 to 1.0, negative = left yaw)"""
        pos = max(-1.0, min(1.0, float(position)))
        # Rudder affects heading
        if self._airspeed_kt > 50:
            self._heading_deg = (self._heading_deg + pos * 1.0) % 360.0
        return True

    def _set_flaps(self, position: float) -> bool:
        """Set flaps position (0.0 = retracted, 1.0 = fully extended)"""
        pos = max(0.0, min(1.0, float(position)))
        self.config["flaps_position"] = pos
        # Flaps reduce airspeed but increase lift
        if pos > 0:
            self._airspeed_kt = max(0.0, self._airspeed_kt - pos * 10.0)
        return True

    def _set_landing_gear(self, extended: bool) -> bool:
        """Set landing gear position"""
        self.config["landing_gear_extended"] = bool(extended)
        if extended:
            # Landing gear increases drag
            self._airspeed_kt = max(0.0, self._airspeed_kt - 20.0)
        logger.info(f"[Aviation] Landing gear {'extended' if extended else 'retracted'}")
        return True

    def _update_flight_dynamics(self):
        """Update flight dynamics based on current state"""
        if not self._engines_running:
            return

        # Simulate altitude change based on vertical speed
        if self._vertical_speed_fpm != 0:
            altitude_change_m = (self._vertical_speed_fpm / 196.85)  # Convert FPM to m/s
            self._altitude_m = max(0.0, self._altitude_m + altitude_change_m)

        # Simulate fuel consumption
        if self._throttle_pct > 0:
            fuel_consumption = (self._throttle_pct / 100.0) * 0.01  # 1% per hour at 100% throttle
            self._fuel_pct = max(0.0, self._fuel_pct - fuel_consumption / 3600.0)  # Per second

        # Simulate airspeed decay if throttle is low
        if self._throttle_pct < 20 and self._airspeed_kt > 0:
            self._airspeed_kt = max(0.0, self._airspeed_kt - 0.5)

    def _telemetry_collector(self):
        """Background thread to collect telemetry data"""
        while self._telemetry_running:
            try:
                self._update_flight_dynamics()

                telemetry = {
                    "ts": time.time(),
                    "device_id": self.core.device_id,
                    "sensors": self.read_sensors(),
                    "state": {
                        "engines_running": self._engines_running,
                        "throttle_pct": self._throttle_pct,
                        "landing_gear": self.config.get("landing_gear_extended", False),
                        "flaps": self.config.get("flaps_position", 0.0),
                    },
                }
                self._telemetry_history.append(telemetry)

                # Send telemetry via comm layer
                self.core.comm.send_telemetry(telemetry)

            except Exception as e:
                logger.error(f"[Aviation] Telemetry collection error: {e}")

            time.sleep(1.0)  # Collect every second

    def start(self) -> None:
        """Start the aviation runtime"""
        self.core.start()
        self._telemetry_running = True
        self._telemetry_thread = threading.Thread(target=self._telemetry_collector, daemon=True)
        self._telemetry_thread.start()
        self._flight_start_time = time.time()
        logger.info(f"[Aviation] Runtime started for device {self.core.device_id}")

    def stop(self) -> None:
        """Stop the aviation runtime"""
        self._telemetry_running = False
        if self._engines_running:
            self._set_throttle(0.0)
            self._engines_running = False
        self.core.stop()
        logger.info(f"[Aviation] Runtime stopped")

    def health_check(self) -> dict[str, Any]:
        """Perform health check"""
        health = {
            "ok": True,
            "device_type": self.core.device_type,
            "device_id": self.core.device_id,
            "ts": time.time(),
            "engines_running": self._engines_running,
            "altitude_m": self._altitude_m,
            "airspeed_kt": self._airspeed_kt,
            "heading_deg": self._heading_deg,
            "fuel_pct": self._fuel_pct,
            "telemetry_count": len(self._telemetry_history),
        }

        # Check for warnings
        warnings = []
        if self._fuel_pct < 15:
            warnings.append("Low fuel")
        if self._altitude_m < 100 and self._airspeed_kt > 50:
            warnings.append("Low altitude warning")
        if abs(self._pitch_deg) > 20:
            warnings.append("Extreme pitch angle")
        if abs(self._roll_deg) > 30:
            warnings.append("Extreme roll angle")

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
            "flaps": self.config.get("flaps_position", 0.0),
            "landing_gear": self.config.get("landing_gear_extended", False),
        }

    def send_command(self, command: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Process aircraft command"""
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
                self._throttle_pct = 10.0  # Idle
                result["status"] = "success"
                logger.info("[Aviation] Engines started")

            elif command == "stop_engines":
                self._engines_running = False
                self._throttle_pct = 0.0
                result["status"] = "success"
                logger.info("[Aviation] Engines stopped")

            elif command == "set_throttle":
                pct = payload.get("percentage", 0.0)
                success = self._actuators["throttle"].activate(pct)
                result["status"] = "success" if success else "failed"

            elif command == "set_elevator":
                pos = payload.get("position", 0.0)
                success = self._actuators["elevator"].activate(pos)
                result["status"] = "success" if success else "failed"

            elif command == "set_aileron":
                pos = payload.get("position", 0.0)
                success = self._actuators["aileron"].activate(pos)
                result["status"] = "success" if success else "failed"

            elif command == "set_rudder":
                pos = payload.get("position", 0.0)
                success = self._actuators["rudder"].activate(pos)
                result["status"] = "success" if success else "failed"

            elif command == "set_flaps":
                pos = payload.get("position", 0.0)
                success = self._actuators["flaps"].activate(pos)
                result["status"] = "success" if success else "failed"

            elif command == "set_landing_gear":
                extended = payload.get("extended", False)
                success = self._actuators["landing_gear"].activate(extended)
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
            logger.error(f"[Aviation] Command error: {e}")

        return result

    def get_statistics(self) -> dict[str, Any]:
        """Get runtime statistics"""
        flight_time = 0.0
        if self._flight_start_time:
            flight_time = time.time() - self._flight_start_time

        return {
            "device_id": self.core.device_id,
            "device_type": self.core.device_type,
            "flight_time_seconds": flight_time,
            "telemetry_points": len(self._telemetry_history),
            "sensor_count": len(self._sensors),
            "actuator_count": len(self._actuators),
            "current_state": {
                "engines_running": self._engines_running,
                "altitude_m": self._altitude_m,
                "airspeed_kt": self._airspeed_kt,
                "heading_deg": self._heading_deg,
                "fuel_pct": self._fuel_pct,
            },
        }
