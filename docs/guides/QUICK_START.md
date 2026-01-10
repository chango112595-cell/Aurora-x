# 🚀 Quick Start Guide

## ⚠️ Important: Always Start from the Aurora-x Directory!

You must be in the `Aurora-x` directory to run Aurora commands.

## 📍 Step 1: Navigate to Aurora-x

### Command Prompt (CMD):
```cmd
cd C:\Users\negry\Aurora-x
```

### PowerShell:
```powershell
cd C:\Users\negry\Aurora-x
```

## 🎯 Step 2: Start Aurora

### Command Prompt (CMD):
```cmd
npm run dev
```

### PowerShell:
```powershell
npm run dev
```

## ✅ Verify You're in the Right Directory

Before running `npm run dev`, check that you see:
- `package.json` file exists
- `server/` folder exists
- `secrets/` folder exists

## 🐛 Common Mistakes

### ❌ Wrong Directory:
```
C:\Users\negry> npm run dev
```
**Error**: `Could not read package.json`

### ✅ Correct Directory:
```
C:\Users\negry\Aurora-x> npm run dev
```
**Success**: Aurora starts!

## 📝 Quick Reference

```cmd
REM Navigate to Aurora
cd C:\Users\negry\Aurora-x

REM Start Aurora
npm run dev

REM Stop Aurora (if needed)
Ctrl+C

REM Kill stuck processes (if port 5000 is busy)
scripts\kill-aurora.bat
```

## 🌐 Access Aurora

Once started:
- **Web UI**: http://localhost:5000
- **Chat**: http://localhost:5000/chat
- **API**: http://localhost:5000/api
