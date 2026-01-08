#!/usr/bin/env python3
"""
Driver Manager: register drivers, lazy-load drivers, capability probing
Drivers expose 'probe()' and 'open()' APIs by convention.
"""

import importlib
from pathlib import Path

DRIVER_DIR = Path("hal/drivers")


class DriverManager:
    def __init__(self):
        self._drivers = {}  # name -> module
        self._instances = {}
        self._discover()

    def _discover(self):
        if not DRIVER_DIR.exists():
            return
        for p in DRIVER_DIR.iterdir():
            if p.is_dir() and (p / "__init__.py").exists():
                try:
                    mod = importlib.import_module(f"hal.drivers.{p.name}")
                    self._drivers[p.name] = mod
                except Exception as e:
                    print("driver load error", p.name, e)

    def list_drivers(self):
        return list(self._drivers.keys())

    def probe(self, name):
        mod = self._drivers.get(name)
        if not mod:
            return False
        fn = getattr(mod, "probe", None)
        if not fn:
            return False
        return fn()

    def open(self, name, *args, **kwargs):
        mod = self._drivers.get(name)
        if not mod:
            raise RuntimeError("driver missing")
        inst = mod.open(*args, **kwargs)
        self._instances[name] = inst
        return inst
