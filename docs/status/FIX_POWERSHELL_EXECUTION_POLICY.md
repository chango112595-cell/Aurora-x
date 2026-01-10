# 🔧 Fix PowerShell Execution Policy Error

## Problem
PowerShell is blocking npm because script execution is disabled.

## Quick Fix Options

### Option 1: Use Command Prompt (CMD) Instead (Easiest)

**Don't use PowerShell - use Command Prompt:**
1. Press `Win + R`
2. Type `cmd` and press Enter
3. Navigate to Aurora:
   ```cmd
   cd C:\Users\negry\Aurora-x
   ```
4. Run:
   ```cmd
   npm run dev
   ```

### Option 2: Bypass Policy for Current Session (PowerShell)

**In PowerShell, run:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
npm run dev
```

This only affects the current PowerShell window.

### Option 3: Change Policy for Current User (PowerShell)

**In PowerShell (as Administrator):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
npm run dev
```

### Option 4: Use npx directly

```powershell
npx tsx server/index.ts
```

---

## Recommended: Use CMD (Command Prompt)

**CMD doesn't have this restriction!**

1. Open Command Prompt (not PowerShell)
2. `cd C:\Users\negry\Aurora-x`
3. `npm run dev`

That's it! 🎉
