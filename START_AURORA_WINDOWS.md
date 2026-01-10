# 🚀 Start Aurora on Windows - Step by Step

## ✅ **YES - Start from Terminal!**

You can use either:
- **Command Prompt (CMD)**
- **PowerShell** (recommended)

---

## 📝 **Step-by-Step Instructions:**

### 1. Open Terminal

**Option A: PowerShell (Recommended)**
- Press `Win + X`
- Select "Windows PowerShell" or "Terminal"
- OR right-click Start button → "Windows PowerShell"

**Option B: Command Prompt**
- Press `Win + R`
- Type `cmd` and press Enter

---

### 2. Navigate to Aurora Directory

```cmd
cd C:\Users\negry\Aurora-x
```

**OR if you're already there:**
```cmd
cd Aurora-x
```

---

### 3. Start Aurora

**Easiest way:**
```cmd
npm run dev
```

**That's it!** Aurora will start and you'll see output like:

```
[AURORA] Initializing 188 power units...
[AURORA] ✅ 100-worker autofixer pool initialized
[express] serving on port 5000
[express] vite hmr ready
```

---

### 4. Open Browser

Once you see "serving on port 5000", open:

```
http://localhost:5000
```

Then go to:
```
http://localhost:5000/chat
```

---

## 🎯 **Quick Copy-Paste Commands:**

```cmd
cd C:\Users\negry\Aurora-x
npm run dev
```

**Then open:** `http://localhost:5000/chat`

---

## 🛑 **To Stop:**

Press `Ctrl + C` in the terminal

---

## ❓ **If npm run dev doesn't work:**

Make sure Node.js is installed:
```cmd
node --version
npm --version
```

If not installed, download from: https://nodejs.org/

---

## ✅ **What You Should See:**

When Aurora starts successfully, you'll see:
- ✅ Backend API starting
- ✅ Frontend compiling
- ✅ Aurora Nexus V3 initializing
- ✅ Port 5000 listening
- ✅ "serving on port 5000" message

---

**That's it! Just run `npm run dev` in your terminal!** 🎉
