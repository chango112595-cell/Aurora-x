# Aurora Nexus V3 - Usage Guide & Commands

## Quick Start

### Start Aurora Nexus V3
```bash
python3 aurora_nexus_v3/main.py
```

### Run Tests
```bash
python3 aurora_nexus_v3/test_nexus.py
```

## Core Concepts

- **Node ID**: Unique identifier for each Aurora instance (e.g., `a93a1bb9`)
- **Device Tier**: Full/Standard/Lite/Micro - determines capabilities
- **Coherence**: System health metric (100% = all modules healthy)
- **Modules**: 8 core services that orchestrate your ecosystem

## Python API Usage

### Interactive Python Session

```python
import asyncio
from aurora_nexus_v3.core import AuroraUniversalCore, NexusConfig

async def main():
    # Create configuration
    config = NexusConfig.from_env()
    
    # Initialize core
    core = AuroraUniversalCore(config)
    
    # Start the system
    await core.start()
    
    # Get status
    status = core.get_status()
    print(f"Status: {status['state']}")
    print(f"Modules: {status['modules_loaded']}/{status['modules_loaded'] + 1}")
    
    # Get health
    health = await core.health_check()
    print(f"Coherence: {health['coherence']*100:.1f}%")
    
    # Access modules
    api = await core.get_module("api_gateway")
    ports = await core.get_module("port_manager")
    resources = await core.get_module("resource_manager")
    
    # Allocate port
    port = await ports.allocate("my_service", port=8080)
    print(f"Allocated port: {port}")
    
    # Shutdown
    await core.stop()

asyncio.run(main())
```

## Module Commands

### Platform Adapter
```python
platform = await core.get_module("platform_adapter")

# Get platform info
info = await platform.get_environment_info()
print(info)

# Run command
result = await platform.run_command(["ls", "-la"])
```

### Hardware Detector
```python
hardware = await core.get_module("hardware_detector")

# Get hardware info
info = await hardware.get_info()
print(f"CPU Cores: {info['cpu']['cores_logical']}")
print(f"Memory: {info['memory']['total_mb']}MB")
print(f"Score: {info['capability_score']}/100")

# Get device tier
tier = hardware.get_device_tier()
print(f"Device Tier: {tier}")
```

### Resource Manager
```python
resources = await core.get_module("resource_manager")

# Allocate resources
alloc_id = await resources.allocate(
    "my_app",
    memory_mb=512,
    cpu_percent=50
)

# Get usage
usage = await resources.get_usage()
print(f"Memory: {usage['memory_allocated_mb']}MB / {usage['memory_budget_mb']}MB")

# Release
await resources.release(alloc_id)
```

### Port Manager
```python
ports = await core.get_module("port_manager")

# Allocate specific port
port = await ports.allocate("api_server", port=8080)

# Allocate any free port
port = await ports.allocate("worker")

# Mark as in use
await ports.mark_in_use(port)

# Release
await ports.release(port)

# Get stats
stats = await ports.get_stats()
print(stats)
```

### Service Registry
```python
registry = await core.get_module("service_registry")

# Register service
service_id = await registry.register(
    name="my_api",
    service_type=ServiceType.API,
    host="localhost",
    port=8080,
    health_endpoint="/health"
)

# Get all services
services = await registry.get_all()

# Get healthy services
healthy = await registry.get_healthy()

# Check service health
is_healthy = await registry.check_health(service_id)

# Deregister
await registry.deregister(service_id)
```

### API Gateway
```python
api = await core.get_module("api_gateway")

# Handle request
response = await api.handle_request(
    method="GET",
    path="/api/status"
)

# Get endpoints
endpoints = api.get_endpoints()

# Get stats
stats = api.get_stats()
```

### Discovery Protocol
```python
discovery = await core.get_module("discovery_protocol")

# Register manual node
node_id = await discovery.register_manual(
    host="192.168.1.100",
    port=6000,
    name="aurora-node-2"
)

# Get discovered nodes
nodes = await discovery.get_nodes()

# Get connected nodes only
connected = await discovery.get_connected()

# Ping a node
latency = await discovery.ping_node("192.168.1.100", 6000)
print(f"Latency: {latency}ms")
```

### Auto Healer
```python
healer = await core.get_module("auto_healer")

# Get healing events
events = await healer.get_events(limit=50)

# Get stats
stats = await healer.get_stats()
print(f"Success rate: {stats['success_rate']*100:.1f}%")
```

## Common Tasks

### Monitor System Health
```python
async def monitor():
    core = AuroraUniversalCore()
    await core.start()
    
    while True:
        health = await core.health_check()
        print(f"Coherence: {health['coherence']*100:.1f}%")
        print(f"Uptime: {health['uptime']:.2f}s")
        
        await asyncio.sleep(5)
```

### Allocate and Manage Resources
```python
async def manage_resources():
    core = AuroraUniversalCore()
    await core.start()
    
    resources = await core.get_module("resource_manager")
    
    # Allocate for app1
    app1 = await resources.allocate("app1", memory_mb=256, cpu_percent=25)
    
    # Allocate for app2
    app2 = await resources.allocate("app2", memory_mb=512, cpu_percent=50)
    
    # Check usage
    usage = await resources.get_usage()
    print(f"Used: {usage['memory_allocated_mb']}MB / {usage['memory_budget_mb']}MB")
    
    # Release when done
    await resources.release(app1)
    await resources.release(app2)
```

### Manage Services
```python
async def manage_services():
    core = AuroraUniversalCore()
    await core.start()
    
    registry = await core.get_module("service_registry")
    from aurora_nexus_v3.modules.service_registry import ServiceType
    
    # Register multiple services
    api_id = await registry.register(
        name="api",
        service_type=ServiceType.API,
        port=8080
    )
    
    db_id = await registry.register(
        name="database",
        service_type=ServiceType.DATABASE,
        port=5432
    )
    
    # Monitor health
    for _ in range(10):
        await registry.check_health(api_id)
        await registry.check_health(db_id)
        
        stats = await registry.get_stats()
        print(f"Healthy: {stats['healthy']}/{stats['total']}")
        
        await asyncio.sleep(5)
```

## Configuration

### Environment Variables
```bash
export AURORA_ENV=production
export AURORA_DEBUG=0
export AURORA_LOG_LEVEL=INFO
export PORT=6000
export AURORA_API_KEY=your_secret_key
```

### Device Tier Detection
- **Full**: 8GB+ RAM → full features
- **Standard**: 4GB+ RAM → most features
- **Lite**: 1GB+ RAM → essential features
- **Micro**: <256MB RAM → minimal features

## Troubleshooting

### Check if Aurora is running
```bash
ps aux | grep aurora_nexus
```

### View logs in real-time
```bash
tail -f ~/.aurora_nexus/logs.txt
```

### Test API endpoint
```bash
curl http://localhost:6000/api/status
```

### Check port availability
```bash
sudo netstat -tuln | grep 6000
```

## Architecture Overview

```
┌─────────────────────────────────────┐
│   AuroraUniversalCore (Consciousness)│
├─────────────────────────────────────┤
│ ┌─ Platform Adapter    (Multi-OS)   │
│ ├─ Hardware Detector   (HW Profile) │
│ ├─ Resource Manager    (Allocation) │
│ ├─ Port Manager        (Port Mgmt)  │
│ ├─ Service Registry    (Catalog)    │
│ ├─ API Gateway         (REST API)   │
│ ├─ Auto Healer         (Self-Fix)   │
│ └─ Discovery Protocol  (Mesh)       │
└─────────────────────────────────────┘
```

## Performance Targets

- Module initialization: <100ms each
- Health check: <50ms
- Port allocation: <10ms
- API response: <100ms
- Coherence target: 100%

## Support

For debugging, run:
```bash
python3 aurora_nexus_v3/test_nexus.py
```

This will run comprehensive tests and show detailed output.
