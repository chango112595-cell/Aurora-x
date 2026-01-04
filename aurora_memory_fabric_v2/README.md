# Aurora Memory Fabric v2 (Enhanced Hybrid System)

## Overview

Aurora Memory Fabric v2 is a comprehensive multi-tier hybrid memory engine designed for:

- **Short-term Memory**: Immediate chat/task context (session-based)
- **Mid-term Memory**: Task summaries & ongoing sub-projects
- **Long-term Memory**: Major milestones, persistent knowledge
- **Semantic Memory**: Encoded embeddings for reasoning and recall
- **Fact Memory**: Key facts (user name, preferences, etc.)
- **Event Memory**: Logs, actions, and system changes

## Features

- Multi-project compartmentalization
- Automatic summarization and compression
- Semantic search (vector cosine similarity)
- Encryption-ready storage
- Auto-backup and integrity verification
- Full integration with Aurora Core and Luminar Nexus

## Installation

```bash
# Extract the bundle
unzip aurora_memory_fabric_v2_bundle.zip -d .

# Run enhancement integration
python3 aurora_enhance_all.py --include-memory
```

## Usage

### Basic Usage

```python
from core.memory_fabric import AuroraMemoryFabric

am = AuroraMemoryFabric()
am.set_project("MyProject")

# Store facts
am.remember_fact("user_name", "Kai")

# Save messages
am.save_message("user", "Hello Aurora!")
am.save_message("aurora", "Hello! How can I help?")

# Recall facts
name = am.recall_fact("user_name")

# Semantic search
results = am.recall_semantic("previous conversations about Python")

# Get context for AI
context = am.get_context_summary()
```

### Integration with Aurora Core

```python
from integrations.aurora_core_integration import AuroraCoreIntelligence

core = AuroraCoreIntelligence("MyProject")
response = core.process("What is my name?")
core.remember("favorite_color", "blue")
```

### Integration with Luminar Nexus

```python
from integrations.nexus_integration import route_to_core

result = route_to_core("Hello Aurora!")
print(result["context"])
```

## Backup

Run the backup script manually or schedule it:

```bash
python3 ops/cronjobs/backup_memory.py
```

Or add to crontab for daily 2 AM backups:

```
0 2 * * * python3 /path/to/ops/cronjobs/backup_memory.py
```

## Testing

```bash
pytest tests/test_memory_fabric.py -v
```

## Directory Structure

```
aurora_memory_fabric_v2/
├── core/
│   └── memory_fabric.py        # Main memory engine
├── integrations/
│   ├── aurora_core_integration.py
│   └── nexus_integration.py
├── ops/
│   └── cronjobs/
│       └── backup_memory.py
├── tests/
│   └── test_memory_fabric.py
├── data/
│   └── memory/
│       └── global/
│           └── manifest.json
└── README.md
```

## Version

- **Version**: 2.0-enhanced
- **Author**: Aurora AI System
- **Features**: 188 tiers, 66 execution layers
