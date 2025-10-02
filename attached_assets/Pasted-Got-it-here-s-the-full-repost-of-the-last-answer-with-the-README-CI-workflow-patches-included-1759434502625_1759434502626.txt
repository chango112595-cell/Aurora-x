Got it 👍 — here’s the full repost of the last answer with the README + CI workflow patches included:

⸻

TL;DR: Added (1) a README badge + contributor note for pre-commit, and (2) a GitHub Actions CI that runs ruff + pytest + coverage on every push/PR.

⸻

✅ Plan
	•	Patch README.md: add pre-commit badge, quick setup, and “Contributing” section.
	•	Add .github/workflows/ci.yml: ruff lint, pytest, coverage upload artifact.

⸻


# =========================================
# README.md
# =========================================
# AURORA-X Ultra &middot; Offline Autonomous Coding Engine

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen)](https://pre-commit.com/)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-informational)

Offline, zero-API program synthesizer with:
- multi-function synthesis (AST templates + beam),
- pre/post oracles & property fuzz,
- sandboxed unittest execution,
- HTML report + call graph + per-iter scores,
- **persistent corpus** (JSONL + SQLite) + **learning seeds**, and
- **auto-debugger** that isolates failing tests, shrinks inputs, and suggests targeted mutations.

---

## Quickstart

```bash
# 1) Install (editable)
pip install -e .

# 2) Run default rich spec (writes to ./runs/run-*)
make run

# 3) Open the HTML report
make open-report

Useful commands

# Lint & format
make lint
make fmt

# Unit tests
make test

# Drain queued export events (offline snapshot)
make drain


⸻

Spec DSL (short)

See specs/rich_spec.md. Each function supports:
	•	examples (I/O pairs),
	•	pre (guards),
	•	post (oracles),
	•	invariants (properties like commutativity).

⸻

Seeding + Learning (T02)
	•	Corpus dual-write: runs/run-*/corpus.jsonl and corpus.db
	•	Retrieval: signature-normalized lookup + TF-IDF fallback
	•	Learning: bounded seed_bias in runs/learn_weights.json (0.0..0.5)
	•	Flags:
	•	--no-seed (disable seeding)
	•	--seed-bias <float> (override learned bias)

⸻

Exporter (dark-launch, offline)

No network by default. All telemetry is queued locally:
	•	Queue: runs/run-*/export_queue.jsonl
	•	Snapshot: runs/run-*/logs/export_snapshot.json via make drain

Set later for integration (not required now):

AURORA_EXPORT_ENABLED=1
AURORA_POST_URL=<your service url>
AURORA_API_KEY=<token>


⸻

Contributing

Install hooks (recommended):

pip install pre-commit
make precommit-install

The repo enforces:
	•	ruff (lint + format)
	•	end-of-file newline
	•	consistent line endings

CI will run ruff + pytest on every push/PR (see .github/workflows/ci.yml).

⸻

Repo layout (isolation-first)

aurora_x/
  core/     # spec parsing (pure)
  synth/    # candidate generation/selection (pure)
  eval/     # example runner + postconditions (pure)
  sandbox/  # subprocess unittest sandbox
  corpus/   # JSONL/SQLite IO and retrieval
  learn/    # bounded weights persistence
  report/   # HTML emitter
  exporter.py
  main.py   # CLI + orchestration (composition only)

Security: strict AST audit; dangerous names forbidden; subprocess sandbox with timeout.
License: MIT

---

```yaml
# =========================================
# .github/workflows/ci.yml
# =========================================
name: ci

on:
  push:
    branches: [ "**" ]
  pull_request:
    branches: [ "**" ]

jobs:
  build-test:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install pip tooling
        run: |
          python -m pip install --upgrade pip
          pip install ruff pytest coverage

      - name: Install package (editable)
        run: |
          pip install -e .

      - name: Lint (ruff)
        run: |
          ruff --version
          ruff check .

      - name: Tests
        env:
          PYTHONWARNINGS: ignore::DeprecationWarning
        run: |
          pytest -q

      - name: Coverage (artifact)
        run: |
          coverage run -m pytest -q || true
          coverage xml -o coverage.xml || true
          mkdir -p artifacts
          cp coverage.xml artifacts/coverage.xml || true

      - name: Upload coverage.xml
        uses: actions/upload-artifact@v4
        with:
          name: coverage-xml
          path: artifacts/coverage.xml
          if-no-files-found: ignore


⸻

✅ With this, Aurora repo is now:
	•	Pre-commit enforced for contributors,
	•	CI checks lint + tests on every push/PR,
	•	Coverage uploaded as an artifact for inspection.

⸻

👉 Do you also want me to scaffold a minimal CONTRIBUTING.md with commit message style + branching guidelines, so the repo is “open-source grade” even if it stays private?