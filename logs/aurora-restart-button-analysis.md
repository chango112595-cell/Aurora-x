# Aurora Learning Log: Restart Button Behavior

**Date:** November 1, 2025  
**Observer:** Aurora  
**Learning Focus:** Understanding restart functionality and its current limitations

---

## 🔍 What Aurora Observed

### Current Service Status
After user clicked "Restart" button in dashboard:
- ❌ Aurora UI (5000): NOT running
- ✅ Backend API (5001): Running
- ❌ Self-Learning (5002): NOT running
- ❌ File Server (8080): NOT running

**Result:** Only 1 out of 4 services restarted successfully

### What Happened in the Logs

**User clicked Restart on multiple services:**
```
13:24:35 🔄 Restarting aurora-ui in 5s (attempt 1)
13:24:37 🔄 Restarting aurora-backend in 5s (attempt 1)
13:24:38 🔄 Restarting self-learning in 5s (attempt 1)
```

**Services stopped (with pause=True):**
```
13:24:40 Stopping service: aurora-ui (pause=True)
13:24:42 Stopping service: aurora-backend (pause=True)
13:24:43 Stopping service: self-learning (pause=True)
```

**Restart attempted:**
```
13:24:42 Starting service: aurora-ui
13:24:44 Starting service: aurora-backend
13:24:45 WARNING: Dependency aurora-backend not running, waiting...
13:24:46 ✅ Service aurora-ui started successfully on port 5000
13:24:47 ✅ Service aurora-backend started successfully on port 5001
```

**But then... they stopped again (not visible in recent logs)**

---

## 🐛 What's Wrong

### Problem 1: Restart Calls Stop with pause=True
The `restart_service()` method calls `stop_service()` which defaults to `pause=True`:

```python
def restart_service(self, service_name: str):
    # ...delay logic...
    self.stop_service(service_name, graceful=False)  # ← Uses default pause=True!
    time.sleep(2)
    if self.start_service(service_name):
        # ...
```

**Issue:** When restarting, we're PAUSING the service, then trying to start it. But if something goes wrong after the start, it stays paused.

### Problem 2: File Server Missing from Restart
Logs show only 3 services were restarted, not 4. File server wasn't even attempted.

### Problem 3: Services Disappearing After Restart
The logs show aurora-ui and aurora-backend started successfully at 13:24, but now (13:26+) only backend is running.

**Possible causes:**
- Health check failed and they were paused
- Process crashed and paused state prevented restart
- Monitoring thread stopped

---

## 🔧 What Aurora Needs to Fix

### Fix 1: Restart Should NOT Pause
```python
def restart_service(self, service_name: str):
    # ...
    self.stop_service(service_name, graceful=False, pause=False)  # ← Add pause=False
    time.sleep(2)
    # ...
```

**Reason:** Restart is a temporary stop. User wants it back up, not paused.

### Fix 2: Restart Should Clear Paused Flag
Even if service was previously paused, restart means "I want it running now":

```python
def restart_service(self, service_name: str):
    state = self.states[service_name]
    state.paused = False  # ← Clear pause before restarting
    # ...rest of restart logic...
```

### Fix 3: Dashboard Needs Better Error Handling
If restart fails, dashboard should show why (health check failed, dependency missing, etc.)

---

## 🎓 What Aurora Learned

### Lesson 1: Stop vs Restart Are Different Intents

| Button | User Intent | Should Pause? |
|--------|-------------|---------------|
| Stop | "Turn it off and leave it off" | ✅ Yes |
| Restart | "Bounce it to fix issues" | ❌ No |
| Start | "Turn it on" | ❌ No (clear pause) |

**Current bug:** Restart is treating services like Stop (pausing them)

### Lesson 2: Service States Are Tricky
A service can be:
1. Running → Everything good
2. Stopped normally → Can restart
3. Paused (manual stop) → Won't auto-restart
4. Crashed → Will auto-restart
5. Failed (max restarts) → Needs manual intervention

**Aurora confused restart with stop.** They're different operations:
- **Stop:** Running → Paused (don't auto-restart)
- **Restart:** Running → Stopped (temporary) → Running (auto-restart enabled)

### Lesson 3: Logs Tell Stories
Aurora learned to read logs chronologically:
1. Services started ✅
2. User clicked restart 🔄
3. Services stopped with pause=True ⏸️
4. Services started again ✅
5. **Mystery:** Services disappeared later ❓

**Aurora needs to investigate:** Why did they disappear after successful start?

### Lesson 4: Partial Success = Total Failure
In user's eyes:
- ❌ "1 out of 4 worked" = BROKEN
- ✅ "4 out of 4 worked" = WORKING

Aurora shouldn't celebrate partial success. **All or nothing.**

---

## ✅ Expected Behavior (After Fix)

**User clicks Restart on aurora-ui:**
1. Service stops (gracefully)
2. Paused flag = FALSE (or cleared)
3. Service starts
4. Monitoring resumes with auto-restart enabled
5. If it crashes later, auto-restart kicks in

**Currently broken because:**
- Paused flag = TRUE after restart
- Auto-restart disabled
- Service stays down if it fails health check

---

## 🚀 Next Steps for Aurora

1. **Fix restart_service()** to not pause services
2. **Test restart button** on all 4 services individually
3. **Check why services disappeared** after successful start
4. **Add better error reporting** to dashboard
5. **Document restart vs stop** in runbook

---

## 📊 Current vs Expected

**Current State:**
```
User clicks Restart
  ↓
Service stops with pause=True
  ↓
Service starts (paused=True still set??)
  ↓
Health check fails OR process crashes
  ↓
Auto-restart skipped (because paused=True)
  ↓
Service stays down ❌
```

**Expected State:**
```
User clicks Restart
  ↓
Service stops with pause=False
  ↓
Paused flag cleared
  ↓
Service starts
  ↓
Health check fails OR process crashes
  ↓
Auto-restart activated
  ↓
Service comes back up ✅
```

---

## 🎯 Aurora's Conclusion

**Stop button:** ✅ Working perfectly (learned this already)  
**Restart button:** ❌ Broken - pauses services when it shouldn't

**Root cause:** Restart is calling the same "pause" logic as stop, but they should behave differently.

**Aurora now understands:**
- Different buttons = different user intents
- Pause flag should only be set for manual stops, not restarts
- Testing individual features is important (stop works, restart doesn't)

**Next:** Fix the restart functionality so it clears pause and allows auto-restart.

