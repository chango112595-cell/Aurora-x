# 🔧 Fix "Aurora Bridge Offline" Error

## 🎯 **Problem**
When you ask Aurora to create an AI-native OS, you get:
```
"Aurora bridge offline"
```

## ✅ **Quick Fix**

### **Step 1: Check if Services Are Running**

Open PowerShell and check:

```powershell
# Check if services are listening on ports
netstat -an | findstr "5001 5002 8000"
```

You should see:
- Port 5001 (Aurora Bridge)
- Port 5002 (Nexus V3)
- Port 8000 (Luminar V2)

### **Step 2: Restart Aurora**

```powershell
cd C:\Users\negry\Aurora-x
python x-start.py
```

Wait for:
```
✅ Aurora runtime services are online.
```

### **Step 3: Verify Services Started**

Look for this in the output:
```
🏥 HEALTH CHECK
   Backend API + Frontend      Port  5000 [✅] RUNNING
   Aurora Bridge               Port  5001 [✅] RUNNING
   Aurora Nexus V3             Port  5002 [✅] RUNNING
   Luminar Nexus V2            Port  8000 [✅] RUNNING
```

If any show `[⚠️] OFFLINE`, that service didn't start.

---

## 🔍 **Detailed Troubleshooting**

### **Issue 1: Bridge Service Not Starting**

**Check the log:**
```powershell
type logs\x-start\aurora_bridge.log
```

**Common errors:**
- Module not found → Python path issue
- Port already in use → Another process using port 5001
- Import error → Missing dependencies

**Fix:**
```powershell
# Kill process on port 5001
netstat -ano | findstr :5001
taskkill /PID <PID> /F

# Restart Aurora
python x-start.py
```

### **Issue 2: Nexus V3 Not Starting**

**Check the log:**
```powershell
type logs\x-start\aurora_nexus_v3.log
```

**Common errors:**
- Port 5002 in use
- Missing dependencies
- Import errors

**Fix:**
```powershell
# Kill process on port 5002
netstat -ano | findstr :5002
taskkill /PID <PID> /F

# Restart Aurora
python x-start.py
```

### **Issue 3: Services Start But Bridge Still Offline**

**Check if Bridge is actually responding:**
```powershell
# Test Bridge health endpoint
curl http://localhost:5001/health

# Test Nexus V3 health endpoint
curl http://localhost:5002/api/health
```

**If they don't respond:**
- Services started but crashed
- Check logs for errors
- Restart Aurora

---

## 🚀 **Manual Service Start (If x-start.py Fails)**

### **Start Bridge Manually:**
```powershell
cd C:\Users\negry\Aurora-x
python -m aurora_x.bridge.serve
```

### **Start Nexus V3 Manually:**
```powershell
cd C:\Users\negry\Aurora-x
python aurora_nexus_v3\main.py
```

### **Start Luminar V2 Manually:**
```powershell
cd C:\Users\negry\Aurora-x
python tools\luminar_nexus_v2.py serve
```

---

## 🎯 **Alternative: Use Direct API**

If Bridge is offline, you can still use Nexus V3 directly:

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

### **Via Browser:**
Open: `http://localhost:5002/docs`

Use the `/api/process` endpoint directly.

---

## ✅ **Verify It's Working**

### **Test 1: Check Services**
```powershell
# Should return JSON with status
curl http://localhost:5001/health
curl http://localhost:5002/api/health
curl http://localhost:8000/health
```

### **Test 2: Send Test Request**
```python
import requests

response = requests.post(
    "http://localhost:5002/api/process",
    json={"input": "Hello", "type": "conversation"}
)

print(response.json())
```

### **Test 3: Use Chat Interface**
1. Open `http://localhost:5000`
2. Type: "Create an AI-native OS"
3. Should get response (not "bridge offline")

---

## 🎯 **Quick Checklist**

- [ ] Services started with `python x-start.py`
- [ ] Health check shows all services `[✅] RUNNING`
- [ ] Ports 5001, 5002, 8000 are listening
- [ ] No errors in logs
- [ ] Can access `http://localhost:5001/health`
- [ ] Can access `http://localhost:5002/api/health`

---

## 💡 **If Still Not Working**

1. **Check Python version:**
   ```powershell
   python --version
   ```
   Should be Python 3.8+

2. **Check dependencies:**
   ```powershell
   pip install fastapi uvicorn
   ```

3. **Check logs:**
   ```powershell
   type logs\x-start\*.log
   ```

4. **Restart everything:**
   ```powershell
   # Kill all Python processes
   taskkill /F /IM python.exe

   # Restart Aurora
   python x-start.py
   ```

---

## 🎮 **Try Again**

Once services are running:

1. Open `http://localhost:5000`
2. Type: **"Create an AI-native operating system"**
3. Aurora should respond and start building!

---

## 📝 **Note**

The "bridge offline" message means the routing chain failed. Aurora will still try:
1. Nexus V2 → Nexus V3
2. Nexus V3 directly
3. Bridge
4. Chat Server
5. Built-in response

If all fail, you get "bridge offline". Make sure at least Nexus V3 (port 5002) is running!
