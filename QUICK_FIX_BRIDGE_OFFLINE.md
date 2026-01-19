# ⚡ Quick Fix: "Bridge Offline" Error

## 🎯 **The Problem**
You asked Aurora to create an AI-native OS and got: **"Aurora bridge offline"**

## ✅ **The Fix (2 Steps)**

### **Step 1: Check What's Running**
```powershell
netstat -an | findstr "5001 5002 8000"
```

**You need:**
- ✅ Port 5001 (Bridge) - LISTENING
- ✅ Port 5002 (Nexus V3) - LISTENING ← **This is probably missing!**
- ✅ Port 8000 (Luminar V2) - LISTENING

### **Step 2: Restart Aurora**
```powershell
cd C:\Users\negry\Aurora-x
python x-start.py
```

**Wait for:**
```
🏥 HEALTH CHECK
   Aurora Bridge               Port  5001 [✅] RUNNING
   Aurora Nexus V3             Port  5002 [✅] RUNNING  ← Make sure this shows!
   Luminar Nexus V2            Port  8000 [✅] RUNNING
```

---

## 🚀 **If Nexus V3 Still Doesn't Start**

### **Start It Manually:**
```powershell
cd C:\Users\negry\Aurora-x
python aurora_nexus_v3\main.py
```

**Keep this window open** - Nexus V3 needs to stay running!

---

## 🎯 **Alternative: Use Nexus V3 Directly**

If Bridge is still offline, use Nexus V3 directly:

### **Via Browser:**
1. Open: `http://localhost:5002/docs`
2. Use the `/api/process` endpoint
3. Send: `{"input": "Create an AI-native OS", "type": "conversation"}`

### **Via Python:**
```python
import requests

response = requests.post(
    "http://localhost:5002/api/process",
    json={
        "input": "Create an AI-native operating system",
        "type": "conversation"
    }
)

print(response.json())
```

---

## ✅ **Verify It Works**

1. **Check services:**
   ```powershell
   netstat -an | findstr "5002"
   ```
   Should show `LISTENING`

2. **Test Nexus V3:**
   ```powershell
   curl http://localhost:5002/api/health
   ```
   Should return JSON

3. **Try your request again:**
   - Open `http://localhost:5000`
   - Type: "Create an AI-native OS"
   - Should work now!

---

## 💡 **Why This Happens**

The routing chain is:
1. Chat → Nexus V2 → Nexus V3 ✅
2. Chat → Nexus V3 directly ✅
3. Chat → Bridge → Nexus V3 ❌ (if Bridge offline)
4. Chat → Built-in response (shows "bridge offline")

**If Nexus V3 (port 5002) isn't running**, all routes fail and you get "bridge offline".

**Solution:** Make sure Nexus V3 starts! It's the core service that processes requests.
