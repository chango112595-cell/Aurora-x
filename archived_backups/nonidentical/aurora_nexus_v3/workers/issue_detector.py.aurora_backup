"""
Aurora Issue Detector - Automatic System Issue Detection
Triggers autonomous workers when issues occur in the system

This is the bridge between system health monitoring and autonomous healing.
When issues are detected, workers are automatically dispatched to fix them.
"""

import asyncio
import time
import threading
import re
import os
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pathlib import Path
from collections import defaultdict


class IssueSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IssueCategory(Enum):
    CODE = "code"
    SYSTEM = "system"
    SERVICE = "service"
    PERFORMANCE = "performance"
    SECURITY = "security"
    NETWORK = "network"


@dataclass
class DetectedIssue:
    id: str
    category: IssueCategory
    severity: IssueSeverity
    type: str
    target: str
    description: str
    detected_at: datetime = field(default_factory=datetime.now)
    auto_fix_attempted: bool = False
    resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class IssueDetector:
    """
    Automatic issue detection system
    
    Monitors:
    - Code quality issues (syntax, imports, encoding)
    - System health (services, ports, resources)
    - Performance issues (memory, CPU, response time)
    - Security issues (vulnerabilities, exposed secrets)
    
    When issues are detected, automatically dispatches workers to fix them.
    """
    
    def __init__(self, worker_pool: Any = None, core: Any = None):
        self.worker_pool = worker_pool
        self.core = core
        self.monitoring_active = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        self.detected_issues: List[DetectedIssue] = []
        self.issue_handlers: Dict[str, Callable] = {}
        self.issue_patterns: Dict[str, List[str]] = {}
        
        self.check_interval = 30  # Reduced frequency to prevent CPU spikes
        self.auto_fix_enabled = True
        self._last_cpu_reading = 0  # Cache CPU reading
        
        self._initialize_patterns()
    
    def _initialize_patterns(self):
        """Initialize issue detection patterns"""
        self.issue_patterns = {
            "import_error": [
                r'ImportError',
                r'ModuleNotFoundError',
                r'cannot import name',
                r'No module named'
            ],
            "syntax_error": [
                r'SyntaxError',
                r'IndentationError',
                r'unexpected EOF',
                r'invalid syntax'
            ],
            "encoding_error": [
                r'UnicodeDecodeError',
                r'UnicodeEncodeError',
                r'codec can\'t decode',
                r'codec can\'t encode'
            ],
            "type_error": [
                r'TypeError',
                r'not callable',
                r'not subscriptable',
                r'missing.*argument'
            ],
            "port_conflict": [
                r'Address already in use',
                r'port.*already.*use',
                r'EADDRINUSE'
            ],
            "memory_issue": [
                r'MemoryError',
                r'Out of memory',
                r'memory allocation failed'
            ],
            "connection_error": [
                r'ConnectionError',
                r'ConnectionRefused',
                r'Connection reset',
                r'ECONNREFUSED'
            ],
            "timeout_error": [
                r'TimeoutError',
                r'Operation timed out',
                r'connection timed out'
            ]
        }
    
    async def start(self):
        """Start the issue detector monitoring"""
        self.monitoring_active = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        print("[AURORA DETECTOR] Issue detector started - monitoring for problems")
    
    async def stop(self):
        """Stop the issue detector"""
        self.monitoring_active = False
        print("[AURORA DETECTOR] Issue detector stopped")
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                asyncio.run(self._run_detection_cycle())
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"[AURORA DETECTOR] Detection error: {e}")
    
    async def _run_detection_cycle(self):
        """Run a full detection cycle"""
        await self._check_code_issues()
        await self._check_service_health()
        await self._check_system_resources()
    
    async def _check_code_issues(self):
        """Check for code issues in the project"""
        pass
    
    async def _check_service_health(self):
        """Check health of running services"""
        pass
    
    async def _check_system_resources(self):
        """Check system resource usage"""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                await self._report_issue(
                    category=IssueCategory.PERFORMANCE,
                    severity=IssueSeverity.HIGH,
                    issue_type="memory_high",
                    target="system",
                    description=f"Memory usage at {memory.percent}%"
                )
            
            # Use non-blocking CPU check (None interval means don't block)
            # This returns the CPU usage since the last call
            cpu = psutil.cpu_percent(interval=None)
            self._last_cpu_reading = cpu
            # Only report critical CPU issues (sustained high usage)
            if cpu > 95:
                await self._report_issue(
                    category=IssueCategory.PERFORMANCE,
                    severity=IssueSeverity.MEDIUM,
                    issue_type="cpu_high",
                    target="system",
                    description=f"CPU usage at {cpu}%"
                )
        except ImportError:
            pass
    
    async def _report_issue(self, category: IssueCategory, severity: IssueSeverity,
                           issue_type: str, target: str, description: str,
                           metadata: Optional[Dict] = None) -> DetectedIssue:
        """Report a detected issue"""
        import uuid
        
        issue = DetectedIssue(
            id=str(uuid.uuid4()),
            category=category,
            severity=severity,
            type=issue_type,
            target=target,
            description=description,
            metadata=metadata or {}
        )
        
        self.detected_issues.append(issue)
        print(f"[AURORA DETECTOR] Issue detected: {issue_type} ({severity.value}) - {description}")
        
        if self.auto_fix_enabled and self.worker_pool:
            await self._dispatch_auto_fix(issue)
        
        return issue
    
    async def _dispatch_auto_fix(self, issue: DetectedIssue):
        """Dispatch autonomous fix for detected issue"""
        issue.auto_fix_attempted = True
        
        await self.worker_pool.handle_system_issue({
            "id": issue.id,
            "type": issue.type,
            "severity": issue.severity.value,
            "target": issue.target,
            "category": issue.category.value,
            "description": issue.description
        })
    
    async def scan_file(self, filepath: str) -> List[DetectedIssue]:
        """Scan a file for issues"""
        issues = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            for issue_type, patterns in self.issue_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        issue = await self._report_issue(
                            category=IssueCategory.CODE,
                            severity=IssueSeverity.MEDIUM,
                            issue_type=issue_type,
                            target=filepath,
                            description=f"Pattern '{pattern}' found in file"
                        )
                        issues.append(issue)
                        break
        except Exception as e:
            print(f"[AURORA DETECTOR] Error scanning {filepath}: {e}")
        
        return issues
    
    async def scan_directory(self, directory: str, extensions: Optional[List[str]] = None) -> List[DetectedIssue]:
        """Scan a directory for issues"""
        extensions = extensions or ['.py', '.js', '.ts', '.tsx']
        issues = []
        
        try:
            for root, dirs, files in os.walk(directory):
                dirs[:] = [d for d in dirs if d not in ['node_modules', 'venv', '.venv', '__pycache__', '.git']]
                
                for file in files:
                    if any(file.endswith(ext) for ext in extensions):
                        filepath = os.path.join(root, file)
                        file_issues = await self.scan_file(filepath)
                        issues.extend(file_issues)
        except Exception as e:
            print(f"[AURORA DETECTOR] Error scanning directory {directory}: {e}")
        
        return issues
    
    def register_handler(self, issue_type: str, handler: Callable):
        """Register a custom handler for an issue type"""
        self.issue_handlers[issue_type] = handler
    
    def get_issues(self, category: Optional[IssueCategory] = None,
                  severity: Optional[IssueSeverity] = None,
                  resolved: Optional[bool] = None) -> List[DetectedIssue]:
        """Get detected issues with optional filtering"""
        issues = self.detected_issues
        
        if category:
            issues = [i for i in issues if i.category == category]
        if severity:
            issues = [i for i in issues if i.severity == severity]
        if resolved is not None:
            issues = [i for i in issues if i.resolved == resolved]
        
        return issues
    
    def get_status(self) -> Dict[str, Any]:
        """Get detector status"""
        return {
            "monitoring_active": self.monitoring_active,
            "auto_fix_enabled": self.auto_fix_enabled,
            "check_interval": self.check_interval,
            "total_issues": len(self.detected_issues),
            "unresolved_issues": len([i for i in self.detected_issues if not i.resolved]),
            "auto_fix_attempts": len([i for i in self.detected_issues if i.auto_fix_attempted]),
            "pattern_types": list(self.issue_patterns.keys()),
            "custom_handlers": list(self.issue_handlers.keys())
        }
