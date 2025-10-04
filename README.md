# Aurora-X Ultra

![seed-bias](https://img.shields.io/badge/seed__bias-dynamic-%23007acc?label=seed_bias&style=flat)
![offline](https://img.shields.io/badge/mode-offline--first-green?style=flat)

_Offline Autonomous Code Synthesis Engine_

## Overview
Aurora-X is an autonomous code synthesis engine that uses AST-based mutations, beam search, and corpus-based seeding to synthesize functions from specifications. Aurora is **offline-first** — it records to JSONL/SQLite locally and never calls external APIs unless you enable explicit exports.

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
aurorax --spec-file ./specs/rich_spec.md --outdir runs

# Query corpus for past synthesis attempts
aurorax --dump-corpus "add(a:int,b:int)->int" --top 5

# Quick check of bias without running synthesis
aurorax --show-bias --outdir runs

# Run tests
make test
```

## Seed Bias
- Current run's `seed_bias` is shown in the HTML report header and printed by the CLI when a run ends.
- File path: `runs/run-*/learn_weights.json`.

## Project Status
- ✅ **Milestone 1**: Core synthesis engine complete
- ✅ **Milestone 2**: Corpus recording and seeding implemented
- 🔜 **Next**: Auto-bias tuning and advanced learning strategies