# Aurora-x — Production Readiness Roadmap

This roadmap turns the AURORA_X_HANDOFF into an executable plan to take Aurora-x from prototype to production. It is organized as milestones with issue-sized tasks you can paste into GitHub.

---

## Milestone M0 — Repo Hygiene & CI (Week 0–1)
**Goal:** Green CI on PRs, reproducible local/CI runs (Replit-compatible), and secure-by-default.

- [ ] Adopt `.github/workflows/ci.yml` (unit + fast specs) and `nightly.yml` (full T01–T07).
- [ ] Add `pre-commit` with `black`, `ruff`, `isort`; run `pre-commit run -a` once.
- [ ] Add `CODEOWNERS`, PR/issue templates, and `CONTRIBUTING.md`.
- [ ] Enable branch protection on `main` (require CI + code review).
- [ ] Configure `Dependabot` and `CodeQL` alerts.
- [ ] Ensure `.replit` + `replit.nix` match project's entry points.
- [ ] Make targets: `spec-fast`, `pipeline`, `orchestrate-ci` (wrap existing commands).

**Definition of Done:** CI is green for Python {3.10, 3.11, 3.12}. Nightly emits artifacts: `logs/**`, `spec_runs/**`.

---

## Milestone M1 — Core Pipeline Stabilization (Week 1–2)
**Goal:** Deterministic, resumable T01–T07 with clear failure surfaces and artifacts.

- [ ] Define input/output contracts for T01–T07 (pydantic models or dataclasses).
- [ ] Add a pipeline runner with **idempotent steps** and step-level retries/backoff.
- [ ] Centralize config via `AURORA_*.env` (12‑factor; no secrets in code).
- [ ] Standardize logs (structured JSON) per step; write to `logs/{date}/step.log`.
- [ ] Artifact spec runs to `spec_runs/{date}/{run_id}/` (+ index.json).
- [ ] Introduce `@instrument` wrapper for timing/metrics (stdout-friendly for offline).
- [ ] Provide dry-run mode: `AURORA_DRY_RUN=1` skips external side effects.

**Definition of Done:** A single `make pipeline` runs end-to-end locally/Replit and in CI with reproducible artifacts.

---

## Milestone M2 — Testing & Quality Gates (Week 2–3)
**Goal:** Trustworthy changes; rapid PR feedback.

- [ ] Achieve 70%+ coverage on core modules (`orchestrator`, `synthesizer`, `mutator`, `evaluator`).
- [ ] Golden-tests for `spec` I/O fixtures (T01 ↔ T07) with small, deterministic corpora.
- [ ] Add **smoke E2E** test (fast path) to PR CI; full E2E saved for nightly.
- [ ] Static analysis: strict `ruff` ruleset + `mypy` (or pyright) on core modules.
- [ ] Introduce property-based tests for synthesizer mutations (e.g., `hypothesis`).

**Definition of Done:** PRs blocked unless unit + lint + type checks pass; coverage gate enforced on core packages.

---

## Milestone M3 — API & Client Hardening (Week 3–4)
**Goal:** Stable FastAPI service + minimal web client for operator workflows.

- [ ] FastAPI: versioned routes `/api/v1`, request validation, error mappers, timeouts.
- [ ] Health checks `/healthz` + `/readyz` and `/metrics` (if using Prometheus later).
- [ ] Rate-limits or concurrency controls around heavy steps.
- [ ] Client: minimal UX for submitting a spec, tracking a run, and viewing artifacts.
- [ ] CORS + security headers; disable docs in production unless authenticated.

**Definition of Done:** API contracts documented; client can create, inspect, and download a spec run's artifacts.

---

## Milestone M4 — Packaging & Releases (Week 4)
**Goal:** Reproducible builds and semantic versioning.

- [ ] Ensure `pyproject.toml` defines package metadata and console scripts (CLI entry).
- [ ] Enable **python-semantic-release** to tag releases + generate CHANGELOG on `main` merges.
- [ ] Pin minimal supported Python version; publish wheels to GitHub Releases artifacts.
- [ ] Build `aurora-x` CLI with commands: `say`, `spec`, `pipeline`, `inspect`.

**Definition of Done:** `feat:`/`fix:` to `main` → auto GitHub Release with changelog and artifacts.

---

## Milestone M5 — Operations, Observability & SRE (Week 4–5)
**Goal:** Operable in staging/production-like envs; quick triage.

- [ ] Central exception handler → uniform error codes and remediations.
- [ ] Structured logging fields: `run_id`, `step`, `duration_ms`, `status`, `error`.
- [ ] Add run limits (max steps, max time) and graceful shutdown.
- [ ] Redaction of PII/API keys in logs; secrets via env/CI only.
- [ ] CLI `aurora-x inspect` to summarize last N runs, errors, and artifacts.

**Definition of Done:** An operator can debug failures with a single inspect command and the log/artifact set.

---

## Issue Templates (Copy/Paste Into GitHub)

### :white_check_mark: Task
**Summary**
-

**Acceptance Criteria**
- [ ]

**Notes**
-

### :beetle: Bug
**Steps to Reproduce**
1.
2.

**Expected** / **Actual**
-

**Artifacts / Logs**
-

### :rocket: Feature
**Problem**
-

**Proposal**
-

**Risks / Open Questions**
-

---

## Make Targets (suggested)
```Makefile
# Fast PR path
spec-fast:
	AURORA_FAST=1 python -m aurora_x.cli spec --input samples/fast_spec.yaml

# Full nightly path
pipeline:
	AURORA_FULL=1 python -m aurora_x.cli pipeline --config configs/pipeline.yaml

# CI-friendly orchestrator (no TTY, strict exit codes)
orchestrate-ci:
	AURORA_CI=1 python -m aurora_x.cli orchestrate --non-interactive --fail-on-error
```

---

## Environment & Secrets
- `.env.example` with required `AURORA_*` variables (no secrets).
- GitHub Secrets for any tokens (if later needed): `AURORA_WEBHOOK_URL`, etc.
- Support `AURORA_GIT_AUTO=1` (optional) for auto-push after pipeline success.

---

## Acceptance Criteria for "Production-Ready"
- CI: green on PRs; nightly full pipeline succeeds 2 consecutive nights.
- Quality gates: lint, type-checks, coverage ≥ 70% core.
- Release: semantic-release creates version + changelog on `main` merges.
- Operability: artifacts + logs allow reproducing any run within 10 minutes.