#!/usr/bin/env python3
"""
Aurora Complete Codebase Documentation Generator

This script generates a single comprehensive file containing all Aurora code
with file tree structure, integration points, and complete source code.
"""

import os
import datetime
from pathlib import Path

# Core Aurora directories to include (in order of importance)
CORE_DIRECTORIES = [
    "manifests",           # 188 Tiers, 66 AEMs, 550 Modules
    "aurora_nexus_v3",     # Universal Consciousness System
    "controllers",         # Master Controller & Self-Healing
    "hyperspeed",          # Ultra-high-throughput operations
    "server",              # Backend (Express/TypeScript)
    "client/src",          # Frontend (React/TypeScript)
    "shared",              # Shared types/schemas
    "aurora_core",         # Core Aurora modules
    "aurora_x",            # Aurora-X Ultra engine
    "aurora_memory_fabric_v2",  # Memory Fabric
    "tools",               # Luminar Nexus V2
    "aurora_backend",      # Backend systems
    "aurora_modules",      # Additional modules
    "aurora_os",           # OS layer
    "aurora_edgeos",       # Edge runtimes
]

# File extensions to include
INCLUDE_EXTENSIONS = {
    '.py', '.ts', '.tsx', '.js', '.jsx', '.json', '.md',
    '.css', '.html', '.sh', '.yaml', '.yml', '.toml'
}

# Files/directories to skip
SKIP_PATTERNS = {
    'node_modules', '__pycache__', '.git', 'dist', 'build',
    '.next', 'coverage', '.cache', 'logs', 'backups',
    'unused', 'unused-components', 'pack_zips', 'gen_logs',
    '.egg-info', 'coverage_html', 'testbench'
}

def should_skip(path: str) -> bool:
    """Check if path should be skipped."""
    parts = Path(path).parts
    return any(skip in parts for skip in SKIP_PATTERNS)

def get_file_tree(directory: str, prefix: str = "") -> str:
    """Generate a tree view of the directory."""
    if not os.path.exists(directory):
        return f"{prefix}[Directory not found: {directory}]\n"
    
    lines = []
    try:
        entries = sorted(os.listdir(directory))
    except PermissionError:
        return f"{prefix}[Permission denied]\n"
    
    # Filter entries
    entries = [e for e in entries if not should_skip(os.path.join(directory, e))]
    
    for i, entry in enumerate(entries):
        path = os.path.join(directory, entry)
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        
        if os.path.isdir(path):
            lines.append(f"{prefix}{connector}{entry}/")
            extension = "    " if is_last else "│   "
            lines.append(get_file_tree(path, prefix + extension))
        else:
            ext = os.path.splitext(entry)[1]
            if ext in INCLUDE_EXTENSIONS or entry in ['Makefile', 'Dockerfile']:
                lines.append(f"{prefix}{connector}{entry}")
    
    return "\n".join(lines)

def read_file_content(filepath: str) -> str:
    """Read file content safely."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception as e:
        return f"[Error reading file: {e}]"

def collect_files(directory: str) -> list:
    """Collect all relevant files from a directory."""
    files = []
    if not os.path.exists(directory):
        return files
    
    for root, dirs, filenames in os.walk(directory):
        # Skip unwanted directories
        dirs[:] = [d for d in dirs if not should_skip(os.path.join(root, d))]
        
        for filename in sorted(filenames):
            filepath = os.path.join(root, filename)
            ext = os.path.splitext(filename)[1]
            
            if ext in INCLUDE_EXTENSIONS or filename in ['Makefile', 'Dockerfile']:
                files.append(filepath)
    
    return files

def generate_documentation():
    """Generate the complete Aurora codebase documentation."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    doc = []
    doc.append("=" * 100)
    doc.append("AURORA-X ULTRA - COMPLETE CODEBASE DOCUMENTATION")
    doc.append("=" * 100)
    doc.append(f"\nGenerated: {timestamp}")
    doc.append("\nThis file contains the complete Aurora codebase with all source files,")
    doc.append("showing how every component integrates from start to end.")
    doc.append("\n" + "=" * 100)
    
    # Table of Contents
    doc.append("\n\nTABLE OF CONTENTS")
    doc.append("-" * 50)
    doc.append("""
1. SYSTEM OVERVIEW
2. FILE TREE STRUCTURE
3. MANIFESTS (188 Tiers, 66 AEMs, 550 Modules)
4. AURORA NEXUS V3 (Universal Consciousness)
5. CONTROLLERS (Master Controller & Self-Healing)
6. HYPERSPEED MODE
7. SERVER (Express/TypeScript Backend)
8. CLIENT (React/TypeScript Frontend)
9. SHARED (Types & Schemas)
10. AURORA CORE MODULES
11. AURORA-X ULTRA ENGINE
12. MEMORY FABRIC
13. TOOLS (Luminar Nexus V2)
14. INTEGRATION POINTS
""")
    
    # System Overview
    doc.append("\n" + "=" * 100)
    doc.append("1. SYSTEM OVERVIEW")
    doc.append("=" * 100)
    doc.append("""
Aurora-X Ultra is an AI-powered autonomous code synthesis platform featuring:

CORE ARCHITECTURE:
- 188 Grandmaster Intelligence Tiers (Foundational 1-13 + Grandmaster 14-188)
- 66 Advanced Execution Methods (Sequential, Parallel, Speculative, etc.)
- 550 Cross-Temporal Modules (Ancient → Present → Futuristic)
- 300 Autonomous Workers (Non-conscious task executors)
- Hyperspeed Mode (1,000+ code units in <0.001 seconds)

KEY COMPONENTS:
- Aurora Nexus V3: Universal consciousness system with 300 workers
- Luminar Nexus V2: Chat + ML pattern learning
- Memory Fabric: Persistent knowledge storage
- Master Controller: Orchestrates all subsystems
- Self-Healing System: Automatic error recovery

TECHNOLOGY STACK:
- Backend: Express.js, TypeScript, Python
- Frontend: React, TypeScript, Vite, Tailwind CSS
- AI: Claude Sonnet 4 via Anthropic SDK
- Database: SQLite (corpus), PostgreSQL (production)
""")
    
    # File Tree Structure
    doc.append("\n" + "=" * 100)
    doc.append("2. FILE TREE STRUCTURE")
    doc.append("=" * 100)
    
    for directory in CORE_DIRECTORIES:
        if os.path.exists(directory):
            doc.append(f"\n{directory}/")
            doc.append("-" * 50)
            doc.append(get_file_tree(directory))
    
    # Process each directory
    section_num = 3
    section_names = {
        "manifests": "MANIFESTS (188 Tiers, 66 AEMs, 550 Modules)",
        "aurora_nexus_v3": "AURORA NEXUS V3 (Universal Consciousness)",
        "controllers": "CONTROLLERS (Master Controller & Self-Healing)",
        "hyperspeed": "HYPERSPEED MODE",
        "server": "SERVER (Express/TypeScript Backend)",
        "client/src": "CLIENT (React/TypeScript Frontend)",
        "shared": "SHARED (Types & Schemas)",
        "aurora_core": "AURORA CORE MODULES",
        "aurora_x": "AURORA-X ULTRA ENGINE",
        "aurora_memory_fabric_v2": "MEMORY FABRIC",
        "tools": "TOOLS (Luminar Nexus V2)",
        "aurora_backend": "AURORA BACKEND SYSTEMS",
        "aurora_modules": "AURORA MODULES",
        "aurora_os": "AURORA OS LAYER",
        "aurora_edgeos": "AURORA EDGE OS",
    }
    
    for directory in CORE_DIRECTORIES:
        if not os.path.exists(directory):
            continue
            
        section_name = section_names.get(directory, directory.upper())
        doc.append("\n" + "=" * 100)
        doc.append(f"{section_num}. {section_name}")
        doc.append("=" * 100)
        
        files = collect_files(directory)
        
        for filepath in files:
            rel_path = filepath
            doc.append(f"\n{'─' * 80}")
            doc.append(f"FILE: {rel_path}")
            doc.append(f"{'─' * 80}")
            
            content = read_file_content(filepath)
            doc.append(content)
        
        section_num += 1
    
    # Integration Points
    doc.append("\n" + "=" * 100)
    doc.append(f"{section_num}. INTEGRATION POINTS")
    doc.append("=" * 100)
    doc.append("""
HOW COMPONENTS INTEGRATE:

1. ENTRY POINTS:
   - ./aurora-start           → Main startup script
   - server/index.ts          → Express server entry
   - client/src/main.tsx      → React app entry
   - aurora_nexus_v3/main.py  → Nexus V3 entry

2. DATA FLOW:
   Frontend (React) 
     → API Routes (server/routes.ts)
     → Aurora Core (server/aurora-core.ts)
     → Aurora AI Orchestrator (server/aurora.ts)
     → Luminar Nexus V2 (tools/luminar_nexus_v2.py)
     → Aurora Nexus V3 (aurora_nexus_v3/core/universal_core.py)

3. WEBSOCKET CONNECTIONS:
   - /ws/synthesis → Real-time chat and progress updates
   - Handled by server/websocket-server.ts

4. MANIFEST LOADING:
   - manifests/tiers.manifest.json → 188 Intelligence Tiers
   - manifests/executions.manifest.json → 66 Execution Methods
   - manifests/modules.manifest.json → 550 Cross-Temporal Modules

5. WORKER DISPATCH:
   - aurora_nexus_v3/workers/task_dispatcher.py → Routes tasks
   - aurora_nexus_v3/workers/worker_pool.py → Manages 300 workers
   - aurora_nexus_v3/workers/issue_detector.py → Auto-detects problems

6. MEMORY PERSISTENCE:
   - aurora_memory_fabric_v2/ → Long-term knowledge storage
   - data/aurora_corpus.db → SQLite function corpus
""")
    
    # Root config files
    doc.append("\n" + "=" * 100)
    doc.append(f"{section_num + 1}. ROOT CONFIGURATION FILES")
    doc.append("=" * 100)
    
    root_files = [
        'package.json', 'tsconfig.json', 'vite.config.js',
        'tailwind.config.ts', 'drizzle.config.ts', 'requirements.txt',
        'Makefile', 'replit.md', 'aurora-start'
    ]
    
    for filename in root_files:
        if os.path.exists(filename):
            doc.append(f"\n{'─' * 80}")
            doc.append(f"FILE: {filename}")
            doc.append(f"{'─' * 80}")
            doc.append(read_file_content(filename))
    
    # Final summary
    doc.append("\n" + "=" * 100)
    doc.append("END OF AURORA CODEBASE DOCUMENTATION")
    doc.append("=" * 100)
    doc.append(f"\nTotal sections: {section_num + 1}")
    doc.append(f"Generated: {timestamp}")
    
    return "\n".join(doc)

if __name__ == "__main__":
    print("Generating Aurora Complete Codebase Documentation...")
    print("This may take a moment...")
    
    documentation = generate_documentation()
    
    # Save to file
    output_file = "AURORA_COMPLETE_CODEBASE.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(documentation)
    
    # Get file size
    size_mb = os.path.getsize(output_file) / (1024 * 1024)
    
    print(f"\nDone! Documentation saved to: {output_file}")
    print(f"File size: {size_mb:.2f} MB")
    print("\nThis file contains:")
    print("- Complete file tree structure")
    print("- All source code from core directories")
    print("- Integration documentation")
    print("- Configuration files")
