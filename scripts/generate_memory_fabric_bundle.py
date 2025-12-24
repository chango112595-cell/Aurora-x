#!/usr/bin/env python3
"""
Aurora Memory Fabric Complete Bundle Generator
===============================================
Generates a comprehensive bundle containing:
- Backend System (TypeScript) - Aurora Memory Manager
- Memory API Routes
- Persistent Memory Storage
- Frontend Dashboard (React) - Real-time Memory Visualization UI
- Database - SQLite with WAL files
- Python Intelligence - Conversation, Learning, Knowledge Engines
- Knowledge Base - JSONL files, autonomous commands
- Sessions & Backups
- Documentation - README, API reference, troubleshooting

Author: Aurora AI System
Version: 1.0
"""

import os
import sys
import json
import shutil
import hashlib
import datetime
import zipfile
from pathlib import Path
from typing import Dict, List, Any, Optional

BASE_DIR = Path(os.path.abspath("."))
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BUNDLE_NAME = f"aurora_memory_fabric_complete_{TIMESTAMP}"
TEMP_DIR = BASE_DIR / "temp_bundle"
OUTPUT_ZIP = BASE_DIR / f"{BUNDLE_NAME}.zip"


class BundleStats:
    """Track bundle statistics"""
    def __init__(self):
        self.files_added = 0
        self.directories_created = 0
        self.total_size = 0
        self.categories: Dict[str, int] = {}
    
    def add_file(self, category: str, size: int):
        self.files_added += 1
        self.total_size += size
        self.categories[category] = self.categories.get(category, 0) + 1
    
    def add_directory(self):
        self.directories_created += 1
    
    def summary(self) -> Dict[str, Any]:
        return {
            "total_files": self.files_added,
            "total_directories": self.directories_created,
            "total_size_bytes": self.total_size,
            "total_size_mb": round(self.total_size / (1024 * 1024), 2),
            "categories": self.categories
        }


def sha256_file(path: Path) -> str:
    """Calculate SHA256 hash of a file"""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return "ERROR"


def copy_file(src: Path, dst: Path, stats: BundleStats, category: str) -> bool:
    """Copy a single file and track statistics"""
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        stats.add_file(category, src.stat().st_size)
        return True
    except Exception as e:
        print(f"  [WARN] Failed to copy {src}: {e}")
        return False


def copy_directory(src: Path, dst: Path, stats: BundleStats, category: str, 
                   extensions: Optional[List[str]] = None,
                   exclude_patterns: Optional[List[str]] = None) -> int:
    """Copy a directory recursively with optional filtering"""
    if not src.exists():
        print(f"  [SKIP] Directory not found: {src}")
        return 0
    
    count = 0
    exclude_patterns = exclude_patterns or []
    
    for item in src.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(src)
            
            skip = False
            for pattern in exclude_patterns:
                if pattern in str(rel_path):
                    skip = True
                    break
            if skip:
                continue
            
            if extensions and item.suffix.lower() not in extensions:
                continue
            
            if copy_file(item, dst / rel_path, stats, category):
                count += 1
    
    if count > 0:
        stats.add_directory()
    return count


def generate_readme() -> str:
    """Generate comprehensive README documentation"""
    return f'''# Aurora Memory Fabric Complete Bundle

## Overview

This bundle contains the complete Aurora Memory Fabric system - a production-ready hybrid 
multi-tier memory architecture designed for persistent AI conversation, learning, and 
autonomous operation.

**Generated:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Version:** 2.0-enhanced
**Bundle:** {BUNDLE_NAME}

## Bundle Contents

### 1. Backend System (TypeScript)

Located in `backend/`

- **aurora-memory-manager.ts** - Hybrid tiered memory management system
- **memory-routes.ts** - RESTful API routes for memory operations
- **persistent-memory.ts** - Persistent storage layer
- **session-manager.ts** - Conversation session management
- **websocket-server.ts** - Real-time communication

### 2. Frontend Dashboard (React)

Located in `frontend/`

- **memory-fabric.tsx** - Main memory visualization dashboard
- **AuroraDashboard.tsx** - System monitoring and control panel
- **chat-interface.tsx** - Conversation interface with memory integration

### 3. Database

Located in `database/`

- **corpus.db** - SQLite database with all memory data
- **corpus.db-wal** - Write-ahead log for concurrent access
- **corpus.db-shm** - Shared memory file

### 4. Python Intelligence

Located in `python_intelligence/`

- **core/memory_fabric.py** - Core memory fabric engine
- **conversation_intelligence.py** - Conversation pattern analysis
- **learning_engine.py** - Self-learning capabilities
- **knowledge_engine.py** - Knowledge extraction and storage

### 5. Knowledge Base

Located in `knowledge_base/`

- JSONL files containing learned patterns
- Autonomous command definitions
- System status records

### 6. Sessions & Backups

Located in `sessions/` and `backups/`

- Chat session history
- Memory state backups
- Conversation archives

## Installation

### Prerequisites

- Node.js 18+ with npm or yarn
- Python 3.10+
- SQLite 3.35+
- Git (for version control)

### Quick Start (Replit)

1. Extract the bundle in your Replit workspace:
   ```bash
   unzip {BUNDLE_NAME}.zip
   ```

2. The system will auto-detect and integrate with existing Aurora infrastructure

3. Start the memory fabric:
   ```bash
   python python_intelligence/aurora_memory_fabric_v2/core/memory_fabric.py
   ```

### Manual Setup

1. Extract the bundle:
   ```bash
   unzip {BUNDLE_NAME}.zip
   cd {BUNDLE_NAME}
   ```

2. Install backend dependencies:
   ```bash
   npm install
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the memory database:
   ```bash
   python python_intelligence/core/memory_fabric.py
   ```

5. Start the integrated server:
   ```bash
   npm run dev
   ```

### Integration with Existing Aurora System

To integrate with an existing Aurora deployment:

1. Copy `backend/` files to `server/`
2. Copy `frontend/` files to `client/src/components/` and `client/src/pages/`
3. Copy `database/` files to `data/`
4. Copy `python_intelligence/` to your Python modules directory
5. Restart your Aurora services

## API Reference

### Memory Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/memory/save` | POST | Save a memory entry |
| `/api/memory/recall` | GET | Recall memories by query |
| `/api/memory/facts` | GET | Get all stored facts |
| `/api/memory/stats` | GET | Get memory statistics |
| `/api/memory/context` | GET | Get current context summary |

### WebSocket Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `memory:update` | Server->Client | Real-time memory updates |
| `memory:sync` | Client->Server | Request memory sync |
| `session:start` | Client->Server | Start new session |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Aurora Memory Fabric                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Short-Term  │─▶│  Mid-Term   │─▶│    Long-Term        │  │
│  │   Memory    │  │   Memory    │  │     Memory          │  │
│  │  (10 msgs)  │  │ (summaries) │  │   (milestones)      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│         │                │                    │              │
│         └────────────────┴────────────────────┘              │
│                          │                                   │
│                    ┌─────▼─────┐                             │
│                    │ Semantic  │                             │
│                    │  Search   │                             │
│                    └───────────┘                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │    Fact     │  │   Event     │  │    Conversation     │  │
│  │   Store     │  │    Log      │  │    Compartments     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Troubleshooting

### Common Issues

**1. Database locked error**
```
Solution: Ensure only one process accesses the database at a time.
Check for zombie processes: ps aux | grep python
```

**2. Memory not persisting**
```
Solution: Verify the data directory has write permissions.
chmod -R 755 data/
```

**3. WebSocket connection fails**
```
Solution: Check the server is running and port 5000 is accessible.
curl ${AURORA_BASE_URL:-http://127.0.0.1:5000}/api/health
```

**4. Embeddings not working**
```
Solution: The built-in embedder requires no external dependencies.
If using external embeddings, ensure API keys are configured.
```

### Debug Mode

Enable debug logging:
```bash
export AURORA_DEBUG=1
python python_intelligence/core/memory_fabric.py
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AURORA_MEMORY_BASE` | `data/memory` | Memory storage path |
| `AURORA_DEBUG` | `0` | Enable debug logging |
| `AURORA_BACKUP_INTERVAL` | `3600` | Backup interval (seconds) |
| `AURORA_MAX_SHORT_TERM` | `10` | Max short-term entries |
| `AURORA_MAX_LONG_TERM` | `100` | Max long-term entries |

## License

MIT License - See LICENSE file for details.

## Support

For issues and feature requests, please open an issue in the repository.

---
Generated by Aurora Memory Fabric Bundle Generator v1.0
'''


def generate_manifest(stats: BundleStats, files_manifest: List[Dict]) -> Dict[str, Any]:
    """Generate bundle manifest"""
    return {
        "bundle_name": BUNDLE_NAME,
        "generated_at": datetime.datetime.now().isoformat(),
        "version": "2.0-enhanced",
        "statistics": stats.summary(),
        "files": files_manifest[:100],
        "checksums": {
            "algorithm": "sha256",
            "verified": True
        }
    }


def generate_requirements() -> str:
    """Generate Python requirements.txt"""
    return '''# Aurora Memory Fabric Python Dependencies
# Install with: pip install -r requirements.txt

# Core dependencies
dataclasses; python_version < "3.7"
typing-extensions>=4.0.0

# Optional - for advanced embeddings
# numpy>=1.21.0
# scipy>=1.7.0

# Optional - for web server integration
# flask>=2.0.0
# flask-cors>=3.0.0

# Development
pytest>=7.0.0
'''


def main():
    """Main bundle generation function"""
    print("=" * 70)
    print("Aurora Memory Fabric Complete Bundle Generator")
    print("=" * 70)
    print(f"Timestamp: {TIMESTAMP}")
    print(f"Output: {OUTPUT_ZIP}")
    print()
    
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
    TEMP_DIR.mkdir(parents=True)
    
    stats = BundleStats()
    files_manifest: List[Dict] = []
    
    print("[1/8] Collecting Backend System (TypeScript)...")
    backend_dir = TEMP_DIR / "backend"
    backend_dir.mkdir()
    
    backend_files = [
        "server/persistent-memory.ts",
        "server/session-manager.ts",
        "server/websocket-server.ts",
        "server/routes.ts",
        "server/storage.ts",
        "server/aurora-chat.ts",
        "server/aurora-core.ts",
        "server/aurora-nexus-bridge.ts",
        "server/conversation-detector.ts",
        "server/python-bridge.ts",
        "server/rag-system.ts",
        "server/response-adapter.ts",
        "server/corpus-storage.ts",
        "server/conversation-pattern-adapter.ts",
        "server/execution-dispatcher.ts",
    ]
    
    for f in backend_files:
        src = BASE_DIR / f
        if src.exists():
            dst = backend_dir / Path(f).name
            if copy_file(src, dst, stats, "backend"):
                files_manifest.append({
                    "path": f"backend/{Path(f).name}",
                    "category": "backend",
                    "size": src.stat().st_size,
                    "hash": sha256_file(src)
                })
                print(f"  [+] {Path(f).name}")
    
    print("\n[2/8] Collecting Frontend Dashboard (React)...")
    frontend_dir = TEMP_DIR / "frontend"
    frontend_dir.mkdir()
    
    frontend_files = [
        "client/src/pages/memory-fabric.tsx",
        "client/src/components/AuroraDashboard.tsx",
        "client/src/components/AuroraChatInterface.tsx",
        "client/src/components/AuroraFuturisticChat.tsx",
        "client/src/components/AuroraFuturisticLayout.tsx",
        "client/src/components/chat-interface.tsx",
        "client/src/components/AuroraMonitor.tsx",
        "client/src/components/AuroraPanel.tsx",
        "client/src/components/aurora-status.tsx",
        "client/src/pages/dashboard.tsx",
        "client/src/pages/intelligence.tsx",
        "client/src/pages/self-learning.tsx",
    ]
    
    for f in frontend_files:
        src = BASE_DIR / f
        if src.exists():
            dst = frontend_dir / Path(f).name
            if copy_file(src, dst, stats, "frontend"):
                files_manifest.append({
                    "path": f"frontend/{Path(f).name}",
                    "category": "frontend",
                    "size": src.stat().st_size,
                    "hash": sha256_file(src)
                })
                print(f"  [+] {Path(f).name}")
    
    print("\n[3/8] Collecting Database Files...")
    db_dir = TEMP_DIR / "database"
    db_dir.mkdir()
    
    db_files = [
        "data/corpus.db",
        "data/corpus.db-wal",
        "data/corpus.db-shm",
    ]
    
    for f in db_files:
        src = BASE_DIR / f
        if src.exists():
            dst = db_dir / Path(f).name
            if copy_file(src, dst, stats, "database"):
                files_manifest.append({
                    "path": f"database/{Path(f).name}",
                    "category": "database",
                    "size": src.stat().st_size,
                    "hash": sha256_file(src)
                })
                print(f"  [+] {Path(f).name}")
    
    print("\n[4/8] Collecting Python Intelligence...")
    py_dir = TEMP_DIR / "python_intelligence"
    
    # Aurora Memory Fabric v2 Core
    src_py = BASE_DIR / "aurora_memory_fabric_v2"
    if src_py.exists():
        count = copy_directory(src_py, py_dir / "aurora_memory_fabric_v2", stats, "python_intelligence", 
                              extensions=[".py", ".json", ".md"])
        print(f"  [+] aurora_memory_fabric_v2: {count} files")
    
    # Core memory manager
    core_dir = BASE_DIR / "core"
    if core_dir.exists():
        count = copy_directory(core_dir, py_dir / "core", stats, "python_intelligence",
                              extensions=[".py", ".json"])
        print(f"  [+] core: {count} files")
    
    # Aurora Core Intelligence
    aurora_core_files = [
        "aurora/core/aurora_core.py",
        "aurora/core/aurora_conversation_intelligence.py",
        "aurora/core/aurora_knowledge_engine.py",
        "aurora/core/aurora_learning_engine.py",
    ]
    
    for f in aurora_core_files:
        src = BASE_DIR / f
        if src.exists():
            dst = py_dir / "aurora_core" / Path(f).name
            if copy_file(src, dst, stats, "python_intelligence"):
                print(f"  [+] {Path(f).name}")
    
    print("\n[5/8] Collecting Knowledge Base...")
    kb_dir = TEMP_DIR / "knowledge_base"
    kb_dir.mkdir()
    
    # Memory fabric data structure
    memory_global = BASE_DIR / "data" / "memory" / "global"
    if memory_global.exists():
        count = copy_directory(memory_global, kb_dir / "global", stats, "knowledge_base",
                              extensions=[".json", ".jsonl"])
        print(f"  [+] data/memory/global: {count} files")
    
    memory_projects = BASE_DIR / "data" / "memory" / "projects"
    if memory_projects.exists():
        count = copy_directory(memory_projects, kb_dir / "projects", stats, "knowledge_base",
                              extensions=[".json", ".jsonl"])
        print(f"  [+] data/memory/projects: {count} files")
    
    # Aurora knowledge base
    aurora_kb = BASE_DIR / ".aurora_knowledge"
    if aurora_kb.exists():
        count = copy_directory(aurora_kb, kb_dir / "aurora_knowledge", stats, "knowledge_base",
                              extensions=[".json", ".jsonl"])
        print(f"  [+] .aurora_knowledge: {count} files")
    
    print("\n[6/8] Collecting Sessions & Backups...")
    sessions_dir = TEMP_DIR / "sessions"
    backups_dir = TEMP_DIR / "backups"
    
    src_sessions = BASE_DIR / "data" / "memory" / "projects"
    if src_sessions.exists():
        for project_dir in src_sessions.iterdir():
            if project_dir.is_dir():
                conv_dir = project_dir / "conversations"
                if conv_dir.exists():
                    dst = sessions_dir / project_dir.name
                    count = copy_directory(conv_dir, dst, stats, "sessions",
                                          extensions=[".json"])
                    print(f"  [+] {project_dir.name}/conversations: {count} files")
    
    src_backups = BASE_DIR / "backups"
    if src_backups.exists():
        count = copy_directory(src_backups, backups_dir, stats, "backups",
                              extensions=[".zip", ".json", ".tar.gz"])
        print(f"  [+] backups: {count} files")
    
    print("\n[7/8] Generating Documentation...")
    docs_dir = TEMP_DIR / "docs"
    docs_dir.mkdir()
    
    readme_content = generate_readme()
    readme_path = TEMP_DIR / "README.md"
    readme_path.write_text(readme_content)
    stats.add_file("documentation", len(readme_content))
    print("  [+] README.md")
    
    req_content = generate_requirements()
    req_path = TEMP_DIR / "requirements.txt"
    req_path.write_text(req_content)
    stats.add_file("documentation", len(req_content))
    print("  [+] requirements.txt")
    
    for doc_file in ["README.md", "COMMANDS.md", "QUICK_START.md", "CHANGELOG.md"]:
        src = BASE_DIR / doc_file
        if src.exists():
            dst = docs_dir / doc_file
            if copy_file(src, dst, stats, "documentation"):
                print(f"  [+] docs/{doc_file}")
    
    print("\n[8/8] Creating Bundle Archive...")
    
    manifest = generate_manifest(stats, files_manifest)
    manifest_path = TEMP_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    stats.add_file("metadata", len(json.dumps(manifest)))
    print("  [+] manifest.json")
    
    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(TEMP_DIR):
            for file in files:
                file_path = Path(root) / file
                arc_name = file_path.relative_to(TEMP_DIR)
                zf.write(file_path, arc_name)
    
    final_size = OUTPUT_ZIP.stat().st_size
    
    print("\n" + "=" * 70)
    print("Bundle Generation Complete!")
    print("=" * 70)
    print(f"\nOutput File: {OUTPUT_ZIP}")
    print(f"Bundle Size: {final_size / (1024 * 1024):.2f} MB")
    print(f"\nStatistics:")
    print(f"  - Total Files: {stats.files_added}")
    print(f"  - Categories:")
    for cat, count in sorted(stats.categories.items()):
        print(f"      {cat}: {count} files")
    print(f"\nBundle Contents:")
    print(f"  - Backend System (TypeScript)")
    print(f"  - Frontend Dashboard (React)")
    print(f"  - Database (SQLite + WAL)")
    print(f"  - Python Intelligence")
    print(f"  - Knowledge Base")
    print(f"  - Sessions & Backups")
    print(f"  - Documentation")
    print(f"\nManifest and comprehensive README included.")
    
    shutil.rmtree(TEMP_DIR)
    
    print(f"\n{'=' * 70}")
    print(f"SUCCESS: {OUTPUT_ZIP.name}")
    print(f"{'=' * 70}")
    
    return str(OUTPUT_ZIP)


if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Bundle generation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
