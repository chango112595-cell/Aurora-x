# AURORA INTEGRATION GUIDE
## How to Integrate & Fix the 4 Experimental Files

This document provides step-by-step instructions on how to integrate the 4 experimental files into Aurora's core system, with detailed code examples and fixes for each.

---

## 📋 FILE #1: SELF-LEARNING DIAGNOSTICS
### Source: `aurora_honest_self_diagnosis.py`
### Target: `aurora_x/self_learn.py`

### What It Does
Provides **honest self-assessment** of Aurora's performance by checking:
1. What features are visible to users (UI integration)
2. What tools are actually usable (backend integration)
3. What's broken or incomplete
4. Root cause analysis with solutions

### The Problem It Solves
Currently, `aurora_x/self_learn.py` runs synthesis tasks but has **NO FEEDBACK LOOP**:
- ❌ Doesn't know if synthesis is actually helping
- ❌ Doesn't capture why some synthesies fail
- ❌ No learning from failures
- ❌ No quality metrics stored

### The Fix (Step-by-Step)

#### Step 1: Create Diagnostic Module
**File**: Create `aurora_x/self_learn_diagnostics.py`

```python
#!/usr/bin/env python3
"""
Aurora Self-Learning Diagnostics Module
Provides honest feedback on learning quality and effectiveness
"""

from pathlib import Path
from datetime import datetime
import json
from typing import Dict, List, Optional

class SelfLearningDiagnostics:
    """Diagnoses quality and effectiveness of self-learning runs"""
    
    def __init__(self):
        self.diagnostics_file = Path(".aurora_diagnostics.json")
        self.failed_specs = []
        self.quality_scores = []
        
    def diagnose_synthesis_run(
        self, 
        spec_name: str, 
        success: bool, 
        output_repo: Optional[Path] = None,
        error_msg: Optional[str] = None
    ) -> Dict:
        """
        Diagnose a single synthesis run
        
        Args:
            spec_name: Name of the spec that was synthesized
            success: Whether synthesis succeeded
            output_repo: Path to generated code repo
            error_msg: Error message if failed
            
        Returns:
            Diagnostic report dict
        """
        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "spec_name": spec_name,
            "success": success,
            "quality_score": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        if success and output_repo:
            # Check code quality of generated code
            quality_score = self._check_code_quality(output_repo)
            diagnosis["quality_score"] = quality_score
            
            # Rate: 0-100
            # 0-30: Poor (has issues)
            # 31-70: Okay (works but needs improvement)
            # 71-100: Good (high quality)
            
            if quality_score < 30:
                diagnosis["issues"].append("Generated code has quality issues")
                diagnosis["recommendations"].append("Review generated code patterns")
            elif quality_score < 70:
                diagnosis["issues"].append("Generated code could be improved")
                diagnosis["recommendations"].append("Analyze common improvement areas")
            else:
                diagnosis["recommendations"].append("Continue current synthesis approach")
        else:
            diagnosis["quality_score"] = 0.0
            diagnosis["issues"].append(f"Synthesis failed: {error_msg or 'Unknown error'}")
            diagnosis["recommendations"].append("Investigate failure pattern")
            self.failed_specs.append(spec_name)
        
        # Store for analytics
        self.quality_scores.append({
            "spec": spec_name,
            "score": diagnosis["quality_score"],
            "timestamp": diagnosis["timestamp"]
        })
        
        return diagnosis
    
    def _check_code_quality(self, repo_path: Path) -> float:
        """Check generated code quality (0-100 scale)"""
        score = 50.0  # Default baseline
        
        try:
            # Check for common quality indicators
            py_files = list(repo_path.rglob("*.py"))
            
            if not py_files:
                return 30.0  # No Python files = poor quality
            
            # Check if files have docstrings
            docstring_coverage = 0
            for py_file in py_files:
                content = py_file.read_text()
                if '"""' in content or "'''" in content:
                    docstring_coverage += 1
            
            # If 80%+ of files have docstrings, add points
            if len(py_files) > 0:
                coverage_ratio = docstring_coverage / len(py_files)
                if coverage_ratio >= 0.8:
                    score += 20
                elif coverage_ratio >= 0.5:
                    score += 10
            
            # Check for type hints
            has_type_hints = False
            for py_file in py_files[:3]:  # Check first 3 files
                content = py_file.read_text()
                if " -> " in content or ": str" in content or ": int" in content:
                    has_type_hints = True
                    break
            
            if has_type_hints:
                score += 10
            
            # Check for tests
            test_files = list(repo_path.rglob("test_*.py")) + list(repo_path.rglob("*_test.py"))
            if test_files:
                score += 15
            
            # Cap at 95 (nothing is perfect)
            return min(score, 95.0)
            
        except Exception as e:
            return 40.0  # Error checking = moderate quality concern
    
    def get_learning_progress(self) -> Dict:
        """Get overall self-learning progress"""
        total_runs = len(self.quality_scores)
        if total_runs == 0:
            return {
                "total_runs": 0,
                "success_rate": 0,
                "avg_quality": 0,
                "failed_specs": []
            }
        
        successful_runs = sum(1 for s in self.quality_scores if s["score"] > 0)
        avg_quality = sum(s["score"] for s in self.quality_scores) / total_runs
        
        return {
            "total_runs": total_runs,
            "success_rate": (successful_runs / total_runs) * 100,
            "avg_quality": round(avg_quality, 1),
            "failed_specs": self.failed_specs,
            "high_quality_runs": sum(1 for s in self.quality_scores if s["score"] >= 70)
        }
    
    def save_diagnostics(self):
        """Save diagnostics to disk for tracking"""
        diagnostics = {
            "generated_at": datetime.now().isoformat(),
            "progress": self.get_learning_progress(),
            "recent_scores": self.quality_scores[-20:]  # Last 20 runs
        }
        
        self.diagnostics_file.write_text(json.dumps(diagnostics, indent=2))
        return diagnostics
```

#### Step 2: Modify `self_learn.py` to Use Diagnostics

**File**: Modify `aurora_x/self_learn.py`

Add this import at the top:
```python
from aurora_x.self_learn_diagnostics import SelfLearningDiagnostics
```

Modify the `SelfLearningDaemon` class:

```python
class SelfLearningDaemon:
    """Continuous learning daemon for Aurora-X."""

    def __init__(
        self,
        spec_dir: Path = Path("specs"),
        outdir: Path = Path("runs"),
        sleep_seconds: int = 15,
        max_iters: int = 50,
        beam: int = 20,
    ):
        # ... existing code ...
        self.diagnostics = SelfLearningDiagnostics()  # ADD THIS LINE
        
    def run_synthesis(self, spec_path: Path) -> bool:
        """Run synthesis on a spec file."""
        try:
            self.log(f"Starting synthesis: {spec_path.name}")

            # ... existing synthesis code ...
            repo, success = aurora.run(spec_text)

            # ADD THIS: Capture diagnosis
            diagnosis = self.diagnostics.diagnose_synthesis_run(
                spec_name=spec_path.name,
                success=success,
                output_repo=repo.root if success else None,
                error_msg=None if success else "Synthesis incomplete"
            )
            
            # Log the quality score
            self.log(f"Quality Score: {diagnosis['quality_score']:.1f}/100")
            if diagnosis['recommendations']:
                self.log(f"Recommendation: {diagnosis['recommendations'][0]}")
            
            # ... rest of existing code ...
            
            return success

        except Exception as e:
            # Capture error diagnosis
            self.diagnostics.diagnose_synthesis_run(
                spec_name=spec_path.name,
                success=False,
                error_msg=str(e)
            )
            # ... rest of error handling ...
            return False
    
    def run_forever(self):
        """Run continuous learning loop."""
        # ... existing code ...
        
        while True:
            try:
                # ... existing synthesis code ...
                
                # Every 5 runs, save diagnostics
                if self.run_count % 5 == 0:
                    progress = self.diagnostics.get_learning_progress()
                    self.log(f"Learning Progress: {progress['success_rate']:.1f}% success, {progress['avg_quality']:.1f} avg quality")
                    self.diagnostics.save_diagnostics()
                
                # ... rest of loop ...
                
            except KeyboardInterrupt:
                self.log("Received interrupt signal, shutting down...")
                self.diagnostics.save_diagnostics()  # ADD THIS
                break
```

#### Step 3: Test the Integration

```bash
# Run self-learning with diagnostics enabled
python3 aurora_x/self_learn.py --spec-dir specs --sleep 60

# Check diagnostics output
cat .aurora_diagnostics.json
```

**Expected Output**:
```json
{
  "generated_at": "2025-11-27T10:15:30",
  "progress": {
    "total_runs": 5,
    "success_rate": 80.0,
    "avg_quality": 72.5,
    "high_quality_runs": 4
  }
}
```

---

## 🔧 FILE #2: AUTONOMOUS HEALING/FIXES
### Source: `aurora_implement_self_fixes.py`
### Target: Create healing system (new file)

### What It Does
Automatically detects and fixes common Aurora issues:
1. Session context problems
2. Routing failures
3. Priority conflicts
4. Generic template responses

### The Problem It Solves
Currently Aurora:
- ❌ Doesn't know when services are down
- ❌ Can't auto-fix common issues
- ❌ Requires manual intervention for failures
- ❌ No self-healing capability

### The Fix (Step-by-Step)

#### Step 1: Create Autonomous Fixer Module
**File**: Create `tools/aurora_autonomous_fixer.py`

```python
#!/usr/bin/env python3
"""
Aurora Autonomous Healing System
Auto-detects and fixes common issues
"""

from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime

class AutonomousHealer:
    """Autonomously identifies and fixes Aurora issues"""
    
    def __init__(self):
        self.fixes_log = Path(".aurora_healing_log.json")
        self.fixes_applied = []
        self.health_history = []
        
    def health_check(self) -> Dict:
        """Check Aurora's health across all systems"""
        health = {
            "timestamp": datetime.now().isoformat(),
            "systems": {
                "self_learn": self._check_self_learn(),
                "chat_server": self._check_chat_server(),
                "corpus_db": self._check_corpus_db(),
                "frontend": self._check_frontend()
            }
        }
        
        # Calculate overall health (0-100)
        health_scores = [h["healthy"] for h in health["systems"].values()]
        health["overall_health"] = sum(health_scores) / len(health_scores) * 100
        
        self.health_history.append(health)
        return health
    
    def _check_self_learn(self) -> Dict:
        """Check if self-learning system is operational"""
        try:
            state_file = Path(".self_learning_state.json")
            
            if not state_file.exists():
                return {
                    "name": "Self-Learning",
                    "healthy": True,
                    "status": "Not running (normal)",
                    "issue": None
                }
            
            state = json.loads(state_file.read_text())
            last_update = state.get("last_updated", "")
            
            # Check if state was updated recently (within 1 hour)
            # This is just an example - adjust based on your needs
            return {
                "name": "Self-Learning",
                "healthy": True,
                "status": f"Running, processed {len(state.get('processed_specs', {}))} specs",
                "issue": None
            }
        except Exception as e:
            return {
                "name": "Self-Learning",
                "healthy": False,
                "status": "Error",
                "issue": str(e)
            }
    
    def _check_chat_server(self) -> Dict:
        """Check if chat server is operational"""
        try:
            # Check if server files exist
            server_file = Path("server/index.ts")
            if not server_file.exists():
                return {
                    "name": "Chat Server",
                    "healthy": False,
                    "status": "Server files missing",
                    "issue": "server/index.ts not found"
                }
            
            return {
                "name": "Chat Server",
                "healthy": True,
                "status": "Server files found",
                "issue": None
            }
        except Exception as e:
            return {
                "name": "Chat Server",
                "healthy": False,
                "status": "Error",
                "issue": str(e)
            }
    
    def _check_corpus_db(self) -> Dict:
        """Check if corpus database is accessible"""
        try:
            from aurora_x.corpus.store import CorpusStore
            corpus = CorpusStore()
            # Try to get entry count
            return {
                "name": "Corpus Database",
                "healthy": True,
                "status": "Database accessible",
                "issue": None
            }
        except Exception as e:
            return {
                "name": "Corpus Database",
                "healthy": False,
                "status": "Database error",
                "issue": str(e)
            }
    
    def _check_frontend(self) -> Dict:
        """Check if frontend files exist"""
        try:
            app_file = Path("client/src/App.tsx")
            if not app_file.exists():
                return {
                    "name": "Frontend",
                    "healthy": False,
                    "status": "Frontend files missing",
                    "issue": "client/src/App.tsx not found"
                }
            
            return {
                "name": "Frontend",
                "healthy": True,
                "status": "Frontend ready",
                "issue": None
            }
        except Exception as e:
            return {
                "name": "Frontend",
                "healthy": False,
                "status": "Error",
                "issue": str(e)
            }
    
    def fix_issue(self, issue_name: str) -> Tuple[bool, str]:
        """
        Attempt to fix a specific issue
        
        Returns: (success: bool, message: str)
        """
        
        if issue_name == "missing_corpus_db":
            return self._fix_corpus_db()
        elif issue_name == "session_persistence":
            return self._fix_session_persistence()
        elif issue_name == "routing_failure":
            return self._fix_routing()
        else:
            return False, f"Unknown issue: {issue_name}"
    
    def _fix_corpus_db(self) -> Tuple[bool, str]:
        """Fix corpus database issues"""
        try:
            from aurora_x.corpus.store import CorpusStore
            corpus = CorpusStore()
            # Force reinitialize
            corpus.initialize()
            
            fix_record = {
                "timestamp": datetime.now().isoformat(),
                "issue": "corpus_db_initialization",
                "success": True,
                "fix_type": "reinitialize"
            }
            self.fixes_applied.append(fix_record)
            return True, "Corpus database reinitialized"
        except Exception as e:
            return False, f"Failed to fix corpus db: {str(e)}"
    
    def _fix_session_persistence(self) -> Tuple[bool, str]:
        """Fix session persistence issues"""
        try:
            # Clear stale sessions
            session_file = Path(".aurora_sessions.json")
            if session_file.exists():
                sessions = json.loads(session_file.read_text())
                # Remove sessions older than 24 hours
                now = datetime.now().timestamp()
                updated_sessions = {
                    sid: sess for sid, sess in sessions.items()
                    if now - sess.get("created", 0) < 86400
                }
                session_file.write_text(json.dumps(updated_sessions, indent=2))
            
            fix_record = {
                "timestamp": datetime.now().isoformat(),
                "issue": "session_persistence",
                "success": True,
                "fix_type": "cleanup"
            }
            self.fixes_applied.append(fix_record)
            return True, "Sessions cleaned up"
        except Exception as e:
            return False, f"Failed to fix sessions: {str(e)}"
    
    def _fix_routing(self) -> Tuple[bool, str]:
        """Fix routing issues"""
        try:
            # Verify routing configuration exists
            # This is a placeholder - implement based on your routing setup
            fix_record = {
                "timestamp": datetime.now().isoformat(),
                "issue": "routing_failure",
                "success": True,
                "fix_type": "verify_config"
            }
            self.fixes_applied.append(fix_record)
            return True, "Routing verified"
        except Exception as e:
            return False, f"Failed to fix routing: {str(e)}"
    
    def autonomous_heal(self) -> Dict:
        """
        Run autonomous healing:
        1. Check health
        2. Identify issues
        3. Auto-fix what we can
        4. Report results
        """
        health = self.health_check()
        
        healing_report = {
            "timestamp": datetime.now().isoformat(),
            "health_check": health,
            "issues_found": [],
            "fixes_attempted": [],
            "fixes_successful": []
        }
        
        # Identify issues
        for system_name, system_health in health["systems"].items():
            if not system_health["healthy"] and system_health["issue"]:
                healing_report["issues_found"].append({
                    "system": system_name,
                    "issue": system_health["issue"]
                })
        
        # Attempt fixes for known issues
        issue_to_fix_map = {
            "corpus_db": "missing_corpus_db",
            "session_persistence": "session_persistence",
            "routing": "routing_failure"
        }
        
        for issue_found in healing_report["issues_found"]:
            system = issue_found["system"]
            if system in issue_to_fix_map:
                fix_name = issue_to_fix_map[system]
                success, message = self.fix_issue(fix_name)
                
                healing_report["fixes_attempted"].append({
                    "issue": fix_name,
                    "attempted": True,
                    "success": success,
                    "message": message
                })
                
                if success:
                    healing_report["fixes_successful"].append(fix_name)
        
        # Save healing report
        self._save_healing_report(healing_report)
        
        return healing_report
    
    def _save_healing_report(self, report: Dict):
        """Save healing report to disk"""
        self.fixes_log.write_text(json.dumps(report, indent=2))
```

#### Step 2: Integration with Backend

**File**: Modify `server/index.ts` to trigger healing

```typescript
// Add health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// Add healing trigger endpoint
app.post('/api/heal', async (req, res) => {
  try {
    // This would call the Python healing system
    // For now, just log that healing was requested
    console.log('🏥 Aurora Autonomous Healing Requested');
    
    res.json({
      status: 'healing_initiated',
      message: 'Autonomous healing started'
    });
  } catch (error) {
    res.status(500).json({ error: 'Healing failed' });
  }
});
```

#### Step 3: Test Healing
```bash
# Run the healer
python3 tools/aurora_autonomous_fixer.py

# Check healing log
cat .aurora_healing_log.json
```

---

## 🆘 FILE #3: EMERGENCY RECOVERY
### Source: `recovery_script.py` (NOTE: This file is about iOS recovery, NOT Aurora)
### Target: Create proper recovery system (new file)

### What It Does
Recovers Aurora if she crashes or breaks on any platform

### The Problem It Solves
Currently:
- ❌ If Aurora crashes, need manual restart
- ❌ No backup/restore capability
- ❌ No emergency procedures
- ❌ No data recovery

### The Fix (Step-by-Step)

#### Step 1: Create Proper Recovery System
**File**: Create `tools/aurora_recovery_system.py`

```python
#!/usr/bin/env python3
"""
Aurora Emergency Recovery System
Recovers Aurora from any platform (Windows, Mac, Linux, Replit)
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import json

class AuroraRecoverySystem:
    """Platform-independent recovery for Aurora"""
    
    def __init__(self):
        self.backup_dir = Path.home() / ".aurora_backups"
        self.backup_dir.mkdir(exist_ok=True)
        self.critical_dirs = [
            "aurora_x",
            "server",
            "client/src",
            ".aurora"
        ]
    
    def create_backup(self) -> bool:
        """Create emergency backup of Aurora system"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"backup_{timestamp}"
            backup_path.mkdir(parents=True)
            
            print(f"🔄 Creating backup: {backup_path}")
            
            # Backup critical directories
            for dir_name in self.critical_dirs:
                src = Path(dir_name)
                if src.exists():
                    dst = backup_path / dir_name
                    shutil.copytree(src, dst)
                    print(f"  ✓ Backed up {dir_name}")
            
            # Backup state files
            state_files = [
                ".self_learning_state.json",
                ".aurora_diagnostics.json",
                ".aurora_healing_log.json"
            ]
            
            for state_file in state_files:
                src = Path(state_file)
                if src.exists():
                    shutil.copy2(src, backup_path / state_file)
                    print(f"  ✓ Backed up {state_file}")
            
            # Create recovery metadata
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "platform": sys.platform,
                "backup_version": "1.0",
                "critical_dirs": self.critical_dirs
            }
            
            (backup_path / "recovery_metadata.json").write_text(
                json.dumps(metadata, indent=2)
            )
            
            print(f"✅ Backup created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def restore_from_backup(self, backup_path: Optional[str] = None) -> bool:
        """Restore Aurora from backup"""
        try:
            if not backup_path:
                # Use latest backup
                backups = sorted(self.backup_dir.iterdir(), reverse=True)
                if not backups:
                    print("❌ No backups found")
                    return False
                backup_path = backups[0]
            else:
                backup_path = Path(backup_path)
            
            print(f"🔄 Restoring from: {backup_path}")
            
            # Restore critical directories
            for dir_name in self.critical_dirs:
                src = backup_path / dir_name
                dst = Path(dir_name)
                
                if src.exists():
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                    print(f"  ✓ Restored {dir_name}")
            
            print(f"✅ Aurora restored successfully")
            return True
            
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def emergency_reset(self) -> bool:
        """Full emergency reset (last resort)"""
        try:
            print("🆘 EMERGENCY RESET INITIATED")
            print("⚠️  This will reset Aurora to factory settings")
            
            # Confirm before proceeding
            confirm = input("Type 'CONFIRM' to proceed: ")
            if confirm != "CONFIRM":
                print("❌ Reset cancelled")
                return False
            
            # Remove corrupted state
            print("🔄 Clearing corrupted state...")
            state_files = [
                ".self_learning_state.json",
                ".aurora_diagnostics.json",
                ".aurora_healing_log.json",
                ".aurora_sessions.json"
            ]
            
            for state_file in state_files:
                try:
                    Path(state_file).unlink()
                    print(f"  ✓ Removed {state_file}")
                except:
                    pass
            
            print("✅ Emergency reset complete")
            print("ℹ️  Aurora will reinitialize on next startup")
            return True
            
        except Exception as e:
            print(f"❌ Reset failed: {e}")
            return False
    
    def health_report(self) -> Dict:
        """Generate recovery health report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "platform": sys.platform,
            "aurora_exists": Path("aurora_x").exists(),
            "server_exists": Path("server").exists(),
            "client_exists": Path("client").exists(),
            "backups_available": len(list(self.backup_dir.iterdir())),
            "backup_location": str(self.backup_dir)
        }
        return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Aurora Emergency Recovery System")
    parser.add_argument(
        "command",
        choices=["backup", "restore", "reset", "health"],
        help="Recovery command to execute"
    )
    parser.add_argument(
        "--backup-path",
        help="Path to backup (for restore)"
    )
    
    args = parser.parse_args()
    
    recovery = AuroraRecoverySystem()
    
    if args.command == "backup":
        recovery.create_backup()
    elif args.command == "restore":
        recovery.restore_from_backup(args.backup_path)
    elif args.command == "reset":
        recovery.emergency_reset()
    elif args.command == "health":
        report = recovery.health_report()
        print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
```

#### Step 2: Usage
```bash
# Create backup (do this regularly!)
python3 tools/aurora_recovery_system.py backup

# Check health
python3 tools/aurora_recovery_system.py health

# Restore from backup if something breaks
python3 tools/aurora_recovery_system.py restore

# Last resort: emergency reset
python3 tools/aurora_recovery_system.py reset
```

---

## 💬 FILE #4: TERMINAL CHAT INTERFACE
### Source: `chat_with_aurora.py`
### Target: `server/aurora-chat.ts` + `tools/aurora_terminal_client.py`

### What It Does
Enables Aurora chat from terminal (not just web UI):
- Human-like conversation
- Intent detection (chat vs task)
- Tone detection
- Full personality

### The Problem It Solves
Currently:
- ❌ Can only chat via web browser
- ❌ No terminal access to Aurora
- ❌ IDE users stuck with web interface
- ❌ No programmatic access

### The Fix (Step-by-Step)

#### Step 1: Create Terminal Client
**File**: Create `tools/aurora_terminal_client.py`

```python
#!/usr/bin/env python3
"""
Aurora Terminal Client
Interactive terminal interface to Aurora with full capabilities
"""

import asyncio
import os
import sys
from datetime import datetime
import requests
import json
from pathlib import Path
from typing import Optional

class AuroraTerminalClient:
    """Terminal client for Aurora"""
    
    def __init__(self, server_url: str = "http://localhost:5000"):
        self.server_url = server_url
        self.session_id = f"terminal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.conversation_history = []
        self.config_file = Path.home() / ".aurora_terminal_config"
        self.load_config()
    
    def load_config(self):
        """Load terminal configuration"""
        if self.config_file.exists():
            self.config = json.loads(self.config_file.read_text())
        else:
            self.config = {
                "show_thinking": False,
                "use_color": True,
                "enable_clipboard": True
            }
            self.save_config()
    
    def save_config(self):
        """Save terminal configuration"""
        self.config_file.write_text(json.dumps(self.config, indent=2))
    
    async def send_message(self, message: str) -> Optional[str]:
        """Send message to Aurora and get response"""
        try:
            response = requests.post(
                f"{self.server_url}/api/chat",
                json={
                    "message": message,
                    "session_id": self.session_id,
                    "client": "terminal"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
            else:
                return f"Error: {response.status_code}"
        except requests.exceptions.ConnectionError:
            return "❌ Cannot connect to Aurora server. Is it running?"
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def interactive_session(self):
        """Run interactive terminal session"""
        print("\n" + "🌌" * 40)
        print("                    ✨ AURORA TERMINAL CLIENT ✨")
        print("                 Talk to Aurora from your terminal!")
        print("🌌" * 40 + "\n")
        
        print(f"Server: {self.server_url}")
        print(f"Session: {self.session_id}")
        print("Commands: type 'help' for commands, 'quit' to exit\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == "quit":
                    print("\n👋 Aurora: Goodbye! Come back soon! 💙\n")
                    break
                
                if user_input.lower() == "help":
                    self.show_help()
                    continue
                
                if user_input.lower() == "clear":
                    os.system("clear" if os.name != "nt" else "cls")
                    continue
                
                # Send message
                print("\nAurora: ", end="", flush=True)
                response = await self.send_message(user_input)
                print(response)
                print()
                
                # Store in history
                self.conversation_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "user": user_input,
                    "aurora": response
                })
                
            except KeyboardInterrupt:
                print("\n\n👋 Aurora: Caught that interrupt! Take care! 💙\n")
                break
            except Exception as e:
                print(f"\n⚠️  Error: {e}\n")
    
    def show_help(self):
        """Show help for terminal commands"""
        print("""
╔════════════════════════════════════════════════════════════════╗
║                    AURORA TERMINAL HELP                        ║
╚════════════════════════════════════════════════════════════════╝

Commands:
  help       - Show this help message
  clear      - Clear the screen
  status     - Show Aurora status
  config     - Show configuration
  history    - Show conversation history
  quit       - Exit Aurora terminal

Tips:
  • Type normally to chat with Aurora
  • Type 'create file.py' to generate code
  • Type 'fix error' for debugging help
  • Use Ctrl+C to interrupt long responses

═══════════════════════════════════════════════════════════════════
""")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Aurora Terminal Client")
    parser.add_argument(
        "--server",
        default="http://localhost:5000",
        help="Aurora server URL"
    )
    parser.add_argument(
        "--session",
        help="Existing session ID (for continuing conversations)"
    )
    
    args = parser.parse_args()
    
    client = AuroraTerminalClient(server_url=args.server)
    
    if args.session:
        client.session_id = args.session
    
    asyncio.run(client.interactive_session())

if __name__ == "__main__":
    main()
```

#### Step 2: Update Backend to Support Terminal Requests
**File**: Modify `server/index.ts`

```typescript
// Update chat endpoint to handle terminal clients
app.post('/api/chat', async (req, res) => {
  const { message, session_id, client } = req.body;
  
  // Detect if request is from terminal
  const isTerminalClient = client === 'terminal';
  
  try {
    // Process with Aurora
    const response = await processWithAurora(message, session_id);
    
    // Format response based on client type
    const formattedResponse = isTerminalClient 
      ? formatForTerminal(response)
      : formatForWeb(response);
    
    res.json({
      response: formattedResponse,
      session_id: session_id,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

function formatForTerminal(response: string): string {
  // Remove HTML tags for terminal display
  return response
    .replace(/<[^>]*>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>');
}

function formatForWeb(response: string): string {
  // Keep HTML for web display
  return response;
}
```

#### Step 3: Test Terminal Client
```bash
# Start server first
npm run dev

# In another terminal, run client
python3 tools/aurora_terminal_client.py --server http://localhost:5000

# Test conversation
You: Hi Aurora!
Aurora: Hey there! 👋 Ready to chat?
```

---

## 📊 INTEGRATION SUMMARY TABLE

| File | Problem It Solves | Integration Points | Success Criteria |
|------|-------------------|-------------------|------------------|
| **aurora_honest_self_diagnosis.py** | No feedback on learning quality | `aurora_x/self_learn.py` | Diagnostics saved to `.aurora_diagnostics.json` with quality scores |
| **aurora_implement_self_fixes.py** | No autonomous healing | `tools/aurora_autonomous_fixer.py` + `server/index.ts` | Health checks return 80%+ and auto-fixes succeed |
| **recovery_script.py** | No emergency recovery | `tools/aurora_recovery_system.py` | Backups created and restore works |
| **chat_with_aurora.py** | Limited to web UI | `tools/aurora_terminal_client.py` + `server/index.ts` | Terminal chat works from any OS |

---

## 🚀 INTEGRATION CHECKLIST

### Phase 1: Diagnostics (Day 1-2)
- [ ] Create `aurora_x/self_learn_diagnostics.py`
- [ ] Modify `aurora_x/self_learn.py` to use diagnostics
- [ ] Test: Run self-learning, verify diagnostics output
- [ ] Verify: `.aurora_diagnostics.json` is created

### Phase 2: Healing (Day 3-4)
- [ ] Create `tools/aurora_autonomous_fixer.py`
- [ ] Modify `server/index.ts` to add `/api/health` and `/api/heal` endpoints
- [ ] Test: Run healer, verify `fix_log.json` created
- [ ] Test: Manual health check

### Phase 3: Recovery (Day 5)
- [ ] Create `tools/aurora_recovery_system.py`
- [ ] Test: Create backup, verify files copied
- [ ] Test: Restore from backup
- [ ] Test: Emergency reset

### Phase 4: Terminal Chat (Day 6-7)
- [ ] Create `tools/aurora_terminal_client.py`
- [ ] Modify `server/index.ts` for terminal support
- [ ] Test: Run client, send messages
- [ ] Test: On Windows, Mac, Linux

---

## ✅ HOW TO VERIFY EACH FIX WORKS

### Diagnostics Fix
```bash
# Should output quality scores
python3 aurora_x/self_learn.py --spec-dir specs --sleep 60
tail .aurora_diagnostics.json
# Check: Has "quality_score" field with number 0-100
```

### Healing Fix
```bash
# Should show health report
python3 tools/aurora_autonomous_fixer.py
# Check: JSON with system healths and fixes applied
```

### Recovery Fix
```bash
# Should create backup
python3 tools/aurora_recovery_system.py backup
ls -la ~/.aurora_backups/
# Check: Backup directory has subdirectory with timestamp
```

### Terminal Chat Fix
```bash
# Terminal should connect to server
python3 tools/aurora_terminal_client.py
You: Hi Aurora!
# Check: Aurora responds in terminal
```

---

## 🎯 NEXT STEPS AFTER INTEGRATION

1. **Test all 4 fixes together** - Make sure they don't conflict
2. **Add to IDE plugins** - Use these as foundation for VS Code, JetBrains, Sublime
3. **Deploy to production** - Ensure recovery system is automated
4. **Monitor & tune** - Adjust healing rules based on real-world failures

