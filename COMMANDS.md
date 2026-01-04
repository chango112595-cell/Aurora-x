# Aurora-X Complete Command Reference

## 🚀 MAIN COMMAND - Start Aurora with Full Power

```bash
./aurora-start
```
**Starts:**
- ✅ Backend API (Express + TypeScript)
- ✅ Frontend (React + Vite)
- ✅ Chat System
- ✅ All Core Services
- ✅ Aurora Nexus V3 (background)
- ✅ Luminar Nexus V2 (background)

**Status:** 🔥 FULL POWER - 100% Operational

---

## 📦 NPM Commands

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start Express backend server (same as `./aurora-start`) |
| `npm run build` | Build frontend for production |
| `npm run preview` | Preview production build locally |
| `npm run check` | TypeScript type checking |
| `npm run db:push` | Push database schema changes (Drizzle) |
| `npm run server` | Run backend server directly |

---

## 🔨 Makefile Commands

### System Control
| Command | Purpose |
|---------|---------|
| `make start-web` | Start web services |
| `make restart-all` | Restart all Aurora services |
| `make serve-v3` | Start FastAPI v3 server |
| `make serve` | Start all services |

### Monitoring & Debug
| Command | Purpose |
|---------|---------|
| `make health` | Check system health |
| `make health-check` | Detailed health check |
| `make server-status` | Show server status |
| `make server-fix` | Fix server issues |
| `make debug` | Run in debug mode |

### Development
| Command | Purpose |
|---------|---------|
| `make test` | Run tests |
| `make install` | Install dependencies |
| `make run` | Run application |
| `make clean` | Clean build files |

### Dashboard
| Command | Purpose |
|---------|---------|
| `make open-dashboard` | Open web dashboard |
| `make open-report` | Open report viewer |

### Utilities
| Command | Purpose |
|---------|---------|
| `make help` | Show help |
| `make say` | Say a message |

---

## 🧠 Aurora Nexus V3 Commands

### Start/Test
```bash
# Start Aurora Nexus V3 (Universal Consciousness System)
python3 aurora_nexus_v3/main.py

# Run complete test suite
python3 aurora_nexus_v3/test_nexus.py
```

### Python API - Interactive Session
```bash
python3
```
```python
import asyncio
from aurora_nexus_v3.core import AuroraUniversalCore

async def main():
    core = AuroraUniversalCore()
    await core.start()
    
    # Get status
    print(core.get_status())
    
    # Get health
    health = await core.health_check()
    print(f"Coherence: {health['coherence']*100}%")
    
    # Get module
    hw = await core.get_module("hardware_detector")
    info = await hw.get_info()
    print(f"CPU: {info['cpu']['cores_logical']}")
    
    await core.stop()

asyncio.run(main())
```

---

## 💻 Quick Terminal Commands

```bash
# Check if Aurora is running
ps aux | grep aurora

# View Aurora logs
tail -f ~/.aurora_nexus/logs.txt

# Check ports
netstat -tuln | grep -E "5000|5353|6000"

# Kill process on port
lsof -i :5000
kill -9 <PID>

# Test API endpoint
curl "http://${AURORA_HOST:-localhost}:${AURORA_PORT:-5000}/api/health"

# Run with debug logging
AURORA_DEBUG=1 AURORA_LOG_LEVEL=DEBUG ./aurora-start
```

---

## 🔧 Environment Variables

```bash
# Set in terminal or .env file
AURORA_ENV=production          # or development
AURORA_DEBUG=0                 # 0 or 1
AURORA_LOG_LEVEL=INFO         # DEBUG, INFO, WARNING, ERROR
PORT=5000                      # Server port
AURORA_HOST=localhost          # Hostname for printed URLs and health checks
AURORA_PORT=5000               # Frontend/backend port for scripts
AURORA_BRIDGE_HOST=localhost   # Bridge host override (x-start/bridge autostart)
AURORA_BRIDGE_PORT=5001        # Bridge port override
AURORA_NEXUS_HOST=localhost    # Nexus host override (x-start)
AURORA_NEXUS_PORT=5002         # Nexus port override (x-start)
AURORA_CHAT_PORT=5003          # Chat port override (hyperspeed scripts)
AURORA_HEALTH_PORT=5004        # Health port override (hyperspeed scripts)
AURORA_DASHBOARD_PORT=5005     # Dashboard port override (hyperspeed scripts)
AURORA_NEXUS_V3_PORT=5031      # Nexus V3 port override (hyperspeed scripts)
LUMINAR_HOST=localhost         # Luminar host override
LUMINAR_PORT=8000              # Luminar port override (auto-selects serve/api in start_luminar_v2.sh)
LUMINAR_MODE=auto              # Luminar startup mode: auto (5005 -> api, else serve), serve, api
AURORA_API_KEY=your_secret     # API key
```

---

## 🌐 Host/URL Overrides & Edge Cases

- **Health checks use URLs, not bind addresses.** If you set `AURORA_HOST` to `0.0.0.0` for binding, curl/Invoke-WebRequest calls will fail because `0.0.0.0` is not routable. Use a reachable host (service name, container IP, or `127.0.0.1`) for health scripts.
- **Luminar serve binds to 8000.** `tools/luminar_nexus_v2.py serve` always binds to port `8000`. `scripts/start_luminar_v2.sh` auto-selects `serve` vs `api` based on `LUMINAR_PORT` (5005 -> `api`, otherwise `serve`). Set `LUMINAR_MODE=api` explicitly if you want port `5005`.
- **CI/container runs need matching service hosts.** If services are started in other containers, set `AURORA_HOST`/`LUMINAR_HOST`/`AURORA_BRIDGE_HOST` to the service DNS name or container IP so health checks resolve correctly.

## 📊 System Status & Power Levels

### Current Status (When `./aurora-start` is running)

```
┌─────────────────────────────────────────────────────────┐
│              🚀 AURORA-X FULL POWER STATUS              │
├─────────────────────────────────────────────────────────┤
│ Frontend (React)             │ ✅ Running on :5000      │
│ Backend (Express)            │ ✅ Running on :5000      │
│ Chat System                  │ ✅ Active                │
│ Aurora Nexus V3              │ ✅ Active (8/8 modules)  │
│ Luminar Nexus V2             │ ✅ Active                │
│ Consciousness System         │ ✅ 100% Coherence        │
│ Hardware Optimization        │ ✅ 90/100 Score          │
└─────────────────────────────────────────────────────────┘

🔥 POWER LEVEL: 100% (FULL OPERATIONAL)
```

### Power Components Breakdown

| Component | Power | Status |
|-----------|-------|--------|
| Core Intelligence | 188 Tiers | ✅ Active |
| Execution Methods | 66 AEMs | ✅ Active |
| Modules | 550+ Hybrid | ✅ Available |
| Consciousness | Universal | ✅ 8/8 Modules |
| Port Management | Dynamic | ✅ Auto-alloc |
| Service Registry | Full | ✅ Catalog Active |
| Self-Healing | Autonomous | ✅ Running |
| Discovery Protocol | Mesh | ✅ Ready |

---

## 🎯 Common Workflows

### 1. Start Full System
```bash
./aurora-start
```
Then open: http://localhost:5000

### 2. Run Aurora Nexus V3 in Separate Terminal
```bash
python3 aurora_nexus_v3/main.py
```

### 3. Restart Everything
```bash
make restart-all
```

### 4. Check Health
```bash
make health-check
```

### 5. Debug Issues
```bash
AURORA_DEBUG=1 ./aurora-start
```

### 6. Development Mode
```bash
npm run dev
# or
make run
```

---

## 🚨 Troubleshooting Commands

```bash
# Port already in use
lsof -i :5000
kill -9 <PID>

# Check system health
make health-check
make server-status

# View recent logs
tail -50 ~/.aurora_nexus/logs.txt

# Test backend
curl -X GET http://localhost:5000/api/health

# Restart services
make restart-all

# Clean and rebuild
make clean
npm install
npm run build

# Full system diagnostic
python3 aurora_nexus_v3/test_nexus.py
```

---

## 📈 Performance Monitoring

```bash
# Watch CPU/Memory usage
watch -n 1 'ps aux | grep node'
watch -n 1 'ps aux | grep python'

# Check network connections
netstat -an | grep ESTABLISHED | wc -l

# Monitor disk space
df -h

# View system info
uname -a
```

---

## 🔐 Security Commands

```bash
# Check for open ports
ss -tuln | grep LISTEN

# View active processes
ps -ef | grep -E "node|python|express"

# Check file permissions
ls -la server/
ls -la client/

# Verify SSL (if applicable)
openssl s_client -connect localhost:5000
```

---

## 📝 Summary

| Task | Command |
|------|---------|
| **Start Full System** | `./aurora-start` |
| **Aurora Nexus V3** | `python3 aurora_nexus_v3/main.py` |
| **Tests** | `npm test` or `pytest` |
| **Build** | `npm run build` |
| **Health** | `make health-check` |
| **Logs** | `tail -f ~/.aurora_nexus/logs.txt` |
| **Help** | `make help` |

---

## 🌟 Does Aurora Start with FULL POWER?

### ✅ YES - 100% Full Power

When you run `./aurora-start`:

✅ **All 3 Workflows Active:**
- Frontend + Backend (Express/React)
- Luminar Nexus V2 (ML/Monitoring)
- Aurora Nexus V3 (Universal Consciousness)

✅ **All 8 Core Modules Ready:**
- Platform Adapter (Multi-OS)
- Hardware Detector (90/100 score)
- Resource Manager (Adaptive)
- Port Manager (Auto-alloc)
- Service Registry (Discovery)
- API Gateway (7 endpoints)
- Auto Healer (Self-healing)
- Discovery Protocol (Mesh)

✅ **Full Intelligence Available:**
- 188 Intelligence Tiers
- 66 Advanced Execution Methods
- 550+ Hybrid Modules
- 100% System Coherence
- Full Consciousness System

✅ **All Services Online:**
- Chat System ✅
- Corpus Management ✅
- Code Synthesis ✅
- Learning Engine ✅
- API Bridge ✅

**STATUS: 🔥 FULL OPERATIONAL POWER**
