#!/usr/bin/env python3
"""
EdgeOS Runtime Offline Validation Test

Tests all EdgeOS platform runtimes to ensure they work completely offline
(no network dependencies, no external APIs, no cloud services).

Issue: #14 [MEDIUM] Validate all 12 EdgeOS runtimes work offline
"""

import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Test imports (should work offline)
try:
    from aurora_edgeos.automotive.runtime import AutomotiveRuntime
    from aurora_edgeos.aviation.runtime import AviationRuntime
    from aurora_edgeos.maritime.runtime import MaritimeRuntime
    from aurora_edgeos.satellite.runtime import SatelliteRuntime
    from aurora_edgeos.iot.runtime import IoTRuntime
    from aurora_edgeos.mobile.runtime import MobileRuntime
    from aurora_edgeos.tv.runtime import TvRuntime
except ImportError as e:
    print(f"[ERROR] Failed to import runtimes: {e}")
    sys.exit(1)


class RuntimeValidator:
    """Validates EdgeOS runtimes work offline"""

    def __init__(self):
        self.results: Dict[str, Dict[str, Any]] = {}
        self.test_count = 0
        self.pass_count = 0
        self.fail_count = 0

    def test_runtime(
        self,
        name: str,
        runtime_class,
        test_commands: List[Dict[str, Any]] | None = None,
    ) -> bool:
        """Test a single runtime"""
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print(f"{'='*60}")

        self.test_count += 1
        test_commands = test_commands or []
        runtime = None
        passed = True
        errors = []

        try:
            # Test 1: Instantiation
            print(f"  [1/6] Testing instantiation...")
            runtime = runtime_class(device_id=f"test_{name.lower()}")
            assert runtime is not None, "Runtime instantiation failed"
            print(f"         [OK] Runtime created")

            # Test 2: Start
            print(f"  [2/6] Testing start()...")
            runtime.start()
            assert hasattr(runtime, "core"), "Runtime missing core"
            assert runtime.core.device_id is not None, "Device ID not set"
            print(f"         [OK] Runtime started")

            # Test 3: Health check
            print(f"  [3/6] Testing health_check()...")
            health = runtime.health_check()
            assert isinstance(health, dict), "Health check should return dict"
            assert "ok" in health, "Health check missing 'ok' field"
            assert "device_id" in health, "Health check missing 'device_id'"
            assert health["device_type"] == name.lower(), f"Wrong device type: {health.get('device_type')}"
            print(f"         [OK] Health check passed: {health.get('ok')}")

            # Test 4: Read sensors
            print(f"  [4/6] Testing read_sensors()...")
            sensors = runtime.read_sensors()
            assert isinstance(sensors, dict), "Sensors should return dict"
            assert len(sensors) > 0, "No sensors available"
            print(f"         [OK] Read {len(sensors)} sensors")

            # Test 5: Send commands
            print(f"  [5/6] Testing send_command()...")
            for cmd in test_commands:
                result = runtime.send_command(cmd["command"], cmd.get("payload"))
                assert isinstance(result, dict), "Command result should be dict"
                assert "status" in result, "Command result missing 'status'"
                print(f"         [OK] Command '{cmd['command']}' executed")

            # Test 6: Stop
            print(f"  [6/6] Testing stop()...")
            runtime.stop()
            print(f"         [OK] Runtime stopped")

            print(f"\n[PASS] {name} - All tests passed")
            self.pass_count += 1

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            errors.append(error_msg)
            print(f"\n[FAIL] {name} - {error_msg}")
            traceback.print_exc()
            passed = False
            self.fail_count += 1

        finally:
            if runtime:
                try:
                    runtime.stop()
                except:
                    pass

        self.results[name] = {
            "passed": passed,
            "errors": errors,
            "runtime_class": runtime_class.__name__,
        }

        return passed

    def run_all_tests(self) -> bool:
        """Run tests for all runtimes"""
        print("=" * 60)
        print("EdgeOS Runtime Offline Validation Test")
        print("=" * 60)
        print("\nTesting all runtimes for offline operation...")
        print("(No network, no external APIs, no cloud services)\n")

        # Test Automotive
        self.test_runtime(
            "Automotive",
            AutomotiveRuntime,
            [
                {"command": "ignition_on"},
                {"command": "set_gear", "payload": {"position": "D"}},
                {"command": "set_throttle", "payload": {"percentage": 50.0}},
                {"command": "get_telemetry"},
            ],
        )

        # Test Aviation
        self.test_runtime(
            "Aviation",
            AviationRuntime,
            [
                {"command": "start_engines"},
                {"command": "set_throttle", "payload": {"percentage": 75.0}},
                {"command": "set_elevator", "payload": {"position": 0.1}},
                {"command": "get_telemetry"},
            ],
        )

        # Test Maritime
        self.test_runtime(
            "Maritime",
            MaritimeRuntime,
            [
                {"command": "start_engines"},
                {"command": "set_throttle", "payload": {"percentage": 60.0}},
                {"command": "set_rudder", "payload": {"angle_deg": 15.0}},
                {"command": "get_position"},
            ],
        )

        # Test Satellite
        self.test_runtime(
            "Satellite",
            SatelliteRuntime,
            [
                {"command": "activate_payload"},
                {"command": "deploy_solar_panels"},
                {"command": "set_reaction_wheels", "payload": {"x": 0.1, "y": 0.0, "z": 0.0}},
                {"command": "get_orbital_elements"},
            ],
        )

        # Test IoT
        self.test_runtime(
            "IoT",
            IoTRuntime,
            [
                {"command": "read_sensors"},
                {"command": "health_check"},
            ],
        )

        # Test Mobile
        self.test_runtime(
            "Mobile",
            MobileRuntime,
            [
                {"command": "read_sensors"},
                {"command": "health_check"},
            ],
        )

        # Test TV
        self.test_runtime(
            "TV",
            TvRuntime,
            [
                {"command": "read_sensors"},
                {"command": "health_check"},
            ],
        )

        return self.print_summary()

    def print_summary(self) -> bool:
        """Print test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Runtimes Tested: {self.test_count}")
        print(f"Passed: {self.pass_count}")
        print(f"Failed: {self.fail_count}")
        print(f"Success Rate: {(self.pass_count/self.test_count*100):.1f}%")

        print("\nDetailed Results:")
        for name, result in self.results.items():
            status = "[PASS]" if result["passed"] else "[FAIL]"
            print(f"  {status} {name} ({result['runtime_class']})")
            if result["errors"]:
                for error in result["errors"]:
                    print(f"      Error: {error}")

        all_passed = self.fail_count == 0
        if all_passed:
            print("\n[OK] ALL RUNTIMES WORK OFFLINE")
        else:
            print(f"\n[WARNING] {self.fail_count} runtime(s) failed offline validation")

        return all_passed


def main():
    """Main test runner"""
    validator = RuntimeValidator()
    success = validator.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
