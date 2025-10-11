
# 🌌 AURORA-X ULTRA - COMPLETE PROJECT DOCUMENTATION

## Project Overview

Aurora-X Ultra is an **offline-first autonomous code synthesis engine** with persistent learning, adaptive exploration, and comprehensive monitoring capabilities.

### Core Features
- **Offline-first architecture** - No external API dependencies by default
- **Persistent learning seeds** - EMA-based bias updates with drift caps
- **Adaptive exploration** - ε-greedy strategy with decay and cooldown
- **Multi-function specs** - SpecDSL v3 with examples and post-conditions
- **Live dashboard** - Real-time monitoring with WebSocket updates
- **Production hardening** - CI gates, Discord notifications, automated backups
- **Autonomous orchestrator** - Watches specs, auto-compiles, runs tests

---

## 📁 Project Structure

```
aurora-x-ultra/
├── aurora_x/                    # Core Python engine
│   ├── config/                  # Configuration management
│   ├── corpus/                  # Corpus storage (JSONL + SQLite)
│   ├── learn/                   # Learning & adaptation
│   ├── spec/                    # Spec parsers (v2, v3, NL)
│   ├── synthesis/               # Code synthesis engine
│   ├── main.py                  # Main orchestration
│   ├── serve.py                 # Task tracker server
│   └── orchestrator.py          # Autonomous watcher
│
├── server/                      # TypeScript/Express backend
│   ├── routes.ts                # API endpoints
│   ├── corpus-storage.ts        # Corpus integration
│   └── vite.ts                  # Vite dev server
│
├── client/                      # React frontend
│   └── src/
│       ├── components/          # UI components
│       ├── pages/               # Route pages
│       └── lib/                 # Utilities
│
├── tools/                       # Build & automation tools
│   ├── spec_compile_v3.py       # Spec compiler
│   ├── notify_discord.py        # Discord integration
│   ├── update_progress.py       # Progress tracking
│   └── ci_gate.py              # CI validation
│
├── specs/                       # Function specifications
├── runs/                        # Synthesis output runs
└── tests/                       # Test suite
```

---

## 🚀 Core Components

### 1. Spec DSL v3 Parser

**File:** `aurora_x/spec/parser_v3.py`

Parses markdown specs with:
- Function signatures
- Example inputs/outputs
- Post-conditions
- Multi-function support

```python
# Example spec:
"""
# SpecV3: Palindrome Checker

def check_palindrome(s: str) -> bool
def reverse_string(s: str) -> str

## Examples
check_palindrome("racecar") -> true
reverse_string("hello") -> "olleh"

## Post
assert check_palindrome(reverse_string(x) + x) == true
"""
```

### 2. Synthesis Engine

**File:** `aurora_x/synthesis/search.py`

Features:
- AST-based code generation
- Beam search with mutations
- Corpus-based seeding
- Security auditing (forbidden imports/calls)

### 3. Persistent Learning Seeds

**File:** `aurora_x/learn/seeds.py`

- EMA updates (α=0.2)
- Drift caps (±0.15)
- Top-N tracking (10 seeds)
- JSON persistence

```python
class SeedStore:
    def update(self, result):
        # EMA: new = (1-α)*old + α*value
        # Drift cap: max ±0.15 per update
```

### 4. Adaptive Learning Engine

**File:** `aurora_x/learn/adaptive.py`

```python
class AdaptiveBiasScheduler:
    # ε-greedy exploration (ε=0.15)
    # Decay per iteration (0.98)
    # Cooldown: 5 iterations
    # Max drift: 0.10 per iteration
```

### 5. Corpus Storage

**Files:** `aurora_x/corpus/store.py`, `server/corpus-storage.ts`

- **Python:** JSONL + SQLite local storage
- **TypeScript:** API integration with Express
- Signature normalization
- TF-IDF similarity matching

---

## 🛠️ Key Commands

### Installation
```bash
pip install -e .
npm install
```

### Synthesis
```bash
# Compile spec to code
python tools/spec_compile_v3.py specs/example.md

# Run orchestrator (watches /specs)
make orchestrate-bg

# Manual synthesis
python -m aurora_x.main --spec-file specs/example.md
```

### Dashboard
```bash
# Start dashboard
make serve-v3

# Access at
http://localhost:5000/dashboard
```

### Testing
```bash
# Run all tests
make test

# CI gate checks
make ci

# Specific test
pytest tests/test_adaptive.py -v
```

### Progress Tracking
```bash
# Update task progress
python -m aurora_x.main --update-task T02.1.6=75

# Bump progress
python -m aurora_x.main --bump T02.1.6=+5

# Generate summary
make summary
```

---

## 📊 Configuration

### Production Config

**File:** `aurora_x/prod_config.py`

```python
@dataclass(frozen=True)
class ProdConfig:
    EPSILON: float = 0.15          # Exploration rate
    DECAY: float = 0.98            # Bias decay
    COOLDOWN_ITERS: int = 5        # Reuse cooldown
    MAX_DRIFT: float = 0.10        # Max drift per iter
    TOP_K: int = 10                # Top biases to track
```

### Environment Variables
```bash
# Discord notifications
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Orchestrator
AURORA_ORCH_INTERVAL=300          # Poll interval (seconds)
AURORA_GIT_AUTO=1                 # Enable auto-commit
AURORA_GIT_URL=https://github.com/user/repo.git

# Seeds
AURORA_SEED=42                    # Reproducible runs
AURORA_SEEDS_PATH=.aurora/seeds.json
```

---

## 🔄 Workflows

### 1. Spec → Code Flow

```
1. Create/edit spec in /specs/*.md
2. Orchestrator detects change (SHA256)
3. tools/spec_compile_v3.py parses spec
4. Synthesis engine generates code + tests
5. Tests run in sandbox
6. Results → runs/run-YYYYMMDD-HHMMSS/
7. Dashboard updates (WebSocket)
8. Optional: Discord alert + Git push
```

### 2. Learning Flow

```
1. Synthesis attempts recorded to corpus
2. Success/failure updates seed biases (EMA)
3. Adaptive scheduler adjusts exploration
4. Next synthesis uses learned biases
5. Periodic snapshots to .progress_history/
```

---

## 📈 API Endpoints

### Aurora-X Endpoints (Python)

```
GET  /api/adaptive_stats         # Scheduler statistics
GET  /api/seed_bias              # Seed bias summary
GET  /api/seed_bias/history      # Bias history
```

### Dashboard Endpoints (Express)

```
GET  /api/corpus/runs            # Recent runs
GET  /api/corpus/functions       # Function library
POST /api/corpus/record          # Record entry
GET  /dashboard                  # Dashboard UI
```

---

## 🧪 Testing

### Test Files
- `tests/test_seeds.py` - Seed store tests
- `tests/test_adaptive.py` - Adaptive scheduler tests
- `tests/test_corpus_store.py` - Corpus storage tests
- `tests/test_learn_weights.py` - Learning weights tests

### CI Gates
```bash
python tools/ci_gate.py
```

Validates:
- Production config bounds
- Deterministic scheduler
- Drift bounds (max 5.0)
- Seed persistence

---

## 🔐 Security

### Forbidden Operations
- File system access (os.remove, shutil.rmtree)
- Network calls (urllib, requests)
- Subprocess execution
- Eval/exec/compile
- Import restrictions (socket, subprocess, etc.)

### Audit Function
```python
def audit_code(code: str) -> List[str]:
    # AST-based security checks
    # Returns list of violations
```

---

## 📦 Production Deployment

### Checklist
- [ ] Run `make ci` - all tests pass
- [ ] Set environment variables
- [ ] Configure daily snapshots: `make install-cron`
- [ ] Test Discord notifications
- [ ] Deploy dashboard to Replit
- [ ] Monitor drift bounds (max 5.0)
- [ ] Review locked parameters

### Deployment Command
```bash
# Build and start
npm run build
npm run start

# Or use Replit deployment
# Runs on port 5000 → forwards to 80/443
```

---

## 📚 Project Status

### Completed Phases (T01-T07)
- ✅ **T01** Foundation Core - AST synthesis engine
- ✅ **T02** Learning & Memory - Corpus + Seeds
- ✅ **T03** Adaptive Engine - ε-greedy exploration
- ✅ **T04** Production Hardening - CI/CD, Discord
- ✅ **T05** Spec DSL v3 - Multi-function specs
- ✅ **T06** Dashboard v2 - FastAPI + WebSocket
- ✅ **T07** Orchestrator - Autonomous monitoring

### Deferred
- ⏳ **T08** Telemetry/Chango - Feature-gated telemetry

---

## 🎯 Quick Start Examples

### Example 1: Simple Function
```bash
# Create spec
cat > specs/add.md << 'EOF'
# SpecV3: Add Two Numbers

def add(a: int, b: int) -> int

## Examples
add(2, 3) -> 5
add(-1, 1) -> 0
EOF

# Compile
python tools/spec_compile_v3.py specs/add.md

# Run tests
python -m unittest discover -s runs/run-*/tests
```

### Example 2: Multi-Function Spec
```bash
cat > specs/palindrome.md << 'EOF'
# SpecV3: Palindrome Checker

def check_palindrome(s: str) -> bool
def reverse_string(s: str) -> str

## Examples
check_palindrome("racecar") -> true
reverse_string("hello") -> "olleh"

## Post
assert check_palindrome(reverse_string(x) + x) == true
EOF

python tools/spec_compile_v3.py specs/palindrome.md
```

### Example 3: Watch Mode (Orchestrator)
```bash
# Start orchestrator in background
make orchestrate-bg

# Check logs
tail -f /tmp/aurora_orch.log

# Add/edit specs in /specs/ - auto-compiles!
```

---

## 🔧 Advanced Features

### 1. Baseline Comparison
```bash
# Compare against latest run
python -m aurora_x.main --baseline latest

# Compare against specific run
python -m aurora_x.main --baseline run-20251009-212532
```

### 2. Corpus Queries
```bash
# Dump corpus for signature
python -m aurora_x.main --dump-corpus "add(a:int,b:int)->int" --top 10

# With grep filter
python -m aurora_x.main --dump-corpus "add(a:int,b:int)->int" --grep "def add"

# JSON output
python -m aurora_x.main --dump-corpus "add(a:int,b:int)->int" --json
```

### 3. Progress Export
```bash
# Export to CSV
python tools/export_progress_csv.py

# Check for regressions
python tools/check_progress_regression.py

# Rollback progress
python tools/rollback_progress.py SNAPSHOT_ID
```

### 4. Discord Notifications
```python
from tools.notify_discord import success, warning, error

# Simple message
success("Synthesis complete!")

# With fields
warning("Drift warning", fields=[
    {"name": "Bias", "value": "0.45"},
    {"name": "Cap", "value": "0.50"}
])

# Commit alert
commit_alert(
    repo="aurora-x",
    branch="main",
    commit_url="https://...",
    files=5,
    message="feat: add palindrome spec"
)
```

---

## 🎨 Dashboard Features

### Live Monitoring
- Real-time run status
- Synthesis progress bars
- Bias evolution charts
- Function library browser
- Corpus similarity search

### WebSocket Updates
```javascript
// Auto-updates on:
- New run completion
- Test results
- Bias changes
- Progress updates
```

---

## 📝 File Formats

### 1. Spec File (Markdown)
```markdown
# SpecV3: Function Name

def func_name(param: type) -> return_type

## Examples
func_name(input) -> output

## Post
assert condition
```

### 2. Seeds File (JSON)
```json
{
  "biases": {
    "seed_key_1": 0.1234,
    "seed_key_2": -0.0567
  },
  "metadata": {
    "total_updates": 42,
    "config": {"alpha": 0.2, "drift_cap": 0.15}
  }
}
```

### 3. Progress File (JSON)
```json
{
  "phases": [
    {
      "id": "T01",
      "tasks": [
        {
          "id": "T01.1",
          "progress": 100,
          "subtasks": [...]
        }
      ]
    }
  ]
}
```

---

## 🐛 Troubleshooting

### Issue: Orchestrator not detecting changes
```bash
# Check if running
ps aux | grep orchestrator

# Restart
make orchestrate-bg

# Manual trigger
python tools/spec_compile_v3.py specs/your_spec.md
```

### Issue: Discord not sending
```bash
# Verify webhook
echo $DISCORD_WEBHOOK_URL

# Test notification
python tools/notify_discord.py
```

### Issue: Dashboard not updating
```bash
# Check server logs
make serve-v3

# Verify WebSocket connection
# Open browser console, look for WS errors

# Restart server
pkill -f "uvicorn"
make serve-v3
```

---

## 📖 References

### Key Files to Study
1. `aurora_x/main.py` - Main orchestration
2. `aurora_x/learn/adaptive.py` - Adaptive learning
3. `aurora_x/synthesis/search.py` - Synthesis engine
4. `tools/spec_compile_v3.py` - Spec compiler
5. `server/routes.ts` - API routes

### Documentation Files
- `README.md` - Quick start guide
- `PROJECT_SUMMARY.md` - Phase summary
- `AURORA_PRODUCTION_ROADMAP.md` - Roadmap
- `MASTER_TASK_LIST.md` - Task tracker
- `aurora_X.md` - Project notes

---

## 🏆 Best Practices

### 1. Writing Specs
- Clear function signatures with types
- Concrete examples (3-5 minimum)
- Post-conditions for invariants
- One concern per spec file

### 2. Managing Seeds
- Monitor drift via `/api/seed_bias`
- Prune periodically: `seed_store.prune()`
- Backup before experiments: `cp .aurora/seeds.json seeds.backup`

### 3. Production Deployment
- Lock production config
- Enable daily snapshots
- Monitor Discord alerts
- Set up Git auto-push
- Review CI gates daily

---

## 🔮 Future Enhancements (Post-T07)

### T08: Telemetry/Chango (Deferred)
- Feature-gated telemetry
- Local buffer with retry queue
- No code/PII transmission
- Opt-in via environment variable

### Potential Extensions
- Multi-language support (TypeScript, Rust)
- Distributed synthesis (parallel workers)
- ML-based mutation operators
- Visual spec builder UI
- Community corpus sharing (opt-in)

---

## 📄 License

MIT License - See LICENSE file

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Run `make ci` to validate
5. Submit pull request

---

## 📞 Support

- Issues: GitHub Issues
- Docs: This file + README.md
- Discord: Set webhook for alerts

---

**Aurora-X Ultra v1.1.0 - Autonomous Code Synthesis Engine**

*Offline-first • Secure-by-default • Learning-enabled*

---

## Appendix A: Complete Command Reference

### Synthesis Commands
```bash
# Basic synthesis
python -m aurora_x.main --spec-file SPEC.md

# With options
python -m aurora_x.main --spec-file SPEC.md --iterations 200 --timeout 600

# Disable features
python -m aurora_x.main --spec-file SPEC.md --no-corpus --no-seeds
```

### Corpus Commands
```bash
# Dump corpus
python -m aurora_x.main --dump-corpus "SIGNATURE" --top 10

# Filter results
python -m aurora_x.main --dump-corpus "SIGNATURE" --grep "PATTERN"

# JSON output
python -m aurora_x.main --dump-corpus "SIGNATURE" --json
```

### Progress Commands
```bash
# Update task
python -m aurora_x.main --update-task T01.1=100

# Bump progress
python -m aurora_x.main --bump T01.1=+5

# Auto-calculate
python -m aurora_x.main --update-task T01=auto
```

### Make Commands
```bash
make test              # Run all tests
make ci                # CI gate checks
make summary           # Update tracker
make drift             # Check task drift
make snapshot          # Take snapshot
make serve-v3          # Start dashboard
make orchestrate-bg    # Start orchestrator
make clean             # Clean generated files
```

---

## Appendix B: API Schema

### Seed Bias Endpoint
```
GET /api/seed_bias

Response:
{
  "summary": {
    "total_seeds": int,
    "avg_bias": float,
    "max_bias": float,
    "min_bias": float,
    "total_updates": int,
    "config": {...}
  },
  "top_biases": [
    {"seed_key": str, "bias": float}
  ]
}
```

### Adaptive Stats Endpoint
```
GET /api/adaptive_stats

Response:
{
  "summary": {
    "key1": float,
    "key2": float
  },
  "iteration": int
}
```

---

## Appendix C: Project Metrics

### Code Statistics
- **Total Files:** 40+
- **Lines of Code:** ~5,000+
- **Test Coverage:** Core modules tested
- **Languages:** Python, TypeScript, Bash

### Performance
- **Synthesis Speed:** ~10-50 attempts/minute
- **Corpus Size:** Unbounded (pruned periodically)
- **Memory Usage:** <100MB typical
- **Startup Time:** <2s

---

*End of Complete Project Documentation*
