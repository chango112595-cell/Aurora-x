# 🌌 How to Use Aurora - Complete Guide

## 🎯 Aurora's Purpose

Aurora is designed to:
1. **Execute your requests** - Write code, fix bugs, build features, analyze systems
2. **Autonomously analyze** - Continuously scan and identify issues in the system
3. **Self-heal** - Automatically fix problems when detected

---

## 🚀 Access Methods

### Option 1: Web UI (Like Cursor) - **RECOMMENDED**

**Start Aurora:**
```cmd
cd C:\Users\negry\Aurora-x
npm run dev
```

**Access in Browser:**
```
http://localhost:5000/chat
```

**Features:**
- ✅ Beautiful web interface
- ✅ Real-time chat with Aurora
- ✅ Code generation and execution
- ✅ System monitoring dashboard
- ✅ File browser and editor
- ✅ Task execution interface

---

### Option 2: Terminal Chat (Command Line)

**Full Power Mode** (All 188 tiers, 66 execution modes, 550+ modules):
```cmd
cd C:\Users\negry\Aurora-x
python tools/aurora_terminal_chat_full_power.py
```

**Or use the launcher:**
```bash
./aurora-terminal-chat
```

**Features:**
- ✅ Direct terminal access
- ✅ All Aurora capabilities
- ✅ Persistent memory
- ✅ Autonomous execution
- ✅ Self-learning

---

## 💬 How to Talk to Aurora

### Basic Commands

**Ask Aurora to do something:**
```
"Create a Python function to sort a list"
"Fix the bug in server/routes.ts"
"Analyze the codebase for security issues"
"Build a REST API for user management"
```

**Request system analysis:**
```
"Analyze the entire system"
"Scan for all issues"
"Check system health"
"Find all bugs"
```

**Autonomous mode:**
```
"Aurora, fix yourself"
"Autonomously analyze the system"
"Identify all issues and fix them"
```

---

## 🤖 Autonomous System Analysis

### How Aurora Analyzes Automatically

Aurora runs **autonomous analysis** in the background:

1. **Continuous Monitoring** (Every 30 seconds):
   - Service health checks
   - System resource monitoring
   - Network connectivity

2. **Code Scanning** (Every 10 minutes):
   - Syntax errors
   - Import errors
   - Type errors
   - Security vulnerabilities
   - Code quality issues

3. **Predictive Analysis**:
   - Identifies potential issues before they occur
   - Trend analysis
   - Anomaly detection

### What Gets Analyzed

- ✅ **Code Quality**: Syntax, imports, types, encoding
- ✅ **System Health**: Services, ports, resources
- ✅ **Performance**: Memory, CPU, response times
- ✅ **Security**: Vulnerabilities, exposed secrets
- ✅ **Network**: Connectivity, port conflicts

### Automatic Fixing

When issues are detected:
1. Aurora analyzes the root cause
2. Generates a fix strategy
3. Executes the fix (if safe)
4. Validates the fix worked
5. Reports results

---

## 🎯 Executing Requests

### Example 1: Code Generation

**You say:**
```
"Create a function that calculates fibonacci numbers"
```

**Aurora:**
- Generates the code
- Tests it
- Provides documentation
- Saves it to the appropriate location

### Example 2: Bug Fixing

**You say:**
```
"Fix the error in server/aurora.ts line 45"
```

**Aurora:**
- Analyzes the error
- Identifies root cause
- Generates fix
- Tests the fix
- Applies it

### Example 3: System Analysis

**You say:**
```
"Analyze the entire Aurora system and report all issues"
```

**Aurora:**
- Scans all code files
- Checks system health
- Identifies issues by severity
- Generates comprehensive report
- Optionally fixes issues

---

## 🔍 Triggering Full System Analysis

### Via Web UI

1. Go to `http://localhost:5000/chat`
2. Type: `"Run full system analysis"`
3. Aurora will:
   - Scan all files
   - Check all services
   - Identify all issues
   - Generate report

### Via Terminal

```python
# In terminal chat
"Analyze the entire system and identify all issues"

# Or use the Python API directly
from aurora_nexus_v3.workers.issue_detector import IssueDetector
detector = IssueDetector()
await detector.scan_directory(".")
```

### Via API

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Run full system analysis"}'
```

---

## 📊 Monitoring Aurora's Analysis

### Check Detected Issues

**Web UI:**
- Go to `http://localhost:5000/dashboard`
- View "System Health" section
- See detected issues and fixes

**Terminal:**
```python
# In terminal chat
"Show me all detected issues"
"List system problems"
"What issues have you found?"
```

**API:**
```bash
curl http://localhost:5000/api/aurora/status
```

---

## 🛠️ Advanced Usage

### Autonomous Mode

Tell Aurora to work independently:
```
"Aurora, autonomously analyze and fix all issues"
"Work on improving the system yourself"
"Identify and fix problems without asking"
```

### Specific Analysis

```
"Analyze only security issues"
"Check for performance problems"
"Scan for code quality issues"
"Find all import errors"
```

### Continuous Monitoring

Aurora automatically:
- Monitors every 30 seconds
- Scans code every 10 minutes
- Predicts future issues
- Auto-fixes when safe

---

## 📝 Example Conversation

```
You: "Aurora, analyze the system"

Aurora: "🔍 Starting comprehensive system analysis...
         Scanning 550+ modules...
         Checking 300 workers...
         Analyzing code quality...

         ✅ Analysis complete!

         Found:
         - 2 critical issues (auto-fixed)
         - 5 high priority issues
         - 12 medium priority issues
         - 23 low priority issues

         All critical issues have been resolved.
         Would you like me to fix the remaining issues?"
```

---

## 🎨 Interface Comparison

### Web UI (http://localhost:5000/chat)
- ✅ Visual interface
- ✅ Code highlighting
- ✅ File browser
- ✅ Real-time updates
- ✅ Dashboard views

### Terminal Chat
- ✅ Direct access
- ✅ Scriptable
- ✅ Full power mode
- ✅ Persistent memory
- ✅ Autonomous execution

**Recommendation**: Use Web UI for daily use, Terminal for advanced/automated tasks.

---

## 🚀 Quick Start Examples

### 1. Start Aurora
```cmd
cd C:\Users\negry\Aurora-x
npm run dev
```

### 2. Open Browser
```
http://localhost:5000/chat
```

### 3. First Request
```
"Hello Aurora! Analyze this system and tell me what you find."
```

### 4. Execute Task
```
"Create a Python script that monitors system resources"
```

### 5. Request Fix
```
"Fix any issues you found in the previous analysis"
```

---

## 🔧 Configuration

### Enable/Disable Auto-Fix

Aurora asks before fixing critical issues by default. To enable full autonomy:

**Via Chat:**
```
"Enable autonomous fixing for all issues"
```

**Via Config:**
```python
# In aurora_nexus_v3/core/universal_core.py
AUTO_FIX_ENABLED = True
AUTO_FIX_CRITICAL = True  # Fix critical issues without asking
```

---

## 📚 More Information

- **API Documentation**: See `AURORA_X_FUNCTIONS.md`
- **System Status**: `http://localhost:5000/api/aurora/status`
- **Worker Status**: `http://localhost:5000/api/workers/status`
- **Issue History**: Check logs in `logs/` directory

---

**Aurora is ready! Start chatting and she'll analyze, execute, and fix!** 🌟
