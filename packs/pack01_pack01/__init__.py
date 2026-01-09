"""
Aurora Pack 01: Core System

The foundational core system for Aurora-X platform.
Provides essential IPC, event bus, state storage, and logging.

Author: Aurora AI System
Version: 1.0.0
"""

PACK_ID = "pack01"
PACK_NAME = "Core System"
PACK_VERSION = "1.0.0"


def get_pack_info():
    return {"id": PACK_ID, "name": PACK_NAME, "version": PACK_VERSION, "status": "integrated"}
