# 🚀 Start Aurora-X - Quick Guide

## ✅ VERIFIED: Everything Works!

**Test Date**: December 3, 2025
**Status**: ✅ ALL SYSTEMS OPERATIONAL

---

## 🎯 One Command to Rule Them All

```bash
npm run dev
```

That's it! This starts everything you need:
- ✅ Express backend on port 5000
- ✅ React frontend with HMR
- ✅ Aurora Core (188 power units)
- ✅ Luminar Nexus V2
- ✅ WebSocket support
- ✅ All API routes

---

## 📍 Access Points

Once started, access Aurora at:

```
http://localhost:5000
```

### Available Routes:
- `/` - Home
- `/dashboard` - Dashboard
- `/chat` - Chat with Aurora
- `/servers` - Server Control
- `/luminar-nexus` - Orchestration
- `/intelligence` - Intelligence Tiers
- `/autonomous` - Autonomous Mode
- `/monitoring` - System Monitoring
- And 10+ more routes...

---

## 🔍 What Happens When You Start

```plaintext
[AURORA] Initializing 188 power units...
[AURORA] ✅ 100-worker autofixer pool initialized
[AURORA] Connecting to Python intelligence...
[AURORA] ✅ Aurora initialized with 188 power units
[AURORA] Status: {
  "status": "operational",
  "powerUnits": 188,
  "knowledgeCapabilities": 79,
  "executionModes": 66,
  "systemComponents": 43,
  "totalModules": 289,
  "autofixer": {
    "workers": 100,
    "active": 0,
    "queued": 0,
    "completed": 0
  }
}
[WebSocket] WebSocket server initialized
✅ Luminar Nexus V2 routes registered
[express] serving on port 5000
[express] vite hmr ready
```

---

## ✅ Verification Checklist

After starting, verify:

1. ✅ No errors in console
2. ✅ Port 5000 is listening
3. ✅ Aurora shows 188 power units
4. ✅ Vite HMR is ready
5. ✅ WebSocket initialized
6. ✅ Routes registered
7. ✅ Frontend loads at http://localhost:5000

---

## 🛠️ Other Useful Commands

### Check Status
```bash
npm run x-status
```

### Stop All Services
```bash
npm run x-stop
```

### Build for Production
```bash
npm run build
```

### Check Package Info
```bash
npm list --depth=0
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Then restart
npm run dev
```

### Dependencies Missing
```bash
npm install
npm run dev
```

### TypeScript Errors
```bash
npm run check
```

---

## 🎨 Development Tips

### Hot Module Replacement (HMR)
- Edit any `.tsx` file in `client/src/`
- Changes appear instantly in browser
- No manual refresh needed

### API Development
- Edit `server/routes.ts` for new endpoints
- Server auto-restarts on changes
- Test with: `curl http://localhost:5000/api/...`

### Add New Page
1. Create `client/src/pages/my-page.tsx`
2. Add route to `client/src/App.tsx`
3. Navigate to `/my-page`

---

## 📦 What's Running

### Express Backend (TypeScript)
- **File**: `server/index.ts`
- **Port**: 5000
- **Features**:
  - REST API
  - WebSocket
  - Aurora Core
  - Luminar Nexus
  - Session management
  - Rate limiting

### React Frontend (TSX)
- **Root**: `client/`
- **Entry**: `client/src/main.tsx`
- **Router**: Wouter
- **Features**:
  - Hot reload
  - TypeScript
  - Tailwind CSS
  - Radix UI
  - React Query

### Aurora Core
- **Power Units**: 188
- **Workers**: 100
- **Modules**: 289
- **Capabilities**:
  - 79 Knowledge domains
  - 66 Execution modes
  - 43 System components

---

## 🔐 Default Credentials

**Admin Account**:
- Username: `admin`
- Password: ⚠️ Default (change in production!)

⚠️ **Security Warnings**:
- Using default JWT secret
- Using default admin password
- Set these environment variables for production:
  - `JWT_SECRET`
  - `ADMIN_PASSWORD`

---

## 🌟 Success Indicators

You know everything is working when you see:

```
✅ Aurora initialized with 188 power units
✅ 100-worker autofixer pool initialized
✅ Luminar Nexus V2 routes registered
✅ All 188 power units operational
[express] serving on port 5000
[express] vite hmr ready
```

---

## 📖 Further Reading

- See `AURORA_REBUILD_GUIDE.md` for architecture details
- Check `package.json` for all available scripts
- Review `server/index.ts` for server configuration
- Explore `client/src/` for frontend components

---

**Ready to go!** 🚀

Just run `npm run dev` and open http://localhost:5000
