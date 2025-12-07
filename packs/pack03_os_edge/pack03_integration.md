# PACK 03 Integration Guide

## Overview
PACK 03 provides the Aurora OS Base layer with:
- Virtual Filesystem (VFS)
- Namespace Registry
- Cooperative Scheduler
- Process Abstraction
- Hypervisor (sandbox orchestrator)
- Resource Governor
- Runtime Loader (Python/Node)
- IPC Bridge
- Module Lifecycle Manager
- Virtual Networking
- Security Layer
- Diagnostics

## Dependencies
- PACK 01: Core installer infrastructure
- PACK 02: Environment profiler (for runtime selection)

## Installation
```bash
python3 installer/aurora_installer.py stage --pack pack03_os_base
python3 installer/aurora_installer.py install --pack pack03_os_base
```

## Testing
```bash
python3 -m pytest packs/pack03_os_base/tests -q
```

## Core APIs

### VirtualFS
```python
from core.vfs import VirtualFS
v = VirtualFS("my_pack")
v.write_text("config.json", '{"key": "value"}')
```

### Hypervisor
```python
from core.hypervisor import Hypervisor
hv = Hypervisor()
result = hv.run_in("my_pack", "echo hello")
```

### RuntimeLoader
```python
from core.runtime_loader import RuntimeLoader
rl = RuntimeLoader("my_pack")
result = rl.run("script.py")
```

### ModuleLifecycle
```python
from core.lifecycle import ModuleLifecycle
m = ModuleLifecycle("my_pack")
m.load_from_dir("/path/to/source")
m.activate("python3 main.py")
```
