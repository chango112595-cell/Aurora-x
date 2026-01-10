# 🧠 Aurora Memory System

**Dual-memory architecture for contextual AI intelligence**

## Quick Start

```bash
# Start Aurora with memory system
npm run dev

# The memory system automatically:
# ✅ Starts on port 5003
# ✅ Connects to Aurora Core
# ✅ Enables API endpoints
```

## API Endpoints

### Write Memory
```bash
POST /api/memory/write
{
  "text": "Your text here",
  "meta": { "category": "user-prefs" },
  "longterm": false
}
```

### Query Memory
```bash
POST /api/memory/query
{
  "query": "search text",
  "top_k": 5
}
```

### Check Status
```bash
GET /api/memory/status
```

## Architecture

```
Short-Term Memory  →  Recent context, temporary data
Long-Term Memory   →  Core knowledge, persistent data
Vector Search      →  Semantic similarity matching
```

## Features

- ✅ Dual memory (short-term + long-term)
- ✅ Vector-based semantic search
- ✅ Metadata tagging
- ✅ HTTP API bridge
- ✅ Type-safe TypeScript client
- ✅ Automatic cleanup
- ✅ Production-ready

## Documentation

See `MEMORY_INTEGRATION_COMPLETE.md` for full documentation.

## Test

```bash
python test_memory_integration.py
```

---

**Status**: 🟢 Operational | **Version**: 1.0.0 | **Tests**: ✅ Passing
