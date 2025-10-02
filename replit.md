# Aurora-X Ultra & Chango Integration

## Overview

This repository contains two integrated systems:

1. **Aurora-X Ultra** - An offline autonomous coding engine that synthesizes Python functions through AST-based beam search, corpus learning, and sandboxed execution
2. **Chango** - A JARVIS-inspired web interface that provides UI/UX for interacting with Aurora-X's synthesis capabilities

Aurora-X operates as a standalone Python package focused on program synthesis with zero external API dependencies. Chango provides a TypeScript/React frontend with Express backend for visualization and interaction.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Aurora-X (Python Engine)

**Core Synthesis Flow:**
- Spec parsing → Test generation → AST-based candidate synthesis → Sandbox execution → Iterative refinement
- Beam search with novelty detection to explore candidate solutions
- Symbolic reasoning and cost heuristics for scoring candidates
- Sandboxed unittest execution with timeout protection

**Corpus & Learning System (T02):**
- Dual-write persistence: JSONL (append-only) + SQLite (indexed queries)
- Records every synthesis attempt with metadata: function signature, pass/total tests, score, snippet, complexity
- Seeding system retrieves proven solutions from corpus using signature matching and TF-IDF fallback
- Adaptive bias learning (0.0-0.5 range) for balancing exploration vs exploitation

**Key Architectural Decisions:**
- **Offline-first**: Zero network calls by default; all synthesis happens locally
- **Security**: AST auditing prevents dangerous operations; restricted builtins in sandbox
- **Modularity**: Clean separation between core (spec parsing), synth (generation), corpus (storage), sandbox (execution)
- **Determinism**: Fixed seeds ensure reproducible test results

**File Structure:**
```
aurora_x/
├── main.py           # CLI orchestrator
├── corpus/
│   ├── store.py      # JSONL + SQLite dual-write
│   └── pretty.py     # Query formatting
├── debug.py          # Debugging utilities
└── bench.py          # Benchmarking module
```

### Chango (TypeScript Web Interface)

**Frontend Architecture:**
- React with TypeScript for type safety
- Wouter for client-side routing
- Radix UI components with Tailwind CSS styling
- TanStack Query for server state management
- Theme provider supporting light/dark modes

**Backend Architecture:**
- Express.js server with TypeScript
- Better-SQLite3 for corpus data storage
- Zod schemas for request/response validation
- Vite development server integration with HMR

**Key Pages:**
- `/` - Chat interface for natural language code requests
- `/dashboard` - Real-time synthesis monitoring
- `/library` - Browse synthesized functions
- `/corpus` - Explore and query corpus entries with filters
- `/settings` - Configure synthesis parameters

**Data Flow:**
1. Aurora-X synthesizes code and records to corpus (optional HTTP export via env flags)
2. Chango backend stores corpus entries in SQLite
3. Frontend queries corpus via REST API with pagination and filters
4. UI displays synthesis status, code previews, and corpus analytics

**API Endpoints:**
- `GET /api/corpus` - Query corpus with filters (func, date range, score)
- `GET /api/corpus/top` - Top performers by function
- `GET /api/corpus/recent` - Recent synthesis attempts
- `GET /api/corpus/similar` - Find similar solutions
- `GET /api/run-meta/latest` - Latest run metadata
- `POST /api/corpus` - Ingest corpus entry (currently disabled/commented)

**Architectural Decisions:**
- **Separation of Concerns**: Aurora-X remains independent; Chango provides optional UI layer
- **Optional Integration**: Aurora can POST corpus data via env flags (`AURORA_EXPORT_ENABLED`, `AURORA_POST_URL`)
- **Type Safety**: Shared Zod schemas between client and server prevent runtime errors
- **Performance**: Server-side pagination and filtering for large corpus datasets

## External Dependencies

### Aurora-X Dependencies
- **Python 3.10+** - Core runtime
- **SQLite3** - Local corpus storage (built-in to Python)
- **Standard Library Only** - No external packages required for core functionality
- **Optional**: bump-my-version for release automation

### Chango Dependencies
- **Node.js** - JavaScript runtime for backend
- **Better-SQLite3** - Native SQLite bindings for corpus storage
- **Express** - Web server framework
- **Vite** - Frontend build tool and dev server
- **React** - UI framework
- **TanStack Query** - Data fetching and caching
- **Radix UI** - Accessible component primitives
- **Tailwind CSS** - Utility-first styling
- **Zod** - Schema validation

### Integration Points
- Aurora-X can optionally export corpus data via HTTP POST to Chango backend
- Configured via environment variables (no hard coupling)
- Chango can operate independently with mock data or existing corpus
- Both systems use SQLite for corpus storage (compatible schemas)

### Development Tools
- **TypeScript** - Type checking for Chango
- **ESBuild/TSX** - Fast TypeScript compilation
- **Pre-commit hooks** - Code quality (Ruff for Python)
- **Make** - Build automation for Aurora-X