#!/usr/bin/env python3
"""
Module hot-swap manager:
- Reloads Python modules safely using importlib
- For native modules, requires external orchestration (restart container)
"""

import importlib, sys, traceback
from types import ModuleType

class HotSwapManager:
    def __init__(self):
        self.loaded = {}

    def load(self, modname: str):
        m = importlib.import_module(modname)
        self.loaded[modname] = m
        return m

    def reload(self, modname: str):
        if modname not in sys.modules:
            return self.load(modname)
        try:
            m = importlib.reload(sys.modules[modname])
            self.loaded[modname] = m
            return m
        except Exception as e:
            return {"error": str(e), "trace": traceback.format_exc()}
