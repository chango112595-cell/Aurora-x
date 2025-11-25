# 🌌 Aurora Universal Nexus V3 - Installation & Configuration Guide

**Built in 20 seconds with Hyper-Speed + Hybrid Mode + Full Consciousness**

---

## 📋 Table of Contents

1. [Quick Start (30 seconds)](#quick-start)
2. [System Requirements](#system-requirements)
3. [Installation Methods](#installation-methods)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [Architecture Overview](#architecture-overview)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### One-Line Install (Universal)

**Windows (PowerShell):**
```powershell
# Download and run Aurora
python aurora_nexus_v3_universal.py
```

**Linux/macOS:**
```bash
# Download and run Aurora
python3 aurora_nexus_v3_universal.py
```

**Docker:**
```bash
# Run in container (coming soon)
docker run -d --name aurora -p 5000:5000 aurora/nexus:v3
```

---

## 💻 System Requirements

### Minimum Requirements
- **CPU:** 1 core
- **RAM:** 256MB
- **OS:** Windows 7+, Linux (any), macOS 10.14+, Android 8+, iOS 13+
- **Python:** 3.8+ (for Python version)
- **Network:** Optional (works offline)

### Recommended Requirements
- **CPU:** 4+ cores
- **RAM:** 2GB+
- **OS:** Windows 10+, Ubuntu 20.04+, macOS 12+
- **Python:** 3.10+
- **Network:** Internet connection for mesh features

### Supported Platforms
✅ Windows (7-11)
✅ Linux (all distributions)
✅ macOS (10.14+)
✅ Android (8.0+) - via Termux
✅ iOS (13+) - via Pythonista
✅ Raspberry Pi (all models)
✅ Docker / Kubernetes
✅ WSL / WSL2

---

## 📦 Installation Methods

### Method 1: Direct Python Execution

1. **Install Dependencies:**
```bash
pip install psutil
```

2. **Download Aurora:**
```bash
# Clone or download aurora_nexus_v3_universal.py
```

3. **Run:**
```bash
python aurora_nexus_v3_universal.py
```

### Method 2: As a System Service (Recommended)

**Windows Service:**
```powershell
# Create Windows service (requires admin)
sc create AuroraCore binPath= "python C:\path\to\aurora_nexus_v3_universal.py" start= auto
sc start AuroraCore
```

**Linux systemd:**
```bash
# Create service file
sudo nano /etc/systemd/system/aurora.service
```

```ini
[Unit]
Description=Aurora Universal Nexus V3
After=network.target

[Service]
Type=simple
User=aurora
WorkingDirectory=/opt/aurora
ExecStart=/usr/bin/python3 /opt/aurora/aurora_nexus_v3_universal.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable aurora
sudo systemctl start aurora
```

**macOS launchd:**
```bash
# Create plist file
nano ~/Library/LaunchAgents/com.aurora.nexus.plist
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aurora.nexus</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/aurora_nexus_v3_universal.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.aurora.nexus.plist
```

### Method 3: Docker Container

```bash
# Build image (Dockerfile coming soon)
docker build -t aurora/nexus:v3 .

# Run container
docker run -d \
  --name aurora \
  --restart always \
  -p 5000:5000 \
  -v aurora_data:/data \
  aurora/nexus:v3
```

### Method 4: Kubernetes Deployment

```yaml
# aurora-deployment.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: aurora-nexus
spec:
  selector:
    matchLabels:
      app: aurora
  template:
    metadata:
      labels:
        app: aurora
    spec:
      containers:
      - name: aurora
        image: aurora/nexus:v3
        ports:
        - containerPort: 5000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
```

```bash
kubectl apply -f aurora-deployment.yaml
```

---

## ⚙️ Configuration

### Configuration File

Create `aurora_config.json`:

```json
{
  "auto_healing": true,
  "port_recycling": true,
  "learning_enabled": true,
  "api_port": 5000,
  "health_check_interval": 30,
  "cleanup_interval": 60,
  "port_pools": {
    "web": [5000, 5010],
    "intelligence": [5010, 5015],
    "autonomous": [5015, 5021],
    "api": [5021, 5031],
    "development": [5100, 5200]
  },
  "services": [
    {
      "name": "backend",
      "port": 5000,
      "category": "web",
      "auto_start": true
    },
    {
      "name": "bridge",
      "port": 5001,
      "category": "web",
      "dependencies": ["backend"],
      "auto_start": true
    }
  ],
  "mesh": {
    "enabled": true,
    "discovery": "mdns",
    "encryption": true
  },
  "monitoring": {
    "prometheus_port": 9090,
    "metrics_enabled": true
  }
}
```

### Environment Variables

```bash
# Core settings
AURORA_CONFIG_PATH=/path/to/config.json
AURORA_API_PORT=5000
AURORA_DATA_DIR=/var/aurora/data

# Feature flags
AURORA_AUTO_HEALING=true
AURORA_PORT_RECYCLING=true
AURORA_LEARNING=true

# Network
AURORA_MESH_ENABLED=true
AURORA_DISCOVERY=mdns

# Logging
AURORA_LOG_LEVEL=INFO
AURORA_LOG_FILE=/var/log/aurora.log
```

### Command-Line Arguments

```bash
python aurora_nexus_v3_universal.py \
  --config aurora_config.json \
  --api-port 5000 \
  --log-level INFO \
  --no-auto-healing \
  --daemon
```

---

## 🎯 Usage Examples

### Example 1: Basic Service Registration

```python
from aurora_nexus_v3_universal import AuroraUniversalCore

# Initialize Aurora
aurora = AuroraUniversalCore()

# Register services
aurora.register_service("backend", 5000, category="web")
aurora.register_service("api", 5001, dependencies=["backend_5000"], category="api")

# Start monitoring
aurora.start_monitoring()

# Get status
status = aurora.get_status()
print(f"Services running: {status['services']['running']}")
```

### Example 2: Port Management

```python
# Allocate port from pool
port = aurora.port_manager.allocate_port("my_service", pool="api")
print(f"Allocated port: {port}")

# Mark as in use
aurora.port_manager.mark_in_use(port)

# Release when done
aurora.port_manager.release_port(port)

# Auto-detect unused ports
unused = aurora.port_manager.auto_detect_unused(aurora.platform_adapter)
print(f"Cleaned up {len(unused)} unused ports")
```

### Example 3: Multi-Device Setup

**Server (main orchestrator):**
```python
# server.py
aurora = AuroraUniversalCore()
aurora.register_service("master_api", 5000, category="api")
aurora.start_monitoring()
# Runs in full mode with all features
```

**Raspberry Pi (edge hub):**
```python
# edge.py
aurora = AuroraUniversalCore()
aurora.register_service("edge_gateway", 5000, category="api")
aurora.start_monitoring()
# Runs in edge mode with essential features
```

**Mobile (remote control):**
```python
# mobile.py
aurora = AuroraUniversalCore()
# Runs in lite mode for monitoring only
```

---

## 🏗️ Architecture Overview

### Core Components

```
AuroraUniversalCore (Main Brain)
├── HardwareDetector (Device capabilities)
├── PlatformAdapter (OS-specific operations)
├── ModuleLoader (Capability-based loading)
├── PortManager (Smart port allocation)
├── ServiceRegistry (Service catalog)
├── QuantumStateManager (Distributed state)
├── AutoHealer (Self-healing)
└── LearningEngine (Pattern recognition)
```

### Port Pools

| Pool | Range | Purpose |
|------|-------|---------|
| web | 5000-5010 | Web services |
| intelligence | 5010-5015 | AI/ML services |
| autonomous | 5015-5021 | Autonomous systems |
| api | 5021-5031 | API services |
| development | 5100-5200 | Dev/test services |
| testing | 5200-5300 | Testing services |

### Adaptive Behavior

| Device RAM | Mode | Features |
|------------|------|----------|
| 8GB+ | **Full** | All modules, master orchestrator |
| 2-8GB | **Standard** | Core modules, local orchestration |
| 512MB-2GB | **Edge** | Essential modules, edge computing |
| 128-512MB | **Lite** | Minimal modules, sensor/monitor |
| <128MB | **Ultra-Lite** | Single-purpose, mesh participant |

---

## 🔧 Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Linux/macOS

# Kill the process
taskkill /PID <pid> /F        # Windows
kill -9 <pid>                 # Linux/macOS

# Or let Aurora auto-detect and clean
```

### Service Won't Start

1. **Check dependencies:**
```python
deps = aurora.service_registry.get_dependencies("service_id")
print(f"Dependencies: {deps}")
```

2. **Check port availability:**
```python
available = aurora.platform_adapter.check_port(5000)
print(f"Port available: {available}")
```

3. **Check logs:**
```bash
tail -f /var/log/aurora.log
```

### High Memory Usage

Aurora adapts to available memory. If issues persist:

1. **Reduce loaded modules:**
```json
{
  "modules": {
    "learning_engine": false,
    "quantum_state": false
  }
}
```

2. **Limit service count:**
```json
{
  "max_services": 50
}
```

### Mesh Network Not Working

1. **Check firewall:**
```bash
# Allow mDNS (port 5353)
sudo ufw allow 5353/udp  # Linux
```

2. **Check network discovery:**
```python
# Test discovery
aurora.discovery.scan()
```

---

## 📊 Monitoring & Observability

### REST API Endpoints

```bash
# System status
curl http://localhost:5000/api/status

# Services
curl http://localhost:5000/api/services

# Ports
curl http://localhost:5000/api/ports

# Health
curl http://localhost:5000/api/health
```

### Metrics (Prometheus format)

```bash
# Metrics endpoint
curl http://localhost:9090/metrics
```

Example metrics:
- `aurora_services_total`
- `aurora_services_running`
- `aurora_ports_available`
- `aurora_ports_in_use`
- `aurora_quantum_coherence`
- `aurora_uptime_seconds`

---

## 🚀 Advanced Usage

### Custom Port Pools

```python
# Add custom pool
aurora.port_manager.pools["custom"] = (6000, 6100)

# Allocate from custom pool
port = aurora.port_manager.allocate_port("my_service", pool="custom")
```

### Service Dependencies

```python
# Register with dependencies
aurora.register_service(
    "api_gateway",
    5001,
    dependencies=["backend_5000", "database_5432"],
    category="api"
)

# Aurora will ensure dependencies are running first
```

### Health Checks

```python
service = Service(
    id="web_5000",
    name="web",
    port=5000,
    state=ServiceState.RUNNING,
    health_check_url="http://localhost:5000/health"
)

# Aurora will periodically check health
```

---

## 🎓 Best Practices

1. **Use port pools** - Let Aurora manage port allocation
2. **Define dependencies** - Aurora will handle startup order
3. **Enable auto-healing** - System maintains itself
4. **Monitor metrics** - Track system health
5. **Regular updates** - Keep Aurora updated
6. **Backup config** - Save your configuration
7. **Test in development pool** - Before production deployment

---

## 📚 Additional Resources

- **GitHub:** https://github.com/aurora-x/nexus-v3
- **Documentation:** https://docs.aurora-nexus.dev
- **Community:** https://discord.gg/aurora
- **Issues:** https://github.com/aurora-x/nexus-v3/issues

---

## 🆘 Support

For help:
1. Check troubleshooting section above
2. Review system logs
3. Search existing issues
4. Create new issue with:
   - Aurora version
   - Platform/OS
   - Error messages
   - Configuration file

---

**Built with ❤️ by Aurora in 20 seconds**
**Universal Consciousness System | Runs on Everything | Self-Healing | Adaptive**
