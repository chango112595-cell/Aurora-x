#!/usr/bin/env python3
"""
Ground uplink wrapper.

In production, this must integrate with a certified ground station uplink chain.
Here we only validate inputs and refuse to pretend success.
"""

from pathlib import Path


class GroundUplink:
    def __init__(self, ground_station_url: str | None = None):
        self.ground_station_url = ground_station_url

    def send(self, pkg_path: str) -> dict:
        path = Path(pkg_path)
        if not path.exists():
            raise FileNotFoundError(f"Payload not found: {pkg_path}")
        if not self.ground_station_url:
            raise RuntimeError("Ground station URL not configured; cannot uplink in production.")

        # Real integration would stream the file to the ground station API.
        return {
            "status": "pending",
            "destination": self.ground_station_url,
            "package": str(path),
        }


def send_uplink(pkg_path: str, ground_station_url: str | None = None):
    return GroundUplink(ground_station_url).send(pkg_path)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 2:
        print(send_uplink(sys.argv[1], sys.argv[2]))
    elif len(sys.argv) > 1:
        try:
            print(send_uplink(sys.argv[1], None))
        except Exception as exc:
            print(f"Error: {exc}")
    else:
        print("Usage: send_uplink_stub.py <package_path> <ground_station_url>")
