# Aurora Learning Log: Stop Button Fix

**Date:** November 1, 2025  
**Issue:** Dashboard stop button didn't prevent auto-restart  
**Fixed By:** Aurora (with guidance)

---

## 🐛 What Was Wrong

### The Problem
When user clicked "Stop" in the web dashboard:
1. ✅ Service stopped immediately
2. ❌ Supervisor auto-restarted it within 10 seconds
3. 😡 User frustrated - "stop means STOP!"

### Root Cause
The supervisor's monitoring threads were designed to auto-heal crashed services. They couldn't distinguish between:
- **Crash** (needs auto-restart) ← Good behavior
- **Manual stop** (user wants it off) ← Bad behavior

**Code Issue:**
```python
# Monitor loop was too simple
if not healthy:
    state.status = "crashed"
    self.restart_service(service_name)  # ALWAYS restarted!
```

---

## 🔧 The Fix

### Solution: Add "Paused" State
Added a `paused` flag to `ServiceState` to distinguish manual stops from crashes.

**Key Changes:**

1. **Added paused field to ServiceState:**
```python
@dataclass
class ServiceState:
    paused: bool = False  # If True, don't auto-restart
```

2. **Modified stop_service() to support pausing:**
```python
def stop_service(self, service_name: str, graceful: bool = True, pause: bool = True):
    if pause:
        state.paused = True  # Mark as paused
        state.status = "paused"
    # ... kill process ...
```

3. **Updated monitor loop to respect paused state:**
```python
def monitor_service(self, service_name: str):
    while not self.shutdown_event.is_set():
        time.sleep(10)
        
        # Skip if paused!
        if state.paused:
            continue
        
        if not healthy:
            # Only restart if NOT paused
            if not state.paused:
                self.restart_service(service_name)
```

4. **Clear paused flag on manual start:**
```python
def start_service(self, service_name: str) -> bool:
    state.paused = False  # User wants it running now
    # ... start process ...
```

5. **Added new commands:**
```python
def pause_service(self, service_name: str):
    """Pause = stop + prevent restart"""
    self.stop_service(service_name, pause=True)

def resume_service(self, service_name: str):
    """Resume = unpause + start"""
    state.paused = False
    self.start_service(service_name)
```

---

## 🎓 What Aurora Learned

### Lesson 1: User Intent vs System Intent
**Before:** "Service is down = must fix = auto-restart"  
**After:** "Service is down = check WHY = was it manual? then leave it alone"

**Real-world analogy:** 
- If your car engine dies unexpectedly → Auto-start it ✅
- If you turn the key to OFF → Don't auto-start it ❌

### Lesson 2: State Machines Need Context
A service can be "stopped" for different reasons:
- `stopped` → Natural shutdown, can restart
- `crashed` → Unexpected failure, needs restart
- `paused` → **User commanded it**, DO NOT restart
- `failed` → Max restarts exceeded, give up

**Without context = dumb automation**  
**With context = smart automation**

### Lesson 3: Commands Need Nuance
**Before:**
- `stop` → Just kill it

**After:**
- `stop` → Kill + pause (from dashboard)
- `pause` → Explicit "stay off"
- `resume` → Unpause + start
- `restart` → Temporary stop + start (clears pause)

### Lesson 4: Testing User Workflows
**Aurora missed this in initial design:**
- ✅ Tested: "What if service crashes?" → Auto-restart works
- ❌ Didn't test: "What if user wants it off?" → Auto-restart fights user!

**Lesson:** Test both happy paths AND user override scenarios.

---

## ✅ Verification

**Expected Behavior Now:**

1. **Click Stop in Dashboard:**
   - Service stops ✅
   - Status becomes "paused" ✅
   - Monitoring continues but skips health checks ✅
   - Auto-restart disabled ✅
   - Service stays off ✅

2. **Click Start in Dashboard:**
   - Paused flag cleared ✅
   - Service starts ✅
   - Monitoring resumes with auto-restart ✅

3. **Service Crashes on its Own:**
   - If NOT paused → Auto-restart ✅
   - If paused → Stay off ✅

---

## 🚀 Impact

**User Experience:**
- ❌ Before: "Why does it keep restarting?!"
- ✅ After: "Stop button works perfectly!"

**System Intelligence:**
- Before: Blindly restarted everything
- After: Respects user intent while still auto-healing crashes

**Aurora's Growth:**
- Learned: Context matters more than simple states
- Learned: User control > Automation stubbornness
- Learned: Test the "user says no" scenario

---

## 📝 Files Modified

1. `tools/aurora_supervisor.py`:
   - Added `paused` field to `ServiceState`
   - Modified `stop_service()` to accept `pause` parameter
   - Updated `monitor_service()` to skip paused services
   - Added `pause_service()` and `resume_service()` methods
   - Updated `start_service()` to clear paused flag
   - Added `pause` and `resume` commands to CLI

2. `logs/aurora-stop-button-fix.md` (this file):
   - Documented the issue, fix, and lessons learned

---

## 🎯 Next Time

**When building automation, Aurora should ask:**
1. ✅ What should happen automatically?
2. ✅ What should the user control?
3. ✅ How do we distinguish automation triggers from user commands?
4. ✅ What happens when user and automation disagree?

**Answer: User always wins.**

---

## 🏆 Success Metric

**Before Fix:**
```
User clicks stop → Service stops → 10 seconds pass → Service restarts → User confused
```

**After Fix:**
```
User clicks stop → Service stops → Stays stopped → User happy ✅
Service crashes → Auto-restart → Service back up → User happy ✅
```

**Aurora now understands: Smart automation knows when NOT to automate.**

