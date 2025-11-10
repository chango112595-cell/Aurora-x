<!-- AURORA_PROGRESS_BADGEs:START -->
<p align="center">
  <img alt="Overall Progress" src="https://img.shields.io/badge/Overall-92.69%25-7D5BFF?style=for-the-badge" />
  <img alt="Active" src="https://img.shields.io/badge/Active-T08,%20T10,%20T12-66E6FF?style=for-the-badge" />
  <img alt="Updated" src="https://img.shields.io/badge/Updated-2025-11-10T17%3A30%3A00Z-32325D?style=for-the-badge" />
</p>
<!-- AURORA_PROGRESS_BADGES:END -->

<h1 align="center">🌟 Aurora-X Ultra</h1>

<p align="center">
  <a href="https://github.com/chango112595-cell/Aurora-x/actions/workflows/aurora-main-ci.yml">
    <img alt="CI/CD Status" src="https://github.com/chango112595-cell/Aurora-x/actions/workflows/aurora-main-ci.yml/badge.svg" />
  </a>
  <a href="https://github.com/chango112595-cell/Aurora-x">
    <img alt="Coverage" src="https://raw.githubusercontent.com/chango112595-cell/Aurora-x/badges/badges/coverage.svg" />
  </a>
  <a href="https://github.com/chango112595-cell/Aurora-x/blob/main/LICENSE">
    <img alt="License" src="https://img.shields.io/badge/license-MIT-blue.svg" />
  </a>
  <a href="https://github.com/chango112595-cell/Aurora-x">
    <img alt="Production Ready" src="https://img.shields.io/badge/Production%20Ready-90%25-brightgreen" />
  </a>
</p>

<!-- BADGES-START -->
<p align="center">
  <img alt="Progress" src="https://img.shields.io/badge/Progress-90%25-brightgreen" />
  <img alt="Active Tasks" src="https://img.shields.io/badge/Active-CI/CD-blue" />
  <img alt="Last Updated" src="https://img.shields.io/badge/Updated-2025--11--10-lightgrey" />
  <img alt="Tasks" src="https://img.shields.io/badge/Tasks-✅11_🚀1_🔧0-informational" />
</p>
<!-- BADGES-END -->

<p align="center">
  <img alt="Seed Bias" src="https://img.shields.io/badge/seed__bias-dynamic-%23007acc?label=seed_bias&style=flat" />
  <img alt="Offline Mode" src="https://img.shields.io/badge/mode-offline--first-green?style=flat" />
  <img alt="Docker" src="https://img.shields.io/badge/docker-ready-2496ED?style=flat&logo=docker" />
  <img alt="Security" src="https://img.shields.io/badge/security-85%25-yellow?style=flat&logo=shield" />
</p>

<p align="center"><em>Offline Autonomous Code Synthesis Engine with Self-Learning & Backup Recovery</em></p>

---

## 🚀 Overview

Aurora-X is an autonomous code synthesis engine that uses AST-based mutations, beam search, and corpus-based seeding to synthesize functions from specifications. Aurora is **offline-first** — it records to JSONL/SQLite locally and never calls external APIs unless you enable explicit exports.

### ✨ Key Features

- 🧬 **AST-based synthesis** with beam search and intelligent mutations
- 💾 **Persistent corpus** in JSONL + SQLite format with automatic backup
- 🌱 **Seeding system** that learns from past successful synthesis patterns
- 📊 **Learning seeds** with EMA-based bias updates and drift caps
- 🔍 **Signature normalization** and TF-IDF fallback matching
- 🖥️ **CLI interface** for corpus queries and synthesis runs
- 🌐 **Web API** with seed bias tracking and real-time monitoring
- 🐳 **Docker containerization** with multi-architecture support
- 🔐 **Authentication & authorization** with JWT tokens
- 💾 **Automated backup & disaster recovery** with scheduled backups
- 🧪 **Comprehensive test suite** with 89+ passing tests
- 🔄 **CI/CD automation** with GitHub Actions

### 🏆 Production Readiness: 90%

Aurora-X is production-ready with:
- ✅ Docker containerization (multi-arch)
- ✅ Comprehensive test coverage
- ✅ Authentication system
- ✅ Automated backup & disaster recovery
- ✅ CI/CD automation
- 🔄 Monitoring and alerting (in progress)

---

## 📚 Documentation

- **[Building Workspace](BUILDING_WORKSPACE.md)** - Complete setup and build instructions
- **[Backup Guide](docs/BACKUP_GUIDE.md)** - Backup and restoration procedures
- **[Disaster Recovery](docs/DISASTER_RECOVERY.md)** - Emergency recovery procedures
- **[Architecture Decision](AURORA_ARCHITECTURE_DECISION.md)** - System architecture
- **[Knowledge Engine](AURORA_KNOWLEDGE_ENGINE_COMPLETE.md)** - AI knowledge system

---

## 🔧 Installation

For detailed setup instructions, see **[BUILDING_WORKSPACE.md](BUILDING_WORKSPACE.md)**.

### Quick Install

```bash
# Clone repository
git clone https://github.com/chango112595-cell/Aurora-x.git
cd Aurora-x

# Python setup
pip install -e .

# Node.js setup
npm install

# Docker setup (optional)
docker-compose up -d
```

### Requirements

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional)
- PostgreSQL 15+ (for production)

---

## 🎯 Usage

### Synthesis

```bash
# Run synthesis with seeding
aurorax --spec-file ./specs/rich_spec.md --outdir runs

# Run continuous self-learning
make self-learn

# Or run directly with custom parameters
python3 -m aurora_x.self_learn --sleep 300 --max-iters 50 --beam 20

# Query corpus for past synthesis attempts
aurorax --dump-corpus "add(a:int,b:int)->int" --top 5

# Quick check of bias without running synthesis
aurorax --show-bias --outdir runs
```

### Testing

```bash
# Run all tests
make test

# Run Python tests
pytest -v

# Run Node.js tests
npm test

# Run with coverage
pytest --cov=aurora_x --cov-report=html
```

### Docker

```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Backup & Recovery

```bash
# Backup database
./scripts/backup-database.sh

# Backup configuration
./scripts/backup-config.sh

# Full backup (database + config)
./scripts/backup-all.sh

# Restore from latest backup
./scripts/restore.sh --database --latest
./scripts/restore.sh --config --latest

# List available backups
./scripts/restore.sh --list
```

See **[docs/BACKUP_GUIDE.md](docs/BACKUP_GUIDE.md)** for complete backup documentation.

---

## 🌱 Learning Seeds

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
  "top_reasons": [
    {
      "reason": "loop_heavy",
      "bias": 0.4567,
      "count": 12
    }
  ]
}
```

---

## 🔐 Security

Aurora-X includes comprehensive security features:

- 🔑 JWT-based authentication
- 🛡️ Role-based access control (RBAC)
- 🔒 Password hashing with bcrypt
- 🚨 Security scanning with Bandit & Semgrep
- 📝 Audit logging
- 💾 Encrypted backups (recommended)

---

## 🤝 Contributing

Contributions are welcome! Please see our contribution guidelines.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📊 CI/CD

Aurora-X uses GitHub Actions for continuous integration and deployment:

- ✅ Automated testing (Python + Node.js)
- ✅ Code quality checks (Ruff, ESLint)
- ✅ Security scanning (Bandit, Semgrep)
- ✅ Coverage reporting with badges
- ✅ Docker multi-arch builds
- ✅ Automatic badge updates

See **[.github/workflows/aurora-main-ci.yml](.github/workflows/aurora-main-ci.yml)** for the complete CI/CD configuration.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with ❤️ by the Aurora team
- Powered by Python, Node.js, and Docker
- Inspired by modern AI synthesis techniques

---

<p align="center">
  <strong>Aurora-X Ultra</strong> - Autonomous Code Synthesis with Self-Learning
  <br>
  <em>Production-ready • Secure • Backed up • CI/CD enabled</em>
</p>
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

## Adaptive Learning Engine

Aurora-X includes an adaptive bias scheduler that combines exploitation and ε-greedy exploration to optimize synthesis performance over time.

### Features
- **ε-greedy exploration**: Balance between exploration (ε=0.15) and exploitation
- **Decay mechanism**: Per-iteration decay (0.98) for bias values
- **Cooldown periods**: Prevents immediate reuse of same bias (5 iterations)
- **Top-K tracking**: Maintains top 10 most significant biases
- **Visual sparklines**: Track bias evolution over time

### API Endpoints
```bash
# Get adaptive scheduler statistics
curl http://localhost:8080/api/adaptive_stats

# Get seed bias history
curl http://localhost:8080/api/seed_bias/history
```

## Project Status

### Phase Completion (T01–T07)
| Phase | Status | Description |
|-------|--------|-------------|
| **T01** | ✅ Complete | Foundation Core - AST synthesis engine |
| **T02** | ✅ Complete | Learning & Memory - Corpus recording |
| **T03** | ✅ Complete | Adaptive Engine - ε-greedy exploration |
| **T04** | ✅ Complete | Production Hardening - CI/CD, Discord |
| **T05** | ✅ Complete | Spec DSL v3 - Multi-function specs |
| **T06** | ✅ Complete | Dashboard v2 - FastAPI with WebSocket |
| **T07** | ✅ Complete | Orchestrator - Autonomous monitoring |

### Original Milestones
- ✅ **Milestone 1**: Core synthesis engine complete
- ✅ **Milestone 2**: Corpus recording and seeding implemented
- ✅ **Milestone 3**: Persistent learning seeds with EMA updates
- ✅ **Milestone 4**: Adaptive learning engine with ε-greedy exploration
- 🔜 **Next**: T08 Telemetry/Chango integration (deferred)

## 🚀 Autonomous Mode (T07) — Orchestrator

Aurora's orchestrator watches `/specs/*.md`, synthesizes code on changes/new specs, runs tests, updates the dashboard, and (optionally) pushes to GitHub and pings Discord.

### Quick Start
```bash
make orchestrator          # foreground loop
make orchestrate-bg        # daemon (logs: /tmp/aurora_orch.log)
make serve-v3 && make open-dashboard   # start UI and print URL
```

### Config (env / Replit Secrets)

| Var | Default | Notes |
|-----|---------|-------|
| `AURORA_ORCH_INTERVAL` | `300` | Poll interval (seconds) |
| `AURORA_GIT_AUTO` | `0` | Set `1` to enable auto-commit/push |
| `AURORA_GIT_URL` | — | e.g. `https://github.com/user/repo.git` |
| `AURORA_GIT_BRANCH` | `main` | Target branch |
| `DISCORD_WEBHOOK_URL` | — | Enables status alerts |

### Triggers
- New/changed spec in `/specs` (SHA256 change detection)
- First-run when no prior row exists in `runs/spec_runs.jsonl`

### Outputs
- `runs/run-YYYYMMDD-HHMMSS/{src,tests,report.html}`
- Dashboard row persisted in `runs/spec_runs.jsonl`
- Optional Git push (`aurora: spec run for <spec>`) + Discord embed

### One-tap v3 Spec Flow
```bash
make spec3-all SPEC3=specs/check_palindrome.md
```
