# 🚀 Aurora-X Quick Commands Reference

**Last Updated:** November 6, 2025  
**Project:** Aurora-X Autonomous AI System

---

## 🔥 Start Aurora (Simplified Commands)

### ⭐ Start All Services (EASIEST WAY)
```bash
python3 x-start
```

### ⭐ Stop All Services
```bash
python3 x-stop
```

### ⭐ Check Status
```bash
python3 x-nexus status
```

---

## 🎯 Individual Service Control

### Start Individual Service
```bash
python3 x-nexus start <service>

# Examples:
python3 x-nexus start vite       # Frontend
python3 x-nexus start chat       # Chat server
python3 x-nexus start backend    # Backend API
python3 x-nexus start bridge     # Bridge service
python3 x-nexus start self-learn # Self-learning server
```

### Stop Individual Service
```bash
python3 x-nexus stop <service>

# Examples:
python3 x-nexus stop vite
python3 x-nexus stop chat
```

### Restart Individual Service
```bash
python3 x-nexus restart <service>

# Examples:
python3 x-nexus restart backend
python3 x-nexus restart chat
```

---

## 🔧 Advanced/Legacy Commands

### Start All Services (Legacy Method)
```bash
python tools/luminar_nexus.py start-all
```

### Start Chat Server Directly
```bash
python3 -c "from tools.luminar_nexus import run_chat_server; run_chat_server(5003)"
```

### Start in Background (Detached)
```bash
python3 -c "from tools.luminar_nexus import run_chat_server; run_chat_server(5003)" > /tmp/aurora_chat.log 2>&1 &
```

---

## 📊 Check Status

### ⭐ Check All Services (Simplified)
```bash
python3 x-nexus status
```

### Check Individual Service Health
```bash
# Backend
curl http://localhost:5000/health

# Bridge
curl http://localhost:5001/health

# Self-Learn
curl http://localhost:5002/health

# Chat (Aurora)
curl http://localhost:5003/api/chat -d '{"message":"hello"}'
```

### Check Running Processes
```bash
ps aux | grep -E "uvicorn|luminar|aurora" | grep -v grep
```

---

## 🛑 Stop Services

### ⭐ Stop All Services (Simplified)
```bash
python3 x-stop
```

### Stop Individual Service (Simplified)
```bash
python3 x-nexus stop <service>

# Examples:
python3 x-nexus stop chat
python3 x-nexus stop vite
python3 x-nexus stop backend
```

### Emergency Stop (Kill All)
```bash
# Kill chat server
pkill -f "python.*luminar_nexus.*5003"

# Kill backend
pkill -f "uvicorn.*5000"

# Kill bridge
pkill -f "uvicorn.*5001"

# Kill self-learn
pkill -f "uvicorn.*5002"

# Kill vite
pkill -f "vite.*5173"
```

---

## 🔄 Restart Services

### ⭐ Restart All (Simplified)
```bash
python3 x-stop
sleep 2
python3 x-start
```

### ⭐ Restart Individual Service
```bash
python3 x-nexus restart <service>

# Examples:
python3 x-nexus restart chat
python3 x-nexus restart backend
python3 x-nexus restart vite
```

### Legacy Restart Method
```bash
python tools/luminar_nexus.py stop-all
sleep 2
python tools/luminar_nexus.py start-all
```

---

## 💬 Talk to Aurora

### Simple Chat
```bash
curl -X POST http://localhost:5003/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello Aurora!"}'
```

### Aurora Self-Healing
```bash
curl -X POST http://localhost:5003/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Aurora, fix yourself"}'
```

### Ask Aurora for Status
```bash
curl -X POST http://localhost:5003/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"show status"}' | jq -r '.response'
```

### Pretty Print Response
```bash
curl -s -X POST http://localhost:5003/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello Aurora!"}' | jq -r '.response'
```

---

## 📝 Monitoring & Logs

### Watch Autonomous Monitoring (Live)
```bash
tail -f .aurora_knowledge/autonomous_monitoring_$(date +%Y%m%d).log
```

### View Recent Monitoring Activity
```bash
tail -50 .aurora_knowledge/autonomous_monitoring_$(date +%Y%m%d).log
```

### Check Chat Server Logs
```bash
tail -f /tmp/aurora_chat.log
```

### View All Aurora Logs
```bash
ls -lh .aurora_knowledge/*.log
```

---

## 🧪 Testing Commands

### Test Self-Healing
```bash
# 1. Kill a service
pkill -f "uvicorn.*5000"

# 2. Wait 10 seconds for auto-restart
sleep 10

# 3. Check if restored
curl http://localhost:5000/health
```

### Test Manual Healing
```bash
curl -s -X POST http://localhost:5003/api/chat \
  -d '{"message":"Aurora, fix yourself"}' | jq -r '.response'
```

---

## 🔧 Individual Service Management (Legacy)

> **Note:** Use the simplified `python3 x-nexus` commands above instead!

### Start Individual Services (Old Way)
```bash
# Backend
python tools/luminar_nexus.py start backend

# Bridge
python tools/luminar_nexus.py start bridge

# Self-Learn
python tools/luminar_nexus.py start self-learn

# Vite
python tools/luminar_nexus.py start vite

# Chat
python tools/luminar_nexus.py start chat
```

### Stop Individual Services (Old Way)
```bash
python tools/luminar_nexus.py stop backend
python tools/luminar_nexus.py stop bridge
python tools/luminar_nexus.py stop self-learn
python tools/luminar_nexus.py stop vite
python tools/luminar_nexus.py stop chat
```

### Restart Individual Services (Old Way)
```bash
python tools/luminar_nexus.py restart backend
python tools/luminar_nexus.py restart bridge
python tools/luminar_nexus.py restart self-learn
python tools/luminar_nexus.py restart vite
python tools/luminar_nexus.py restart chat
```

---

## 🌐 Access Points

| Service | Port | URL |
|---------|------|-----|
| Backend API | 5000 | http://localhost:5000 |
| Bridge | 5001 | http://localhost:5001 |
| Self-Learn | 5002 | http://localhost:5002 |
| Chat (Aurora) | 5003 | http://localhost:5003 |
| Vite Frontend | 5173 | http://localhost:5173 |

---

## 🤖 Aurora Autonomous Features

### What Aurora Does Automatically
- ✅ Monitors all services every 5 seconds
- ✅ Auto-restarts failed services (backend, bridge, self-learn, vite)
- ✅ Logs all activity to `.aurora_knowledge/autonomous_monitoring_*.log`
- ✅ Self-heals on command ("Aurora, fix yourself")
- ✅ Runs 24/7 in background (daemon thread)

### Aurora Voice Commands
```bash
# Self-healing
"Aurora, fix yourself"
"Aurora, restart yourself"
"Aurora, heal yourself"
"Fix yourself Aurora"

# Status
"show status"
"check health"

# Server management
"start all servers"
"stop all servers"
"restart servers"
```

---

## 🐛 Debugging

### Check if Services are Running
```bash
curl http://localhost:5000/health && echo "✅ Backend OK" || echo "❌ Backend DOWN"
curl http://localhost:5001/health && echo "✅ Bridge OK" || echo "❌ Bridge DOWN"
curl http://localhost:5002/health && echo "✅ Self-Learn OK" || echo "❌ Self-Learn DOWN"
curl http://localhost:5003/api/chat -d '{"message":"ping"}' && echo "✅ Chat OK" || echo "❌ Chat DOWN"
```

### View All Running Aurora Processes
```bash
ps aux | grep -E "python.*aurora|uvicorn.*500[0-2]|vite" | grep -v grep
```

### Kill All Aurora Processes (Emergency)
```bash
pkill -f "luminar_nexus"
pkill -f "uvicorn.*aurora"
pkill -f "vite"
```

### Clean Start (Kill Everything and Restart)
```bash
pkill -f "luminar_nexus"
pkill -f "uvicorn.*500[0-2]"
pkill -f "vite"
sleep 3
python tools/luminar_nexus.py start-all
```

---

## 📦 Quick Setup (First Time)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
npm install
```

### 2. Start Aurora
```bash
python3 -c "from tools.luminar_nexus import run_chat_server; run_chat_server(5003)"
```

### 3. Verify It's Working
```bash
curl -s http://localhost:5003/api/chat -d '{"message":"Hello"}' | jq -r '.response'
```

---

## 💡 Tips & Tricks

### Run Aurora in Background and Forget
```bash
nohup python3 -c "from tools.luminar_nexus import run_chat_server; run_chat_server(5003)" > /tmp/aurora.log 2>&1 &
```

### Watch Logs While Chatting
```bash
# Terminal 1
tail -f .aurora_knowledge/autonomous_monitoring_$(date +%Y%m%d).log

# Terminal 2
curl -X POST http://localhost:5003/api/chat -d '{"message":"Aurora, fix yourself"}'
```

### Quick Health Check All Services
```bash
for port in 5000 5001 5002 5003; do
  curl -s http://localhost:$port/health 2>/dev/null && echo "✅ Port $port OK" || echo "❌ Port $port DOWN"
done
```

### JSON Pretty Print Aurora Response
```bash
curl -s http://localhost:5003/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello Aurora"}' | jq '.'
```

---

## 🎯 Common Workflows

### ⭐ Daily Startup (Simplified)
```bash
python3 x-start
```

### ⭐ Check Everything is Running
```bash
python3 x-nexus status
```

### ⭐ Restart a Single Service
```bash
python3 x-nexus restart chat
```

### Aurora Self-Heal
```bash
curl -X POST http://localhost:5003/api/chat -d '{"message":"Aurora, fix yourself"}'
```

### View Monitoring Activity
```bash
tail -30 .aurora_knowledge/autonomous_monitoring_$(date +%Y%m%d).log
```

### ⭐ Clean Shutdown
```bash
python3 x-stop
```

---

## 🆘 Emergency Commands

### Aurora Not Responding?
```bash
# Quick restart
python3 x-nexus restart chat
```

### All Services Down?
```bash
python3 x-stop
sleep 3
python3 x-start
```

### Port Already in Use?
```bash
# Find what's using the port
lsof -i :5003

# Kill it
kill -9 $(lsof -t -i :5003)

# Restart
python3 x-nexus start chat
```

### Nuclear Option (Kill Everything)
```bash
pkill -f luminar_nexus
pkill -f "uvicorn.*500[0-2]"
pkill -f vite
sleep 3
python3 x-start
```

---

## 📚 Documentation References

- **Full Phase 1 Summary:** `.aurora_knowledge/PHASE1_FINAL_100_PERCENT.md`
- **Implementation Log:** `.aurora_knowledge/AURORA_PHASE1_IMPLEMENTATION_LOG.md`
- **Project Analysis:** `.aurora_knowledge/AURORA_CROSS_REFERENCE_ANALYSIS.md`
- **Test Results:** `.aurora_knowledge/PHASE1_TEST_RESULTS.md`

---

**Quick Start (Copy-Paste):**
```bash
# ⭐ Start Aurora (EASIEST WAY)
python3 x-start

# Check status
python3 x-nexus status

# Test Aurora
curl -s http://localhost:5003/api/chat -d '{"message":"Hello Aurora!"}' | jq -r '.response'

# Stop everything
python3 x-stop
```

**Available Services:**
- `vite` - Frontend (port 5173)
- `backend` - Backend API (port 5000)
- `bridge` - Bridge service (port 5001)
- `self-learn` - Self-learning server (port 5002)
- `chat` - Aurora chat AI (port 5003)

---

**Need Help?** Check the documentation in `.aurora_knowledge/` or talk to Aurora directly! 🚀
