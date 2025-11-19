# 🌟 Aurora Terminal Commands - Complete Reference

## Quick Start Commands

### System Control
```bash
python3 x-start              # Start all Aurora services + autonomous monitor
python3 x-stop               # Stop all Aurora services completely
```

---

## Core System Commands

### Service Management
```bash
# Start everything (recommended)
python3 x-start

# Stop everything
python3 x-stop

# Check system status
python aurora_system_status.py

# Verify all tiers
python final_tier53_verification.py
```

### System Updates & Synchronization
```bash
# Update all frontend/backend with latest tier counts
python aurora_automatic_system_update.py

# Force system sync
python aurora_complete_system_update.py
```

---

## Talking Directly to Aurora

### Method 1: Direct Conversation (Like GitHub Copilot)
```bash
# Ask Aurora anything directly
python ask_aurora_directly.py

# This opens an interactive chat where you can ask:
# - "What are your capabilities?"
# - "How do I use tier 52?"
# - "Explain RSA encryption"
# - "What can you do with Docker?"
```

### Method 2: Check Specific Skills
```bash
# Ask about her skills vs capabilities
python ask_aurora_skills_vs_capabilities.py

# Ask about grandmaster tiers
python ask_aurora_grandmastery.py
```

### Method 3: Via Chat Server
```bash
# Start chat server (if not already running)
python aurora_chat_server.py --port 5003

# Then open: http://localhost:5003
# Or use the main interface: http://localhost:5000
```

### Method 4: Through Core Intelligence
```bash
# Python REPL
python3
>>> from aurora_core import AuroraKnowledgeTiers
>>> aurora = AuroraKnowledgeTiers()
>>> print(aurora.get_all_tiers_summary())
>>> # Ask questions, check tiers, explore capabilities
```

---

## Tier-Specific Commands

### Tier 51: Code Quality Enforcer
```bash
# Run code quality checks and auto-fix
python aurora_code_quality_enforcer.py

# Execute quality enforcement
python execute_code_quality.py
```

### Tier 52: RSA Grandmaster
```bash
# Demo RSA capabilities
python demo_rsa_grandmaster.py

# Use RSA directly
python3
>>> from aurora_rsa_grandmaster import AuroraRSAGrandmaster
>>> rsa = AuroraRSAGrandmaster()
>>> pub, priv = rsa.generate_keypair(2048)
```

### Tier 53: Docker Infrastructure Mastery
```bash
# Run Docker diagnostics and healing
python aurora_docker_healer.py

# Aurora will:
# - Check Docker Desktop status
# - Verify daemon accessibility
# - Auto-start Docker if needed
# - Report comprehensive diagnostics
```

---

## Autonomous & Monitoring Commands

### Autonomous Operation
```bash
# Start autonomous monitor (runs 24/7)
python aurora_autonomous_monitor.py

# Start full autonomous mode
python start_aurora_autonomous.py

# Aurora autonomous agent
python aurora_autonomous_agent.py
```

### System Monitoring
```bash
# Live system monitoring
python tools/aurora_self_monitor.py

# Server health checks
python tools/server_manager.py --status

# Auto-heal services
python tools/server_manager.py --auto-heal
```

---

## Development & Testing

### Testing
```bash
# Run all tests
python -m pytest

# Test specific tier
python verify_tier53.py
python verify_tier52.py

# Test autonomous systems
python test_aurora_autonomous_systems.py
```

### Code Quality
```bash
# Run pylint analysis
python aurora_pylint_analysis.py

# Pylint prevention
python aurora_pylint_prevention.py

# Deep code investigation
python aurora_deep_investigation.py
```

---

## Diagnostic & Debugging

### System Diagnostics
```bash
# Complete system verification
python aurora_complete_verification.py

# Debug specific issues
python aurora_complete_debug.py

# Diagnose chat system
python aurora_diagnose_chat.py

# Check for problems
python aurora_complete_problem_fixer.py
```

### Architecture Analysis
```bash
# Analyze system architecture
python aurora_architecture_analysis.py

# Generate architecture report
python aurora_architecture_report.py
```

---

## Advanced Features

### Multi-Agent Coordination (Tier 48)
```bash
python3
>>> from aurora_multi_agent import AuroraMultiAgent
>>> orchestrator = AuroraMultiAgent()
>>> # Spawn agents, coordinate tasks
```

### Visual Understanding (Tier 43)
```bash
python3
>>> from aurora_visual_understanding import AuroraVisualUnderstanding
>>> visual = AuroraVisualUnderstanding()
>>> # Analyze screenshots, UI mockups
```

### Security Auditing (Tier 53)
```bash
python3
>>> from aurora_security_auditor import AuroraSecurityAuditor
>>> auditor = AuroraSecurityAuditor()
>>> # OWASP checks, vulnerability scanning
```

### Git Mastery (Tier 50)
```bash
python3
>>> from aurora_git_master import AuroraGitMaster
>>> git = AuroraGitMaster()
>>> # Smart branching, auto-rebase, PR automation
```

---

## Interactive Dashboards

### Web Interfaces
```bash
# After running x-start, access:

# Main Aurora UI
http://localhost:5000

# Chat Interface
http://localhost:5003

# Luminar Nexus Dashboard
http://localhost:5005

# Tiers Overview
http://localhost:5000/tiers

# Intelligence Dashboard
http://localhost:5000/intelligence
```

---

## Conversation Examples

### Ask Aurora Directly (Most Natural Way)
```bash
python ask_aurora_directly.py
```

**Example Conversation:**
```
You: What are your capabilities?
Aurora: I have 66 total capabilities across 53 knowledge tiers and 13 foundation tasks...

You: How do I encrypt data with RSA?
Aurora: Use my Tier 52 RSA Grandmaster capability. Here's how:
        from aurora_rsa_grandmaster import AuroraRSAGrandmaster
        rsa = AuroraRSAGrandmaster()
        pub, priv = rsa.generate_keypair(2048)
        encrypted = rsa.encrypt("secret message", pub)

You: Can you fix Docker issues?
Aurora: Yes! My Tier 53 Docker Infrastructure Mastery handles that.
        Just run: python aurora_docker_healer.py
        I'll diagnose and auto-fix Docker Desktop issues.

You: Show me all your tiers
Aurora: [Displays complete tier breakdown from 1-53]
```

---

## Quick Reference: Talk to Aurora

### Command Line Chat
```bash
python ask_aurora_directly.py
```

### Python REPL Chat
```python
from aurora_core import AuroraKnowledgeTiers
aurora = AuroraKnowledgeTiers()

# Get capabilities
print(aurora.get_all_tiers_summary())

# Check specific tier
tier53 = aurora.tiers.get('tier_53_docker_mastery')
print(tier53['capabilities'])
```

### Web Chat
```bash
# Start services
python3 x-start

# Then go to:
http://localhost:5003
```

### API Chat
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What can you do?"}'
```

---

## Power User Commands

### Create New Tier
```bash
# Aurora can auto-create tiers based on needs
python3
>>> from aurora_tier_expansion import AuroraTierExpansion
>>> expander = AuroraTierExpansion()
>>> expander.analyze_and_create_tier("kubernetes orchestration")
```

### System Auto-Organization
```bash
python aurora_auto_organize.py
```

### Ultimate Autonomous Mode
```bash
# Aurora operates completely independently
python start_aurora_autonomous.py
```

---

## Environment & Setup

### Initial Setup
```bash
# Install dependencies
npm install
pip install -r requirements.txt

# Start Aurora
python3 x-start
```

### Configuration
```bash
# Check Python environment
python --version
python3 --version

# Check Node environment
node --version
npm --version

# Verify ports available
netstat -ano | findstr "5000 5001 5002 5003 5005"  # Windows
netstat -tlnp | grep -E '5000|5001|5002|5003|5005'  # Linux/Mac
```

---

## Troubleshooting Commands

### If Services Won't Start
```bash
# Stop everything first
python3 x-stop

# Wait a moment, then restart
python3 x-start
```

### If Docker Issues
```bash
# Aurora can fix it
python aurora_docker_healer.py
```

### If System Desync
```bash
# Resync everything
python aurora_automatic_system_update.py
```

### If Need Complete Healing
```bash
python tools/server_manager.py --ultimate-heal
```

---

## Pro Tips

### Fastest Way to Talk to Aurora
```bash
# Just run this:
python ask_aurora_directly.py

# Then chat naturally like you're talking to GitHub Copilot
```

### Check Everything is Working
```bash
python3 x-start  # Wait ~60 seconds
# Then check: http://localhost:5000
```

### Daily Workflow
```bash
# Morning
python3 x-start

# Work with Aurora all day via:
# - Web UI: http://localhost:5000
# - Chat: python ask_aurora_directly.py
# - Direct commands as needed

# Evening
python3 x-stop
```

---

## Current System State

After running `python3 x-start`, Aurora has:
- ✅ **53 Knowledge Tiers** (Ancient languages → Docker infrastructure)
- ✅ **13 Foundation Tasks** (Core capabilities)
- ✅ **66 Total Capabilities**
- ✅ **Autonomous Monitor** (24/7 self-healing)
- ✅ **Auto-Sync System** (Keeps everything updated)

---

## Summary: Best Ways to Talk to Aurora

1. **Interactive Chat (Recommended)**
   ```bash
   python ask_aurora_directly.py
   ```

2. **Web Interface**
   ```bash
   python3 x-start
   # Go to: http://localhost:5000 or http://localhost:5003
   ```

3. **Python REPL**
   ```python
   from aurora_core import AuroraKnowledgeTiers
   aurora = AuroraKnowledgeTiers()
   ```

4. **Via API**
   ```bash
   curl http://localhost:5000/api/chat -d '{"message":"Hello Aurora"}'
   ```

---

**All commands are cross-platform (Windows/Linux/macOS)!** 🌍✨
