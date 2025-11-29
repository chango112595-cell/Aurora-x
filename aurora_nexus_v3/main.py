#!/usr/bin/env python3
"""
Aurora Nexus V3 - Universal Consciousness System
Main entry point for starting the Aurora Nexus server
"""

import asyncio
import sys
import os
import signal
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aurora_nexus_v3.core import AuroraUniversalCore, NexusConfig


class NexusServer:
    """Main server wrapper for Aurora Nexus V3"""
    
    def __init__(self, config: Optional[NexusConfig] = None):
        self.config = config or NexusConfig.from_env()
        self.core: Optional[AuroraUniversalCore] = None
        self._shutdown_event = asyncio.Event()
    
    async def start(self):
        print("\n" + "=" * 60)
        print("  AURORA NEXUS V3 - UNIVERSAL CONSCIOUSNESS SYSTEM")
        print("  The Ultimate Universal Orchestrator")
        print("=" * 60 + "\n")
        
        self.core = AuroraUniversalCore(self.config)
        
        await self.core.start()
        
        print("\n" + "-" * 60)
        print(f"  Node ID: {self.core.config.node_id}")
        print(f"  Status: {self.core.state.value.upper()}")
        print(f"  Modules Loaded: {len(self.core.modules)}")
        print(f"  Device Tier: {self.core.config.get_device_tier().upper()}")
        print("-" * 60 + "\n")
        
        status = self.core.get_status()
        print("Modules Status:")
        for name, mod_status in self.core.module_status.items():
            icon = "[OK]" if mod_status.healthy else "[!!]"
            print(f"  {icon} {name}")
        
        print("\n" + "=" * 60)
        print("  Aurora Nexus V3 is now ACTIVE")
        print("  Universal consciousness ready for operation")
        print("=" * 60 + "\n")
        
        return self.core
    
    async def stop(self):
        if self.core:
            await self.core.stop()
            print("\nAurora Nexus V3 shutdown complete.")
    
    async def run_forever(self):
        await self.start()
        
        try:
            await self._shutdown_event.wait()
        except asyncio.CancelledError:
            pass
        finally:
            await self.stop()
    
    def request_shutdown(self):
        self._shutdown_event.set()


async def main():
    server = NexusServer()
    
    loop = asyncio.get_event_loop()
    
    def signal_handler():
        print("\nShutdown signal received...")
        server.request_shutdown()
    
    if sys.platform != "win32":
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, signal_handler)
    
    await server.run_forever()


def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user")


if __name__ == "__main__":
    run()
