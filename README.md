# Aurora-X Ultra
_Offline Autonomous Code Synthesis Engine_

## Overview
Aurora-X is an autonomous code synthesis engine that uses AST-based mutations, beam search, and corpus-based seeding to synthesize functions from specifications.

## Features
- **AST-based synthesis** with beam search and mutations
- **Persistent corpus** in JSONL + SQLite format
- **Seeding system** that learns from past successful snippets
- **Signature normalization** and TF-IDF fallback matching
- **CLI interface** for corpus queries and synthesis runs

## Installation
```bash
pip install -e .
```

## Usage
```bash
# Run synthesis with seeding
make run

# Query corpus for past synthesis attempts
aurorax --dump-corpus "add(a:int,b:int)->int" --top 5

# Run tests
make test
```

## Project Status
- ✅ **Milestone 1**: Core synthesis engine complete
- ✅ **Milestone 2**: Corpus recording and seeding implemented
- 🔜 **Next**: Auto-bias tuning and advanced learning strategies