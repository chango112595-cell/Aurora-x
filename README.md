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
- **Learning seeds** with EMA-based bias updates and drift caps
- **Signature normalization** and TF-IDF fallback matching
- **CLI interface** for corpus queries and synthesis runs
- **Web API** with seed bias tracking endpoint

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

## Learning Seeds

Aurora-X uses persistent learning seeds to improve synthesis performance across runs. The system tracks successful synthesis patterns and adjusts biases using Exponential Moving Average (EMA) with drift caps.

### Configuration
- **Alpha**: EMA smoothing factor (default: 0.2)
- **Drift Cap**: Maximum allowed drift per update (default: ±0.15)
- **Top N**: Number of top bias terms kept (default: 10)

### Seed Persistence
- Seeds are stored in `.aurora/seeds.json`
- Each function signature gets a unique seed key
- Biases range from -1.0 to 1.0 (negative = poor, positive = good)

### Environment Variables
- `AURORA_SEED`: Set random seed for reproducible runs
- `AURORA_SEEDS_PATH`: Override default seed storage path

### API Endpoints
```bash
# Get seed bias summary and top reasons
curl http://localhost:8080/api/seed_bias
```

Response:
```json
{
  "summary": {
    "total_seeds": 15,
    "avg_bias": 0.1234,
    "max_bias": 0.4567,
    "min_bias": -0.2345,
    "total_updates": 42,
    "config": {
      "alpha": 0.2,
      "drift_cap": 0.15,
      "top_n": 10
    }
  },
  "top_biases": [
    {"seed_key": "abc123", "bias": 0.4567},
    {"seed_key": "def456", "bias": 0.3456}
  ]
}
```

## Seed Bias (Legacy)
- Current run's `seed_bias` is shown in the HTML report header and printed by the CLI when a run ends.
- File path: `runs/run-*/learn_weights.json`.

## Reproducible Runs

To ensure reproducible synthesis runs:

```bash
# Set fixed random seed
export AURORA_SEED=42

# Use specific seed storage
export AURORA_SEEDS_PATH=/path/to/seeds.json

# Run synthesis
aurorax --spec-file ./specs/rich_spec.md --seed $AURORA_SEED
```

## Project Status
- ✅ **Milestone 1**: Core synthesis engine complete
- ✅ **Milestone 2**: Corpus recording and seeding implemented
- ✅ **Milestone 3**: Persistent learning seeds with EMA updates
- 🔜 **Next**: Advanced learning strategies and visualization