# 🚀 How to Start Aurora - Quick Reference

## 🎯 **EASIEST WAY - One Command**

### Windows (PowerShell):
```powershell
npm run dev
```

### Linux/Mac:
```bash
./aurora-start
```

**OR:**
```bash
npm run dev
```

---

## 📍 **What This Starts:**

✅ **Backend API** (Express + TypeScript) on port **5000**
✅ **Frontend** (React + Vite) on port **5000**
✅ **Chat System** - Talk to Aurora
✅ **Aurora Nexus V3** - Universal Consciousness System (background)
✅ **All Core Services** - 300 Workers, 188 Tiers, 66 AEMs, 550 Modules

---

## 🌐 **Access Points:**

Once started, open your browser to:

```
http://localhost:5000
```

### Available Routes:
- `/` - Home page
- `/chat` - Chat with Aurora
- `/dashboard` - System dashboard
- `/servers` - Server control
- `/luminar-nexus` - Orchestration
- `/intelligence` - Intelligence tiers
- `/autonomous` - Autonomous mode
- `/monitoring` - System monitoring

---

## 🔧 **Alternative Start Methods:**

### 1. Start Aurora Nexus V3 Only (Python Core)
```bash
python aurora_nexus_v3/main.py
```

### 2. Start Full System (All Services)
```bash
# Windows
python x-start

# Linux/Mac
./x-start
```

This starts:
- Backend API + Frontend (port 5000)
- Aurora Bridge (port 5001)
- Aurora Nexus V3 (port 5002)
- Luminar Nexus V2 (port 8000)

### 3. Start Individual Services

**Backend only:**
```bash
npm run backend
# OR
tsx server/index.ts
```

**Frontend only:**
```bash
npm run frontend
# OR
vite
```

---

## ✅ **Verification:**

After starting, you should see:

```
[AURORA] Initializing 188 power units...
[AURORA] ✅ 100-worker autofixer pool initialized
[AURORA] Connecting to Python intelligence...
[AURORA] ✅ Aurora initialized with 188 power units
[WebSocket] WebSocket server initialized
✅ Luminar Nexus V2 routes registered
[express] serving on port 5000
[express] vite hmr ready
```

---

## 🛑 **Stop Aurora:**

```bash
# Stop all services
npm run x-stop

# OR press Ctrl+C in the terminal
```

---

## 🐛 **Troubleshooting:**

### Port 5000 already in use?
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

### Check if services are running:
```bash
npm run x-status
```

### View logs:
```bash
# Aurora Nexus logs
tail -f ~/.aurora_nexus/logs.txt

# Or check console output
```

---

## 🎯 **Quick Test:**

1. **Start Aurora:**
   ```bash
   npm run dev
   ```

2. **Open browser:**
   ```
   http://localhost:5000
   ```

3. **Go to chat:**
   ```
   http://localhost:5000/chat
   ```

4. **Say hello to Aurora!** 👋

---

## 📊 **System Status:**

Once running, Aurora will show:
- ✅ 300 Autonomous Workers online
- ✅ 188 Grandmaster Tiers active
- ✅ 66 Advanced Execution Methods ready
- ✅ 550 Cross-Temporal Modules loaded
- ✅ 100% Production Ready

---

**That's it! Aurora is ready to use!** 🎉
