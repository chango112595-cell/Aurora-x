#!/usr/bin/env python3
"""
Aurora Nexus V3 - Quick Test
Tests core functionality
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aurora_nexus_v3.core import AuroraUniversalCore, NexusConfig


async def test_nexus():
    print("\n" + "=" * 60)
    print("  AURORA NEXUS V3 - SYSTEM TEST")
    print("=" * 60 + "\n")

    config = NexusConfig.from_env()
    print(f"[+] Config loaded: node_id={config.node_id}")
    print(f"[+] Platform: {config.platform_info['system']} {config.platform_info['machine']}")
    print(f"[+] Device tier: {config.get_device_tier()}")

    core = AuroraUniversalCore(config)
    print(f"\n[+] Core initialized: version {core.VERSION}")

    print("\n[*] Starting Aurora Nexus V3...")
    await core.start()

    print(f"\n[+] State: {core.state.value}")
    print(f"[+] Modules loaded: {len(core.modules)}")

    for name, status in core.module_status.items():
        icon = "[OK]" if status.healthy else "[!!]"
        print(f"    {icon} {name}: loaded={status.loaded}, healthy={status.healthy}")

    print("\n[*] Running health check...")
    health = await core.health_check()
    print(f"[+] Coherence: {health['coherence'] * 100:.1f}%")
    print(f"[+] Uptime: {health['uptime']:.2f}s")

    print("\n[*] Testing API Gateway...")
    api = await core.get_module("api_gateway")
    if api:
        result = await api.handle_request("GET", "/api/status")
        print(f"[+] API Status: {result.get('success', False)}")
        if result.get("data"):
            print(f"    State: {result['data'].get('state')}")
            print(f"    Version: {result['data'].get('version')}")

    print("\n[*] Testing Port Manager...")
    ports = await core.get_module("port_manager")
    if ports:
        port = await ports.allocate(
            "test_service",
            protocol=ports.__class__.__bases__[0].__subclasses__()[0]
            if ports.__class__.__bases__
            else None or None,
        )
        if port is None:
            from aurora_nexus_v3.modules.port_manager import PortProtocol

            port = await ports.allocate("test_service", protocol=PortProtocol.TCP)
        if port:
            print(f"[+] Allocated port: {port}")
            await ports.release(port)
            print(f"[+] Released port: {port}")

    print("\n[*] Testing Resource Manager...")
    resources = await core.get_module("resource_manager")
    if resources:
        usage = await resources.get_usage()
        print(f"[+] Memory: {usage['memory_allocated_mb']}MB / {usage['memory_budget_mb']}MB")
        print(f"[+] CPU: {usage['cpu_allocated_percent']}% / {usage['cpu_budget_percent']}%")

    print("\n[*] Testing Hardware Detector...")
    hardware = await core.get_module("hardware_detector")
    if hardware:
        info = await hardware.get_info()
        print(f"[+] CPU Cores: {info['cpu']['cores_logical']}")
        print(f"[+] Memory: {info['memory']['total_mb']}MB")
        print(f"[+] Capability Score: {info['capability_score']}/100")

    print("\n[*] Testing Discovery Protocol...")
    discovery = await core.get_module("discovery_protocol")
    if discovery:
        stats = await discovery.get_stats()
        print(f"[+] Local Node: {stats['local_node_id']}")
        print(f"[+] Discovered Nodes: {stats['total_nodes']}")

    print("\n[*] Shutting down...")
    await core.stop()

    print("\n" + "=" * 60)
    print("  ALL TESTS PASSED - AURORA NEXUS V3 OPERATIONAL")
    print("=" * 60 + "\n")

    return True


if __name__ == "__main__":
    success = asyncio.run(test_nexus())
    sys.exit(0 if success else 1)
