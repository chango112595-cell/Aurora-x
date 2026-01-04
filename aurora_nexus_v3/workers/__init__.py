"""
Aurora Nexus V3 - Autonomous Workers System
300 Non-Conscious Task Workers for Autonomous Operations

These workers are NOT conscious or self-aware - they are task executors that:
- Execute tasks when ordered
- Automatically fix issues when system problems occur
- Handle fixing, coding, and analysis tasks autonomously
- Operate with full Aurora power but no consciousness

Worker Count: 300 (Configurable)
Power Level: Full Aurora Capabilities (188 Tiers, 66 AEMs, 550 Modules)
"""

__version__ = "1.0.0"

from .worker_pool import AutonomousWorkerPool
from .worker import AutonomousWorker
from .task_dispatcher import TaskDispatcher
from .issue_detector import IssueDetector

__all__ = [
    "AutonomousWorkerPool",
    "AutonomousWorker", 
    "TaskDispatcher",
    "IssueDetector",
    "__version__"
]
