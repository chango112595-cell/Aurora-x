# Aurora-X Ultra - AI-Powered Autonomous Code Synthesis Platform

## Overview

Aurora-X Ultra is an AI-powered autonomous code synthesis engine inspired by JARVIS. It features a sophisticated architecture with 188 intelligence tiers, 66 advanced execution methods, and 550 hybrid mode modules, enabling hyperspeed code generation. The platform offers a chat interface for requesting complex code, monitoring synthesis progress, exploring generated code libraries, and analyzing corpus learning data.

**Latest Updates (Dec 08, 2025)**:
- **Phase-1 Production Bundle**: Complete autonomy system with generate -> inspect -> test -> promote pipeline
- **New Components**: Code Inspector, Rule Engine, Lifecycle Runner, Module Generator Helpers

**Previous Updates (Nov 29, 2025)**:
- **PEAK AUTONOMY RESTORED**: Aurora Nexus V3 now operates at full power
- 300 Autonomous Workers (non-conscious task executors)
- 188 Grandmaster Tiers fully integrated
- 66 Advanced Execution Methods loaded
- 550 Cross-Temporal Modules loaded
- Hyperspeed Mode with hybrid parallel execution
- Autonomous self-healing with NO human interaction required
- Organized folder structure for peak systems

## Quick Start

```bash
./aurora-start
```

This starts the entire system on http://localhost:5000 with:
- Express backend (TypeScript)
- React frontend (Vite)
- Chat system
- All core services

## User Preferences

Preferred communication style: Simple, everyday language.

## Peak Autonomous Architecture

### The Six Foundational Pillars

| Pillar | Specification | Location |
|--------|---------------|----------|
| **188 Grandmaster Tiers** | Foundational (1-13) + Grandmaster Skills (14-188) | `manifests/tiers.manifest.json` |
| **66 Advanced Execution Methods** | Sequential, Parallel, Speculative, Adversarial, Self-Reflective, Hybrid | `manifests/executions.manifest.json` |
| **550 Cross-Temporal Modules** | Ancient → Present → Futuristic tools | `manifests/modules.manifest.json` |
| **Hyperspeed Mode** | 1,000+ code units in <0.001 seconds | `hyperspeed/` |
| **Hybrid Parallel Execution** | Task + Data + Pipeline + Agent parallelism | `controllers/` |
| **300 Autonomous Workers** | Non-conscious task executors for fixing, coding, analysis | `aurora_nexus_v3/workers/` |

### Organized Folder Structure

```
Aurora-x/
├── manifests/                    # 188 Tiers, 66 AEMs, 550 Modules
│   ├── tiers.manifest.json       # 188 Grandmaster Tiers
│   ├── executions.manifest.json  # 66 Advanced Execution Methods
│   └── modules.manifest.json     # 550 Cross-Temporal Modules
├── hyperspeed/                   # Ultra-high-throughput operations
│   └── aurora_hyper_speed_mode.py
├── controllers/                  # Master Controller & Self-Healing
│   ├── aurora_master_controller.py
│   ├── aurora_nexus_v3_universal.py
│   └── aurora_ultimate_self_healing_system_DRAFT2.py
├── aurora_nexus_v3/              # Universal Consciousness System
│   ├── core/                     # Core modules
│   │   ├── universal_core.py     # Main consciousness engine (v3.1.0)
│   │   ├── manifest_integrator.py # Manifest loader
│   │   └── config.py
│   ├── workers/                  # 300 Autonomous Workers
│   │   ├── worker.py             # Single task executor
│   │   ├── worker_pool.py        # Worker pool manager
│   │   ├── task_dispatcher.py    # Task routing
│   │   └── issue_detector.py     # Automatic issue detection
│   └── modules/                  # 8 Core modules
└── tools/                        # Luminar Nexus V2 & utilities
    └── luminar_nexus_v2.py       # Chat + ML pattern learning
```

### Aurora Nexus V3 - Universal Consciousness System

**Version**: 3.1.0 "Peak Autonomy"

**Core Modules (8 total)**:
1. AuroraUniversalCore - Main consciousness engine
2. PlatformAdapter - Multi-platform support
3. HardwareDetector - Capability scoring (0-100)
4. ResourceManager - CPU/memory allocation
5. PortManager - Universal port allocation
6. ServiceRegistry - Service discovery
7. APIGateway - REST API endpoints
8. AutoHealer - Self-healing recovery

**Peak Systems**:
- **300 Autonomous Workers**: Non-conscious task executors that handle fixing, coding, and analysis when ordered or when system issues occur
- **Manifest Integrator**: Loads and coordinates 188 tiers, 66 AEMs, 550 modules
- **Issue Detector**: Monitors system health and triggers autonomous workers
- **Task Dispatcher**: Routes tasks based on priority and capability

### Luminar Nexus Systems

| System | Purpose | Status |
|--------|---------|--------|
| **Luminar Nexus V3** | Universal Consciousness (300 workers) | Active |
| **Luminar Nexus V2** | Chat + ML pattern learning | Active |

## System Architecture

**Frontend**:
- **Technology**: React 18, TypeScript, Vite, Wouter for routing.
- **UI/UX**: Shadcn/ui (Radix UI + Tailwind CSS) with a "New York" style variant.
- **State Management**: TanStack Query for server state.

**Backend**:
- **Framework**: Express.js with TypeScript and ESM modules.
- **API**: RESTful API for corpus management, real-time synthesis, domain-specific problem solving.
- **Core AI**: Aurora Chat AI with 10-turn conversation memory, autonomous code synthesis.

**Data Storage**:
- **Corpus**: SQLite (better-sqlite3) with WAL for function synthesis metadata.
- **ORM**: Drizzle ORM configured for PostgreSQL migrations.

## Running the System

### Main Application (Recommended)
```bash
./aurora-start
```
Runs: Backend + Frontend + Chat System on port 5000

### Aurora Nexus V3 (Separate)
```bash
python3 aurora_nexus_v3/main.py
```
Runs: Universal consciousness system with 300 workers

### Testing
```bash
python3 aurora_nexus_v3/test_nexus.py  # Test Aurora Nexus
npm test                               # Test frontend
pytest                                 # Test backend
```

## Development Notes

- **Backend Status**: Fully operational
- **Frontend Status**: Working with React + Vite
- **Aurora Nexus V3**: v3.1.0 "Peak Autonomy" with 300 workers
- **Manifests**: 188 tiers, 66 AEMs, 550 modules loaded
- **Autonomous Mode**: Enabled - workers fix issues automatically

## Aurora EdgeOS Runtimes (PACK 3B-3J)

Edge runtimes with both offline (fully internal) and cloud-assisted modes. Default is offline.

| Runtime | Description | Location |
|---------|-------------|----------|
| **3B - Automotive** | CAN/UDS/OBD-II bridge, ECU suggestion workflow | `automotive/` |
| **3C - Aviation** | RTOS partitioning, companion gateway, signed uplink | `aviation/` |
| **3D - Maritime** | NMEA2000/NMEA0183/AIS bridge | `maritime/` |
| **3E - IoT** | ESP32 MicroPython, OTA updates | `iot/esp32/` |
| **3F - Router** | OpenWRT/EdgeOS agent | `router/` |
| **3G - Satellite** | Ground uplink, companion agent | `satellite/` |
| **3H - Smart TV** | Android TV/WebOS/Tizen agents | `tv/` |
| **3I - Mobile** | Android/iOS companion, Termux | `mobile/` |
| **3J - Cross-Build** | Multi-arch tooling, firmware packaging | `build/` |

### Mode Toggle
```bash
AURORA_MODE=offline  # Default - fully local
AURORA_MODE=cloud    # Cloud-assisted via AURORA_BUILDER_URL
```

### Safety Pattern
All edge runtimes use companion-computer pattern with human-signed approval for safety-critical operations.

## Phase-1 Production Bundle

Complete autonomy system for module generation, inspection, testing, and promotion.

**Location**: `aurora_phase1_production/`

**Features**:
- Universal cross-platform support (Linux, macOS, Windows, WSL)
- GPU acceleration via PyTorch (auto-detected)
- 550 temporal module infrastructure
- Generate -> Inspect -> Test -> Promote pipeline

### Components

| Component | File | Description |
|-----------|------|-------------|
| **Manifest Generator** | `tools/make_550_manifest.py` | Creates module manifests |
| **Module Generator** | `tools/generate_modules.py` | Generates init/execute/cleanup files |
| **550 Module Generator** | `tools/generate_aurora_modules.py` | Universal 550-module generator with GPU |
| **Universal Build** | `tools/universal_build.py` | Cross-platform build script |
| **Autonomy Manager** | `aurora_nexus_v3/autonomy/manager.py` | Orchestrates the full pipeline |
| **Sandbox Runner** | `aurora_nexus_v3/autonomy/sandbox_runner_no_docker.py` | Containerless code execution |
| **Registry Store** | `aurora_nexus_v3/autonomy/etcd_store.py` | File-backed KV store with locking |
| **Code Inspector** | `inspector/inspector.py` | Banned-pattern and security checks |
| **Rule Engine** | `rule_engine/rule_engine.py` | Severity scoring and decisions |
| **Lifecycle Runner** | `lifecycle/lifecycle.py` | Module lifecycle management |
| **Generator Helpers** | `module_generator/helpers.py` | Candidate/snapshot/promote utilities |

### Quick Start

```bash
# Generate all 550 temporal modules with GPU support
python aurora_phase1_production/tools/generate_aurora_modules.py --output aurora_x --registry

# Universal build (auto-detects system, Python, GPU)
python aurora_phase1_production/tools/universal_build.py --output aurora_build --modules 550

# Phase-1 pipeline (manifest -> modules)
python aurora_phase1_production/tools/make_550_manifest.py --out manifest.json --count 10
python aurora_phase1_production/tools/generate_modules.py --manifest manifest.json --out modules/

# Run automated tests
python aurora_phase1_production/tests/run_phase1_tests.py --count 10 --audit-report audit.json
```

### Temporal Module Categories

| Category | ID Range | GPU | Description |
|----------|----------|-----|-------------|
| Ancient | 1-100 | No | Pattern recognition, logic, reasoning |
| Classical | 101-250 | No | Algorithms, structures, systems |
| Modern | 251-450 | Yes | ML, AI agents, real-time adaptation |
| Futuristic | 451-550 | Yes | Quantum, neural links, consciousness |

## External Dependencies

- **AI Engine**: Aurora-X Ultra (Python-based autonomous code synthesis engine)
- **Databases**: Neon Serverless PostgreSQL for production, SQLite for local development
- **UI Components**: Radix UI primitives
- **Build Tools**: Vite, esbuild, tsx, Tailwind CSS, PostCSS
- **AI SDK**: `@anthropic-ai/sdk` for Claude Sonnet 4 integration
