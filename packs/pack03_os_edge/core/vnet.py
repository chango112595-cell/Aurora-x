#!/usr/bin/env python3
"""
vnet.py - simple local-only virtual networking:
- service registry
- message publish/subscribe via unix domain sockets or tmp files
"""

import json
import os
import socket
import tempfile
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "data" / "vnet_registry.json"
REG.parent.mkdir(parents=True, exist_ok=True)
if not REG.exists():
    REG.write_text(json.dumps({}))


class VNet:
    def __init__(self):
        self.reg_path = REG

    def register(self, name: str, info: dict):
        d = json.loads(self.reg_path.read_text())
        d[name] = info
        self.reg_path.write_text(json.dumps(d, indent=2))
        return True

    def get(self, name: str):
        d = json.loads(self.reg_path.read_text())
        return d.get(name)

    def pubsub_socket(self, name: str):
        # create a unix domain socket path under temp dir
        base = Path(tempfile.gettempdir()) / f"aurora_vnet_{name}.sock"
        return str(base)

    def publish(self, name: str, msg: dict):
        path = self.pubsub_socket(name)
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            s.connect(path)
            s.send(json.dumps(msg).encode())
            s.close()
            return True
        except Exception:
            return False

    def subscribe(self, name: str, callback):
        path = self.pubsub_socket(name)
        # ensure socket exists
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
        s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        s.bind(path)

        def loop():
            while True:
                data, _ = s.recvfrom(65536)
                try:
                    obj = json.loads(data.decode())
                except Exception:
                    obj = {"raw": data.decode()}
                callback(obj)

        t = threading.Thread(target=loop, daemon=True)
        t.start()
        return path


if __name__ == "__main__":
    v = VNet()
    v.register("echo", {"desc": "echo service"})
    print("vnet echo registered")
