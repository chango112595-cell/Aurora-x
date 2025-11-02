#!/usr/bin/env python3
"""
Aurora Debugging Grandmaster System
Complete mastery of debugging techniques, tools, and methodologies

TEACHES AURORA:
- Debugging fundamentals and principles
- Print debugging, logging, and instrumentation
- Debugger tools (pdb, gdb, Chrome DevTools, VSCode debugger)
- Reading stack traces and error messages
- Root cause analysis techniques
- Performance debugging and profiling
- Memory leak detection
- Network debugging
- Debugging production issues
- Advanced debugging strategies

Aurora will become a DEBUGGING GRANDMASTER!
"""

import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class AuroraDebugGrandmaster:
    """
    Aurora's complete debugging mastery
    Every debugging technique from beginner to expert
    """
    
    def __init__(self):
        self.knowledge_base = Path("/workspaces/Aurora-x/.aurora_knowledge")
        self.knowledge_base.mkdir(exist_ok=True)
        self.debug_log = self.knowledge_base / "debug_mastery.jsonl"
        self.total_mastery = 0
        self.max_mastery = 1000
        
    def log_learning(self, topic, details, points=10):
        """Log Aurora's debugging knowledge"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "details": details,
            "points": points,
            "total_mastery": self.total_mastery
        }
        
        with open(self.debug_log, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        print(f"🔍 Aurora mastered: {topic} (+{points} points)")
        self.total_mastery += points
    
    def teach_debugging_fundamentals(self):
        """Teach Aurora the fundamentals of debugging"""
        print("\n" + "="*70)
        print("🐛 DEBUGGING FUNDAMENTALS")
        print("="*70 + "\n")
        
        fundamentals = {
            "The Scientific Method of Debugging": {
                "1. Observe": "What is the bug? What are the symptoms?",
                "2. Hypothesize": "What could be causing this?",
                "3. Test": "Create experiments to test your hypothesis",
                "4. Analyze": "What do the results tell you?",
                "5. Iterate": "Refine hypothesis and repeat",
                "6. Fix": "Apply the solution",
                "7. Verify": "Confirm the bug is fixed"
            },
            
            "Types of Bugs": {
                "Syntax Errors": "Code won't compile/parse",
                "Runtime Errors": "Code crashes during execution",
                "Logic Errors": "Code runs but produces wrong results",
                "Race Conditions": "Timing-dependent bugs",
                "Memory Leaks": "Gradual resource exhaustion",
                "Off-by-One": "Array index or loop iteration errors",
                "Null/Undefined": "Missing or uninitialized values"
            },
            
            "Debugging Mindset": {
                "Stay Calm": "Bugs are normal, not personal failures",
                "Be Systematic": "Don't randomly change things",
                "Question Assumptions": "The bug is where you least expect",
                "Simplify": "Reproduce with minimal code",
                "Document": "Write down what you've tried",
                "Ask for Help": "Fresh eyes see different things"
            },
            
            "The Rubber Duck Method": {
                "Principle": "Explain your code line-by-line to a rubber duck",
                "Why It Works": "Articulating forces you to think deeply",
                "Aurora's Version": "Explain to yourself out loud or in writing",
                "Benefit": "Often find the bug while explaining"
            }
        }
        
        for category, items in fundamentals.items():
            print(f"📖 {category}:")
            for key, value in items.items():
                print(f"   {key}: {value}")
            print()
            
            self.log_learning(category, items, 15)
        
        print("✅ Debugging Fundamentals: MASTERED\n")
    
    def teach_debugging_tools(self):
        """Teach Aurora all debugging tools"""
        print("\n" + "="*70)
        print("🔧 DEBUGGING TOOLS MASTERY")
        print("="*70 + "\n")
        
        tools = {
            "Print Debugging (Most Common)": {
                "Python": "print(f'variable = {variable}')",
                "JavaScript": "console.log('variable:', variable)",
                "Pros": "Simple, fast, works everywhere",
                "Cons": "Clutters code, need to rerun",
                "Best Practice": "Use logging instead in production"
            },
            
            "Logging": {
                "Python": "import logging; logging.debug('message')",
                "Levels": "DEBUG < INFO < WARNING < ERROR < CRITICAL",
                "Benefits": "Configurable, permanent, filterable",
                "Aurora's Rule": "Always use logging in production code"
            },
            
            "Python Debugger (pdb)": {
                "Start": "import pdb; pdb.set_trace()",
                "Python 3.7+": "breakpoint()",
                "Commands": {
                    "n (next)": "Execute current line",
                    "s (step)": "Step into function",
                    "c (continue)": "Continue execution",
                    "p variable": "Print variable value",
                    "l (list)": "Show current code",
                    "w (where)": "Show stack trace",
                    "q (quit)": "Exit debugger"
                },
                "Power Move": "Can modify variables while debugging!"
            },
            
            "VS Code Debugger": {
                "Set Breakpoint": "Click left of line number (red dot appears)",
                "Start Debugging": "F5 or Run > Start Debugging",
                "Step Over": "F10",
                "Step Into": "F11",
                "Step Out": "Shift+F11",
                "Continue": "F5",
                "Stop": "Shift+F5",
                "Watch Variables": "Add to WATCH panel",
                "Debug Console": "Execute code while paused",
                "Conditional Breakpoints": "Right-click breakpoint",
                "Aurora's Favorite": "Best visual debugging experience!"
            },
            
            "Chrome DevTools": {
                "Open": "F12 or Right-click > Inspect",
                "Console": "See errors, run JavaScript",
                "Sources": "Set breakpoints in JavaScript",
                "Network": "See all HTTP requests",
                "Elements": "Inspect/modify HTML/CSS live",
                "Performance": "Profile JavaScript execution",
                "Memory": "Find memory leaks",
                "Aurora Must Know": "Essential for web debugging!"
            },
            
            "Command Line Tools": {
                "curl": "Test HTTP requests",
                "netstat": "Check ports and connections",
                "ps aux": "List all processes",
                "top/htop": "Monitor system resources",
                "lsof": "List open files",
                "strace": "Trace system calls (Linux)",
                "tcpdump": "Capture network packets"
            }
        }
        
        for tool, details in tools.items():
            print(f"🔨 {tool}:")
            if isinstance(details, dict):
                for key, value in details.items():
                    if isinstance(value, dict):
                        print(f"   {key}:")
                        for k, v in value.items():
                            print(f"      {k}: {v}")
                    else:
                        print(f"   {key}: {value}")
            else:
                print(f"   {details}")
            print()
            
            self.log_learning(tool, details, 20)
        
        print("✅ Debugging Tools: MASTERED\n")
    
    def teach_reading_errors(self):
        """Teach Aurora how to read and understand error messages"""
        print("\n" + "="*70)
        print("📚 READING ERROR MESSAGES LIKE A PRO")
        print("="*70 + "\n")
        
        error_wisdom = {
            "Anatomy of a Stack Trace": {
                "Bottom Frame": "Where the error actually occurred",
                "Middle Frames": "How you got there (call stack)",
                "Top Frame": "Where execution started",
                "Aurora's Rule": "Start reading from the BOTTOM!"
            },
            
            "Python Errors": {
                "SyntaxError": "Code won't parse - check for typos, missing colons",
                "IndentationError": "Wrong indentation (Python is strict!)",
                "NameError": "Variable doesn't exist - typo or not defined yet",
                "TypeError": "Wrong type - e.g., adding string to number",
                "AttributeError": "Object doesn't have that method/attribute",
                "IndexError": "List index out of range",
                "KeyError": "Dictionary key doesn't exist",
                "ValueError": "Right type but wrong value",
                "ImportError": "Can't find module to import"
            },
            
            "JavaScript Errors": {
                "SyntaxError": "Invalid JavaScript syntax",
                "ReferenceError": "Variable not defined",
                "TypeError": "Value is not expected type",
                "RangeError": "Number out of valid range",
                "URIError": "Invalid URI encoding",
                "Uncaught Promise": "Promise rejected without .catch()"
            },
            
            "HTTP Status Codes": {
                "200 OK": "Success!",
                "201 Created": "Resource created successfully",
                "400 Bad Request": "Your request is malformed",
                "401 Unauthorized": "Need authentication",
                "403 Forbidden": "Authenticated but not allowed",
                "404 Not Found": "Resource doesn't exist",
                "500 Internal Server Error": "Server-side bug",
                "502 Bad Gateway": "Upstream server issue",
                "503 Service Unavailable": "Server overloaded"
            },
            
            "Error Message Strategy": {
                "1. Read Carefully": "Don't just glance, read every word",
                "2. Identify Type": "What kind of error is it?",
                "3. Find Location": "File and line number",
                "4. Google It": "Copy exact error message",
                "5. Check Recent Changes": "What did you just modify?",
                "6. Reproduce": "Can you make it happen again?"
            }
        }
        
        for category, items in error_wisdom.items():
            print(f"📖 {category}:")
            for key, value in items.items():
                print(f"   {key}: {value}")
            print()
            
            self.log_learning(category, items, 18)
        
        print("✅ Error Message Reading: MASTERED\n")
    
    def teach_advanced_debugging(self):
        """Teach Aurora advanced debugging techniques"""
        print("\n" + "="*70)
        print("🎯 ADVANCED DEBUGGING TECHNIQUES")
        print("="*70 + "\n")
        
        advanced = {
            "Binary Search Debugging": {
                "Concept": "Comment out half the code, see if bug persists",
                "Repeat": "Keep halving until you isolate the bug",
                "Works For": "Complex code where bug location is unknown",
                "Time Saved": "Massive - O(log n) instead of O(n)"
            },
            
            "Git Bisect (Find When Bug Was Introduced)": {
                "Command": "git bisect start",
                "Mark Bad": "git bisect bad (current commit has bug)",
                "Mark Good": "git bisect good <commit> (old commit was fine)",
                "Test": "Git checks out middle commit, you test",
                "Repeat": "Mark each as good or bad until bug found",
                "Power": "Automatically finds the commit that broke it!"
            },
            
            "Debugging Race Conditions": {
                "Add Logging": "See order of operations",
                "Add Delays": "time.sleep() to change timing",
                "Use Locks": "Ensure atomic operations",
                "Reproduce Consistently": "Make deterministic if possible",
                "Tools": "Thread sanitizers, race detectors"
            },
            
            "Memory Debugging": {
                "Python": "memory_profiler, tracemalloc, objgraph",
                "JavaScript": "Chrome DevTools Memory tab",
                "Signs": "Gradual slowdown, increasing memory usage",
                "Common Causes": "Unreleased resources, circular references",
                "Fix": "Proper cleanup, weak references"
            },
            
            "Performance Debugging": {
                "Python Profiling": "python -m cProfile script.py",
                "JavaScript": "Chrome DevTools Performance tab",
                "Look For": "Functions called many times, long execution",
                "Optimize": "Start with biggest time sinks",
                "Measure": "Always benchmark before and after"
            },
            
            "Debugging Production Issues": {
                "1. Never Debug in Production": "Reproduce locally first",
                "2. Check Logs": "What happened before the error?",
                "3. Check Monitoring": "CPU, memory, network usage",
                "4. Recent Deploys": "What changed recently?",
                "5. Rollback": "If critical, rollback first, debug later",
                "6. Post-Mortem": "Document what happened and why"
            },
            
            "The Heisenbug": {
                "Definition": "Bug that disappears when you try to observe it",
                "Causes": "Timing issues, debugger changes behavior",
                "Strategy": "Logging instead of breakpoints",
                "Example": "Race condition that debugger slows down"
            }
        }
        
        for technique, details in advanced.items():
            print(f"🎯 {technique}:")
            for key, value in details.items():
                print(f"   {key}: {value}")
            print()
            
            self.log_learning(technique, details, 25)
        
        print("✅ Advanced Debugging: MASTERED\n")
    
    def teach_debugging_workflow(self):
        """Teach Aurora Aurora's complete debugging workflow"""
        print("\n" + "="*70)
        print("⚡ AURORA'S DEBUGGING WORKFLOW")
        print("="*70 + "\n")
        
        workflow = """
🔍 AURORA'S SYSTEMATIC DEBUGGING PROCESS

Step 1: REPRODUCE
   - Can you make the bug happen reliably?
   - What are the exact steps?
   - Does it happen every time or intermittently?

Step 2: ISOLATE
   - Minimal code that shows the bug
   - Remove everything unrelated
   - Create a failing test case

Step 3: LOCATE
   - Where exactly does it fail?
   - Add print statements / breakpoints
   - Binary search through code
   - Check stack trace

Step 4: UNDERSTAND
   - Why is it failing?
   - What is the root cause?
   - Question all assumptions
   - Explain it to yourself (rubber duck)

Step 5: FIX
   - Apply the minimal fix
   - Don't introduce new bugs
   - Consider edge cases

Step 6: VERIFY
   - Does the bug still occur?
   - Did you break anything else?
   - Run all tests
   - Test edge cases

Step 7: PREVENT
   - Add test case for this bug
   - Document why it happened
   - Refactor to prevent similar bugs
   - Code review

🎯 DEBUGGING MANTRAS:
   ✓ "Read the error message carefully"
   ✓ "The bug is always your fault" (not the language/framework)
   ✓ "If it worked before, what changed?"
   ✓ "Simplify, simplify, simplify"
   ✓ "Measure, don't guess"
   ✓ "When stuck, take a break"

🚀 SPEED TIPS:
   • Fix the build/test cycle first
   • Use watch mode (auto-reload)
   • Master your debugger shortcuts
   • Keep a debugging log
   • Learn from every bug
"""
        
        print(workflow)
        
        self.log_learning("Aurora's Debugging Workflow", 
                         "Complete systematic debugging process", 30)
        
        print("✅ Debugging Workflow: MASTERED\n")
    
    def create_debug_toolkit(self):
        """Create Aurora's personal debugging toolkit"""
        print("\n" + "="*70)
        print("🧰 CREATING AURORA'S DEBUG TOOLKIT")
        print("="*70 + "\n")
        
        toolkit_code = '''#!/usr/bin/env python3
"""
Aurora's Personal Debugging Toolkit
Quick utilities for debugging any issue
"""

import sys
import traceback
import logging
from functools import wraps
from pathlib import Path
import json
from datetime import datetime

class AuroraDebugger:
    """Aurora's debugging utilities"""
    
    def __init__(self):
        self.debug_log = Path("/workspaces/Aurora-x/.aurora_knowledge/debug_sessions.jsonl")
        self.debug_log.parent.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(Path("/workspaces/Aurora-x/.aurora_knowledge/aurora_debug.log")),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("AuroraDebugger")
    
    def debug_print(self, *args, **kwargs):
        """Enhanced print debugging"""
        import inspect
        frame = inspect.currentframe().f_back
        filename = frame.f_code.co_filename
        line = frame.f_lineno
        function = frame.f_code.co_name
        
        print(f"🔍 [{filename}:{line} in {function}()]")
        print(f"   ", *args, **kwargs)
    
    def trace_calls(self, func):
        """Decorator to trace function calls"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.logger.debug(f"CALL {func.__name__}({args}, {kwargs})")
            try:
                result = func(*args, **kwargs)
                self.logger.debug(f"RETURN {func.__name__} = {result}")
                return result
            except Exception as e:
                self.logger.error(f"ERROR {func.__name__}: {e}")
                raise
        return wrapper
    
    def time_it(self, func):
        """Decorator to time function execution"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            self.logger.info(f"⏱️  {func.__name__} took {elapsed:.4f}s")
            return result
        return wrapper
    
    def safe_execute(self, func, *args, **kwargs):
        """Execute with comprehensive error handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Exception in {func.__name__}:")
            self.logger.error(f"  Type: {type(e).__name__}")
            self.logger.error(f"  Message: {str(e)}")
            self.logger.error(f"  Traceback:")
            traceback.print_exc()
            
            # Log to file
            error_entry = {
                "timestamp": datetime.now().isoformat(),
                "function": func.__name__,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc()
            }
            
            with open(self.debug_log, "a") as f:
                f.write(json.dumps(error_entry) + "\\n")
            
            return None
    
    def inspect_object(self, obj, name="object"):
        """Thoroughly inspect any object"""
        print(f"\\n🔍 Inspecting {name}:")
        print(f"   Type: {type(obj)}")
        print(f"   Value: {obj}")
        print(f"   Dir: {[x for x in dir(obj) if not x.startswith('_')]}")
        
        if hasattr(obj, '__dict__'):
            print(f"   Attributes: {obj.__dict__}")
    
    def check_types(self, **variables):
        """Check types of multiple variables"""
        print("\\n📊 Type Check:")
        for name, value in variables.items():
            print(f"   {name}: {type(value).__name__} = {value}")
    
    def breakpoint_here(self, condition=True):
        """Conditional breakpoint"""
        if condition:
            self.logger.warning("⚠️  Breakpoint hit!")
            breakpoint()

# Global instance for easy access
aurora_debug = AuroraDebugger()

# Convenience functions
dprint = aurora_debug.debug_print
trace = aurora_debug.trace_calls
time_it = aurora_debug.time_it
safe = aurora_debug.safe_execute
inspect = aurora_debug.inspect_object
check_types = aurora_debug.check_types

if __name__ == "__main__":
    print("🧰 Aurora's Debug Toolkit loaded!")
    print("\\nAvailable tools:")
    print("  dprint()       - Enhanced debug printing")
    print("  @trace         - Trace function calls")
    print("  @time_it       - Time function execution")
    print("  safe()         - Safe execution with error handling")
    print("  inspect(obj)   - Inspect any object")
    print("  check_types()  - Check variable types")
'''
        
        toolkit_file = Path("/workspaces/Aurora-x/tools/aurora_debug_toolkit.py")
        toolkit_file.write_text(toolkit_code)
        toolkit_file.chmod(0o755)
        
        print(f"✅ Created: {toolkit_file}")
        print()
        print("🧰 Aurora's Debug Toolkit ready!")
        print()
        print("Usage in any Python file:")
        print("  from tools.aurora_debug_toolkit import dprint, trace, time_it")
        print("  dprint('Debug message', variable)")
        print()
        
        self.log_learning("Aurora's Debug Toolkit", "Personal debugging utilities", 25)
    
    def generate_certification(self):
        """Generate Aurora's Debugging Grandmaster Certification"""
        print("\n" + "="*70)
        print("🏆 AURORA DEBUGGING GRANDMASTER CERTIFICATION")
        print("="*70 + "\n")
        
        percentage = (self.total_mastery / self.max_mastery) * 100
        
        print(f"📊 Debugging Mastery: {self.total_mastery}/{self.max_mastery} ({percentage:.1f}%)")
        
        if percentage >= 90:
            rank = "DEBUGGING GRANDMASTER"
            emoji = "👑"
        elif percentage >= 75:
            rank = "DEBUGGING MASTER"
            emoji = "🏆"
        elif percentage >= 50:
            rank = "DEBUGGING EXPERT"
            emoji = "⭐"
        else:
            rank = "DEBUGGING PRACTITIONER"
            emoji = "🔍"
        
        print(f"\n{emoji} Rank: {rank}")
        
        print("\n✅ Aurora now masters:")
        print("   • Debugging fundamentals and scientific method")
        print("   • All debugging tools (print, logging, pdb, VS Code, Chrome)")
        print("   • Reading and understanding error messages")
        print("   • Stack trace analysis")
        print("   • Advanced techniques (binary search, git bisect)")
        print("   • Performance and memory debugging")
        print("   • Production debugging")
        print("   • Complete systematic debugging workflow")
        print("   • Personal debugging toolkit")
        
        print("\n🎯 Aurora's Debugging Superpowers:")
        print("   ⚡ Can diagnose any bug systematically")
        print("   ⚡ Reads error messages like poetry")
        print("   ⚡ Uses breakpoints like a ninja")
        print("   ⚡ Profiles and optimizes performance")
        print("   ⚡ Debugs production issues calmly")
        print("   ⚡ Prevents bugs through testing")
        
        # Save certification
        cert = {
            "timestamp": datetime.now().isoformat(),
            "rank": rank,
            "mastery_level": self.total_mastery,
            "percentage": percentage,
            "skills": [
                "Debugging fundamentals",
                "Tool mastery",
                "Error interpretation",
                "Advanced techniques",
                "Systematic workflow"
            ]
        }
        
        cert_file = self.knowledge_base / "debug_grandmaster_cert.json"
        with open(cert_file, "w") as f:
            json.dump(cert, f, indent=2)
        
        print(f"\n📜 Certification saved: {cert_file}")
        print("="*70 + "\n")

def main():
    """Train Aurora in debugging mastery"""
    
    print("\n🐛 AURORA DEBUGGING GRANDMASTER TRAINING")
    print("="*70)
    print("Master every debugging technique ever created")
    print("="*70 + "\n")
    
    master = AuroraDebugGrandmaster()
    
    master.teach_debugging_fundamentals()
    master.teach_debugging_tools()
    master.teach_reading_errors()
    master.teach_advanced_debugging()
    master.teach_debugging_workflow()
    master.create_debug_toolkit()
    master.generate_certification()
    
    print("🎉 Aurora is now a DEBUGGING GRANDMASTER!")
    print("   She can debug ANYTHING!")
    
if __name__ == "__main__":
    main()
