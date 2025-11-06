# 🚀 Aurora-X Quick Reference Card

**Last Updated:** November 6, 2025

---

## ⚡ Most Common Commands

### Start Everything
```bash
python3 x-start
```

### Stop Everything
```bash
python3 x-stop
```

### Check Status
```bash
python3 x-nexus status
```

---

## 🎯 Individual Service Control

### Start a Service
```bash
python3 x-nexus start <service>
```

### Stop a Service
```bash
python3 x-nexus stop <service>
```

### Restart a Service
```bash
python3 x-nexus restart <service>
```

---

## 📋 Available Services

| Service | Port | Description |
|---------|------|-------------|
| `vite` | 5173 | Frontend UI |
| `chat` | 5003 | Aurora Chat AI |
| `backend` | 5000 | Backend API |
| `bridge` | 5001 | Bridge Service |
| `self-learn` | 5002 | Self-Learning Server |

---

## 🌐 Access Points

- **Frontend:** http://localhost:5173
- **Chat API:** http://localhost:5003/api/chat
- **Backend:** http://localhost:5000
- **Status:** `python3 x-nexus status`

---

## 🆘 Quick Fixes

### Restart Chat Server
```bash
python3 x-nexus restart chat
```

### Restart Frontend
```bash
python3 x-nexus restart vite
```

### Full Restart
```bash
python3 x-stop
sleep 2
python3 x-start
```

### Check What's Running
```bash
python3 x-nexus status
```

---

## 💬 Talk to Aurora

```bash
curl -X POST http://localhost:5003/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello Aurora!"}'
```

Or just open: http://localhost:5173

---

## 📚 Full Documentation

For complete command reference, see: `AURORA_COMMANDS.md`
