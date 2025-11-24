#!/usr/bin/env python3
"""
Aurora Knowledge Consolidation
Takes all duplicate/unfinished programs and adds them to corpus as learning examples
"""

import json
from datetime import datetime
from pathlib import Path

# Programs to consolidate into corpus
LEARNING_SOURCES = [
    {
        "file": "tools/ultimate_api_manager.py",
        "title": "Ultimate API Manager - Advanced autonomous features",
        "lessons": [
            "Fast health monitoring (< 1 second)",
            "Performance metrics and analytics",
            "Progressive scan intervals based on system health",
            "Comprehensive system scanning",
            "Advanced auto-healing with intelligent decisions",
            "Emergency failover support",
            "Connection monitoring and auto-fix",
        ],
        "category": "advanced_server_management",
    },
    {
        "file": "aurora_ultimate_coding_grandmaster.py",
        "title": "Grandmaster Coding Elevation - Production-ready code generation",
        "lessons": [
            "Generate complete code with NO TODOs",
            "Production-ready immediately",
            "Architectural decision making",
            "Complete error handling (not stubs)",
            "Type hints and documentation",
            "Test generation for own code",
        ],
        "category": "code_generation_mastery",
    },
    {
        "file": "aurora_ultimate_omniscient_grandmaster.py",
        "title": "Omniscient Grandmaster - Ultimate autonomy",
        "lessons": [
            "Independent task execution",
            "Self-directed learning",
            "Autonomous problem solving",
            "Zero human intervention operation",
        ],
        "category": "autonomous_operation",
    },
    {
        "file": "tools/aurora_process_grandmaster.py",
        "title": "Process Grandmaster - Process management expertise",
        "lessons": [
            "Advanced process control",
            "Tmux session management",
            "Port conflict resolution",
            "Process health monitoring",
        ],
        "category": "process_management",
    },
]


def consolidate_to_corpus():
    """Add all learning sources to Aurora's corpus"""

    print("[BRAIN] AURORA KNOWLEDGE CONSOLIDATION")
    print("=" * 70)
    print("Converting duplicate/unfinished code into learning corpus...\n")

    corpus_entries = []

    for source in LEARNING_SOURCES:
        filepath = Path(source["file"])

        if not filepath.exists():
            print(f"[WARN]  {source['file']} not found, skipping")
            continue

        # Read the source code
        code = filepath.read_text()

        # Create corpus entry
        entry = {
            "id": f"learning_{source['category']}_{datetime.now().timestamp()}",
            "source_file": source["file"],
            "title": source["title"],
            "category": source["category"],
            "lessons_learned": source["lessons"],
            "code_sample": code[:2000],  # First 2000 chars as sample
            "full_code_available": True,
            "added_to_corpus": datetime.now().isoformat(),
            "status": "reference_material",
            "use_case": "Aurora can reference these patterns when needed",
        }

        corpus_entries.append(entry)
        print(f"[OK] Added: {source['title']}")
        print(f"   Category: {source['category']}")
        print(f"   Lessons: {len(source['lessons'])}")
        print()

    # Save to Aurora's knowledge base
    knowledge_file = Path(".aurora_knowledge/consolidated_learning_corpus.json")
    knowledge_file.parent.mkdir(exist_ok=True)

    with open(knowledge_file, "w") as f:
        json.dump(
            {
                "consolidation_date": datetime.now().isoformat(),
                "total_sources": len(corpus_entries),
                "entries": corpus_entries,
                "purpose": "Reference library of advanced patterns Aurora can learn from",
            },
            f,
            indent=2,
        )

    print("=" * 70)
    print(f"[OK] Consolidated {len(corpus_entries)} sources into corpus")
    print(f"[EMOJI] Saved to: {knowledge_file}")
    print("\n[EMOJI] Aurora now has these as reference patterns!")
    print("   She can learn from them without code duplication")

    return knowledge_file


if __name__ == "__main__":
    consolidate_to_corpus()
