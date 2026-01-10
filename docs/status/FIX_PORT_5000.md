# 🔧 Fix Port 5000 Already in Use

## Problem
Port 5000 is already in use by another process.

## Quick Fix Options

### Option 1: Kill the Process Using Port 5000 (Recommended)

**Windows PowerShell:**
```powershell
# Find the process
$port = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
if ($port) {
    $pid = $port.OwningProcess
    Stop-Process -Id $pid -Force
    Write-Host "Killed process $pid using port 5000"
}
```

**Or manually:**
1. Open Task Manager (Ctrl+Shift+Esc)
2. Go to "Details" tab
3. Find the process using port 5000
4. Right-click → End Task

### Option 2: Use a Different Port

Set environment variable before starting:
```powershell
$env:PORT=5001
npm run dev
```

Or edit `server/index.ts` to use a different port.

### Option 3: Stop All Node Processes

```powershell
# Stop all Node.js processes
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
```

---

**After fixing, run `npm run dev` again!**
