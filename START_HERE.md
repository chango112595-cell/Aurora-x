# 🚀 Aurora-X Quick Start

## ONE Command to Rule Them All

```bash
./aurora-start
```

That's it! This starts:
- ✅ Backend API (Express) on port 5000
- ✅ Frontend (React) on port 5000
- ✅ Chat System
- ✅ All core services

## What's Running?

| Service | Port | Status |
|---------|------|--------|
| Frontend + Backend | 5000 | ✅ Main app |
| Chat System | Built-in | ✅ Active |
| Aurora Nexus V3 | Console | ✅ Background |

## If You Want to Run Aurora Nexus V3 Separately

```bash
python3 aurora_nexus_v3/main.py
```

## Backend Reconstruction Status

✅ **COMPLETE** - All services rebuilt and working:
- aurora-chat.ts (Nov 29)
- conversation-detector.ts (Nov 29)
- execution-dispatcher.ts (Nov 29)
- luminar-routes.ts (Nov 28)
- Full auth system, corpus storage, RAG, etc.

## Troubleshooting

If port 5000 is busy:
```bash
lsof -i :5000
# Kill with: kill -9 <PID>
```

View logs:
```bash
tail -f ~/.aurora_nexus/logs.txt
```
