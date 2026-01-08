# Aurora Nexus V3 - Quick Start Commands

## 🚀 Start Aurora
```bash
python3 aurora_nexus_v3/main.py
```

## 🧪 Test All Systems
```bash
python3 aurora_nexus_v3/test_nexus.py
```

## 🐍 Interactive Python Usage

```python
import asyncio
from aurora_nexus_v3.core import AuroraUniversalCore, NexusConfig

async def main():
    # Initialize
    core = AuroraUniversalCore()
    await core.start()

    # Get status
    print(core.get_status())

    # Get health
    health = await core.health_check()
    print(f"Coherence: {health['coherence']*100}%")

    # Access modules
    resources = await core.get_module("resource_manager")
    ports = await core.get_module("port_manager")

    # Allocate port
    port = await ports.allocate("my_service")
    print(f"Got port: {port}")

    # Allocate resources
    alloc = await resources.allocate("app1", memory_mb=256, cpu_percent=25)
    print(f"Allocated: {alloc}")

    # Cleanup
    await resources.release(alloc)
    await ports.release(port)
    await core.stop()

asyncio.run(main())
```

## 📊 Module Commands

### Hardware Info
```python
hw = await core.get_module("hardware_detector")
info = await hw.get_info()
print(f"CPU: {info['cpu']['cores_logical']}")
print(f"RAM: {info['memory']['total_mb']}MB")
print(f"Score: {info['capability_score']}/100")
```

### Port Management
```python
ports = await core.get_module("port_manager")

# Allocate
port = await ports.allocate("service_name", port=8080)

# Check all
all_ports = await ports.get_all_allocations()

# Release
await ports.release(port)
```

### Services Registry
```python
registry = await core.get_module("service_registry")

# Register
svc_id = await registry.register(
    name="api",
    service_type=ServiceType.API,
    host="localhost",
    port=8080
)

# List
services = await registry.get_all()

# Check health
healthy = await registry.check_health(svc_id)
```

### Resource Allocation
```python
res = await core.get_module("resource_manager")

# Allocate
alloc_id = await res.allocate(
    "app",
    memory_mb=512,
    cpu_percent=50
)

# Check usage
usage = await res.get_usage()
print(usage)

# Release
await res.release(alloc_id)
```

### Discovery
```python
discovery = await core.get_module("discovery_protocol")

# Register node
await discovery.register_manual("192.168.1.100", 6000, "node-2")

# Get nodes
nodes = await discovery.get_nodes()
print(nodes)

# Ping
latency = await discovery.ping_node("192.168.1.100", 6000)
```

### Healing Status
```python
healer = await core.get_module("auto_healer")

# Get events
events = await healer.get_events(limit=20)

# Get stats
stats = await healer.get_stats()
print(f"Success rate: {stats['success_rate']*100}%")
```

## 🔍 Debug Commands

### Check if running
```bash
ps aux | grep aurora_nexus
```

### View current logs
```bash
tail -f ~/.aurora_nexus/logs.txt
```

### Run with debug logging
```bash
AURORA_DEBUG=1 AURORA_LOG_LEVEL=DEBUG python3 aurora_nexus_v3/main.py
```

### Check available ports
```bash
netstat -tuln | grep -E '5000|6000'
```

## 📈 System Status
```python
# Full status
status = core.get_status()
print(status)

# Health check
health = await core.health_check()
print(f"Coherence: {health['coherence']*100}%")
print(f"Uptime: {health['uptime']}s")

# Module details
for name, mod_status in core.module_status.items():
    print(f"{name}: {mod_status.healthy}")
```

## 🎯 Common Tasks

### Monitor Real-time
```python
import time
while True:
    health = await core.health_check()
    print(f"Coherence: {health['coherence']*100:.1f}%")
    time.sleep(5)
```

### Allocate Multiple Resources
```python
# Apps
app1 = await res.allocate("app1", memory_mb=256)
app2 = await res.allocate("app2", memory_mb=512)

usage = await res.get_usage()
print(f"Used: {usage['memory_allocated_mb']}MB")

# Cleanup
await res.release(app1)
await res.release(app2)
```

### Register & Monitor Services
```python
from aurora_nexus_v3.modules.service_registry import ServiceType

# Register
api = await registry.register(
    "api",
    service_type=ServiceType.API,
    port=8080
)

# Monitor
for i in range(10):
    await registry.check_health(api)
    stats = await registry.get_stats()
    print(f"Health: {stats['healthy']}/{stats['total']}")
    await asyncio.sleep(5)

# Cleanup
await registry.deregister(api)
```

## ⚙️ Configuration

### Environment Variables
```bash
AURORA_ENV=production        # production or development
AURORA_DEBUG=0              # 0 or 1
AURORA_LOG_LEVEL=INFO       # DEBUG, INFO, WARNING, ERROR
PORT=6000                   # API port
AURORA_API_KEY=secret       # API key for auth
```

### Device Tiers
- **Full** (8GB+): All features
- **Standard** (4GB+): Most features
- **Lite** (1GB+): Essential features
- **Micro** (<256MB): Minimal features

## 📚 Documentation
See `AURORA_NEXUS_V3_USAGE_GUIDE.md` for complete documentation.

## ✅ Status Check
Run this to verify everything is working:
```bash
python3 aurora_nexus_v3/test_nexus.py
```

Expected output:
- ✅ All 8 modules load
- ✅ 100% coherence
- ✅ Health checks pass
- ✅ Port allocation works
- ✅ Resource management works
- ✅ Hardware detection works
- ✅ Discovery protocol works
