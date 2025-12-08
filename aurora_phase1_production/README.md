# Aurora Phase-1 Production Bundle

A production-ready autonomy system for Aurora module generation, inspection, testing, and promotion.

**Features:**
- Universal cross-platform support (Linux, macOS, Windows, WSL)
- GPU acceleration via PyTorch (auto-detected)
- 550 temporal module infrastructure
- Generate -> Inspect -> Test -> Promote pipeline
- Auto-registration for Aurora Core

## Structure

```
aurora_phase1_production/
├── tools/
│   ├── make_550_manifest.py      # Generates module manifests
│   ├── generate_modules.py       # Production module generator
│   ├── generate_aurora_modules.py # Universal 550-module generator with GPU
│   └── universal_build.py        # Cross-platform build script
├── aurora_nexus_v3/
│   └── autonomy/
│       ├── sandbox_runner_no_docker.py  # Containerless sandbox runner
│       ├── etcd_store.py                # File-backed registry & locking
│       └── manager.py                   # AutonomyManager orchestrator
├── inspector/
│   └── inspector.py              # Static code inspector with banned-pattern checks
├── rule_engine/
│   └── rule_engine.py            # Severity scoring and decision engine
├── lifecycle/
│   └── lifecycle.py              # Runtime loader for module lifecycle
├── module_generator/
│   └── helpers.py                # Candidate generation, snapshot, promote helpers
└── tests/
    └── run_phase1_tests.py       # Automated test script
```

## Quick Start

### 1. Create a Manifest

Generate a manifest with module definitions:

```bash
python tools/make_550_manifest.py --out aurora_nexus_v3/manifests/modules.manifest.json --count 10
```

Options:
- `--count N` - Number of modules to generate (default: 550)
- `--categories` - Limit to specific categories
- `--pretty` - Pretty print JSON output

### 2. Generate Modules

Generate module files from manifest:

```bash
python tools/generate_modules.py \
  --manifest aurora_nexus_v3/manifests/modules.manifest.json \
  --out aurora_nexus_v3/generated_modules \
  --force
```

### 3. Run Autonomy Pipeline

Run the full generate -> inspect -> test -> promote pipeline:

```bash
python -c "
from aurora_nexus_v3.autonomy.manager import AutonomyManager
import json

manager = AutonomyManager()
result = manager.run_pipeline('0001', 'connector', 'http')
print(json.dumps(result, indent=2, default=str))
"
```

### 4. Handle an Incident

```bash
echo '{"module_id":"0001"}' | python -c "
import sys, json
from aurora_nexus_v3.autonomy.manager import AutonomyManager, Incident

payload = json.load(sys.stdin)
manager = AutonomyManager({})
incident = Incident(
    module_id=payload['module_id'],
    error='Test error',
    stacktrace='',
    metrics={},
    extra={}
)
result = manager.handle_incident(incident)
print(result)
"
```

## Components

### Manifest Generator (`tools/make_550_manifest.py`)

Creates structured manifests with:
- 10 module categories (connector, processor, analyzer, etc.)
- Multiple drivers per category
- Configurable capabilities
- Checksum validation

### Module Generator (`tools/generate_modules.py`)

Generates production-ready modules with:
- Init, execute, and cleanup lifecycle methods
- Category-specific templates
- Driver configuration
- Error handling

### Autonomy Manager (`aurora_nexus_v3/autonomy/manager.py`)

Orchestrates the full pipeline:
- **Generate**: Create candidate modules
- **Inspect**: Check for banned patterns and security issues
- **Test**: Run in sandboxed environment
- **Promote**: Move to production with snapshots

### Sandbox Runner (`aurora_nexus_v3/autonomy/sandbox_runner_no_docker.py`)

Containerless execution with:
- AST-based code validation
- Resource limits (CPU, memory, files)
- Dangerous import blocking
- Timeout enforcement

### Code Inspector (`inspector/inspector.py`)

Static analysis with:
- Banned pattern detection (eval, exec, os.system, etc.)
- AST-based structural analysis
- Complexity scoring
- Quality grading

### Rule Engine (`rule_engine/rule_engine.py`)

Decision engine with:
- Severity scoring (0-10 scale)
- Action determination (disable, rollback, regenerate, notify)
- Configurable rules
- Evaluation history

### Lifecycle Runner (`lifecycle/lifecycle.py`)

Module lifecycle management:
- Dynamic module loading
- Phase execution (init, execute, cleanup)
- Timeout enforcement
- Batch execution

### Module Generator Helpers (`module_generator/helpers.py`)

Helper utilities for:
- Candidate generation with templates
- Snapshot management with versioning
- Promotion with automatic backups

## Running Tests

Run the automated test suite:

```bash
python tests/run_phase1_tests.py --count 10 --audit-report test_audit.json
```

## Universal 550 Module Generator

Generate all 550 temporal modules with GPU acceleration support:

```bash
# HYBRID MODE: Enhanced generator with Nexus V3 bridge (recommended)
python tools/enhanced_generate_aurora_modules.py --output aurora_x --zip

# Standalone generation with ZIP archive
python tools/generate_aurora_modules.py --output aurora_x --registry

# Check system capabilities first
python tools/generate_aurora_modules.py --check-system

# Full universal build (system check + generation)
python tools/universal_build.py --output aurora_build --modules 550
```

### Nexus V3 Bridge Integration

The `enhanced_generate_aurora_modules.py` creates a NexusBridge that:
- Plugs into V3 lifecycle hooks (on_boot, on_tick, on_reflect)
- Keeps Luminar V2 chat separate but queryable through V3
- Uses V3's existing ThreadPool (no double-threads)
- Falls back gracefully when GPU/optional libs missing

```python
from aurora_nexus_v3.core import NexusBridge

bridge = NexusBridge(module_path='aurora_nexus_v3/modules')
bridge.load_modules()
bridge.attach_v3_core(v3_core)  # optional

# Query from Luminar V2 through V3
response = bridge.execute(101, {'task': 'semantic-summary'})
```

### Temporal Categories

| Category | ID Range | Drivers | Description |
|----------|----------|---------|-------------|
| Ancient | 1-100 | cpu, sequential, symbolic | Pattern recognition, logic, reasoning |
| Classical | 101-250 | cpu, parallel, distributed | Algorithms, structures, systems |
| Modern | 251-450 | cpu, gpu, tpu, distributed | ML, AI agents, real-time adaptation |
| Futuristic | 451-550 | gpu, quantum, neural, hybrid | Quantum computing, neural links |

### GPU Support

Modules in Modern (251-450) and Futuristic (451-550) categories have GPU acceleration when:
- PyTorch is installed (`pip install torch`)
- CUDA is available
- Driver is `gpu` or `hybrid`

Each module exposes:
- `.execute()` - Main operational logic
- `.learn()` - Adaptive update hooks
- `.diagnose()` - Self-checks and reporting
- `.metadata()` - System metadata for discovery
- `.gpu_accelerate()` - GPU acceleration (if available)

## Phase-1 Module Categories

| Category | Drivers | Description |
|----------|---------|-------------|
| connector | http, grpc, websocket, mqtt, amqp | Connection handling |
| processor | batch, stream, parallel, sequential | Data processing |
| analyzer | pattern, statistical, ml, rule-based | Analysis operations |
| validator | schema, semantic, syntax, constraint | Validation logic |
| transformer | json, xml, csv, binary, protobuf | Data transformation |
| optimizer | cache, compression, dedup, index | Optimization routines |
| monitor | metrics, logs, traces, alerts | Monitoring systems |
| generator | template, procedural, ml, rule | Content generation |
| formatter | text, html, markdown, pdf | Output formatting |
| integrator | api, database, filesystem, message-queue | Integration bridges |

## Security

The sandbox runner blocks:
- Direct imports: os, sys, subprocess, socket, ctypes
- Dangerous builtins: eval, exec, compile, __import__, open
- System calls: os.system, os.popen, os.spawn

Severity levels for issues:
- **9-10**: Critical - Disable module immediately
- **7-8**: High - Rollback to previous version
- **4-6**: Medium - Attempt regeneration
- **1-3**: Low - Notify for review

## Audit Logs

All operations are logged to `aurora_data/audit/audit_YYYYMMDD.jsonl`:
- Incident handling
- Repair actions
- Module promotions
- Pipeline executions
