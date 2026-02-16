# What’s Missing from Aurora-X

**Purpose:** Single reference for gaps, placeholders, and incomplete areas in the Aurora-X AI development platform.
**Last updated:** 2026-02-05

---

## 1. Critical / Must-fix

### 1.1 Knowledge snapshot (corrupted in some paths)

- **What:** `aurora_supervisor/data/knowledge/state_snapshot.json` (or `models/state_snapshot.json`) can be empty or corrupt; load fails with `Expecting value: line 1 column 1`.
- **Where:** `aurora_supervisor/` knowledge loaders; some code expects valid JSON.
- **Impact:** Knowledge system may fail to init (often degraded gracefully).
- **Fix:** Regenerate snapshot (e.g. `scripts/snapshot_supervisor_knowledge.py`) or fix/remove corrupted files; ensure one canonical path and valid JSON.

### 1.2 Security: env and defaults

- **JWT_SECRET:** Required in `server/auth.ts` (server throws if unset). No default in auth code.
- **ADMIN_PASSWORD:** Required in `server/users.ts`; insecure defaults (e.g. `Alebec95!`) are rejected. `server/security-validator.ts` still references a default – ensure all code paths use env/secrets only.
- **Remaining:** Complete secret rotation per `scripts/SECRET_ROTATION_CHECKLIST.md` and runtime smoke tests per `scripts/RUNTIME_SMOKE_TEST.md` (P0 plan still pending).

### 1.3 Commands API import path

- **What:** `aurora_x` serve layer does `from aurora_unified_cmd import AuroraCommandManager`. Module exists at repo root (`aurora_unified_cmd.py`) but not on Python path when server runs from `aurora_x` or a subpackage.
- **Impact:** Commands API fails to load (gracefully handled); feature unavailable.
- **Fix:** Add repo root to `PYTHONPATH` when starting the Python server, or install the package so `aurora_unified_cmd` is importable.

### 1.4 Natural language → spec/code

- **What:** NL compilation depends on `spec_from_text` and `spec_from_flask` (in `tools/`). If they’re not on `PYTHONPATH`, imports fail and the feature falls back or errors.
- **Where:** `aurora_x/serve.py` (NL routes), `aurora_x/main.py`.
- **Impact:** “English to code” can fail or degrade when tools aren’t on path.
- **Fix:** Ensure `tools/` (or installed package) is on `PYTHONPATH` for the process that runs `aurora_x`/serve; document required env in BUILDING_WORKSPACE or README.

---

## 2. High priority (incomplete / placeholder)

### 2.1 RAG embeddings

- **What:** RAG uses a **local** embedding (TF-IDF-style in `server/rag-system.ts`). Comment says “Replace with local embedding model (Luminar/Memory Fabric)”.
- **Reality:** Current path is a production-safe fallback (no external API). Optional improvement: plug in Memory Fabric or another local embedder for better semantics.
- **Impact:** RAG works; quality is limited by TF-IDF-style embeddings.

### 2.2 Synthesis engine TODOs

- **Where:** `aurora_x/synthesis/universal_engine.py` – multiple TODOs for template/CRUD generation (e.g. GET/POST/PUT/DELETE for `/items`, processing/listing/reset, data loading).
- **Impact:** Core synthesis works; some generated templates or endpoints are stubs.

### 2.3 Intelligent refactor (Nexus V3)

- **Where:** `aurora_nexus_v3/refactoring/intelligent_refactor.py` – `_extract_method`, `_extract_variable`, `_rename`, `_simplify_conditional` return placeholders despite AST parsing.
- **Impact:** Refactor features are only partially implemented.

### 2.4 Advanced auto-fix

- **Where:** `aurora_nexus_v3/core/advanced_auto_fix.py` – TODO in fix generation; code does produce fixes but comment suggests incomplete logic.
- **Impact:** Auto-fix may not cover all cases.

### 2.5 Advanced tier manager

- **Where:** `aurora_nexus_v3/core/advanced_tier_manager.py` – “placeholder for optimization logic”.
- **Impact:** Tier optimization not fully implemented.

### 2.6 Hyperspeed mode

- **Where:** `aurora_nexus_v3/core/aurora_brain_bridge.py` (and related) – “1,000+ code units in &lt;0.001s” is largely logging; real processing pipeline for that throughput not fully wired.
- **Impact:** Hyperspeed is more “declared” than proven in production path.

### 2.7 550 generated modules – mock resources

- **What:** Many modules use `self.resource = conn or {'mock': True, 'cfg': cfg}`. Designed as templates/scaffolding.
- **Impact:** Modules load but don’t connect to real backends until configured; not a bug but a gap for “real” deployments.

### 2.8 66 Advanced Execution Methods (AEMs)

- **What:** Manifest defines 66 AEMs; not every method has full execution implementation in code.
- **Where:** `manifests/executions.manifest.json` vs actual runner/orchestrator code.
- **Impact:** Some execution strategies are manifest-only or stubbed.

### 2.9 300 workers – usage

- **What:** Worker pool and 300 workers exist; reports say they’re “idle” or not clearly driven by real task flow in all paths.
- **Impact:** Autonomous/worker-based features may be underused until routing and scheduling are fully exercised.

---

## 3. Deployment and ops

### 3.1 Hardcoded localhost

- **Where:** Several server clients use `localhost` / `127.0.0.1` (e.g. `server/notifications.ts`, `auth-integration.ts`, `aurora-nexus-bridge.ts`, `memory-client.ts`, `memory-fabric-client.ts`, `nexus-v3-client.ts`, `services/*`).
- **Impact:** Multi-host or non-local deployments need config (env/base URL) instead of hardcoded localhost.

### 3.2 Luminar Nexus V2 – dev server

- **Where:** `tools/luminar_nexus_v2.py` runs Flask dev server.
- **Impact:** Not suitable for production; should be run behind Gunicorn/uWSGI or equivalent in production.

### 3.3 Service startup order

- **What:** No explicit “wait for dependency X” before starting dependent services; order is best-effort.
- **Impact:** Occasional flakiness if a service starts before DB/Nexus/Bridge is ready.

### 3.4 Log rotation

- **What:** Log file management / rotation not implemented.
- **Impact:** Long-running instances can grow large log files.

### 3.5 Service discovery

- **What:** No formal service discovery (e.g. dynamic registry of Nexus/Bridge/Memory Fabric endpoints).
- **Impact:** Relies on env vars or static config; harder for dynamic or multi-node setups.

---

## 4. Edge and domain runtimes

- **Automotive / Aviation / Maritime / IoT / Router / Satellite / TV / Mobile:** Code or stubs exist; not all are integrated into the main request path or tested in CI.
- **Impact:** “Runs anywhere” is partially true; full integration and testing per domain are missing.

---

## 5. Vault and security depth

- **What:** Vault has basic encryption; docs mention a “22-layer” design (AES-GCM, ChaCha20-Poly1305, etc.).
- **Reality:** Current implementation is a smaller set; not all 22 layers present.
- **Impact:** Vault is usable but not at the documented “full” security depth.

---

## 6. Testing and quality

- **Test coverage:** Suite exists (e.g. 89+ tests); coverage percentage and which paths are exercised are not clearly documented.
- **Health check:** `aurora_x/api/health_check.py` has a TODO for “actual database check when PostgreSQL is set up” – DB connectivity may not be asserted in health.
- **Impact:** Confidence in “everything works” is limited until coverage and health checks are explicit.

---

## 7. Cleanup and debt

- **TODOs:** Hundreds of TODOs in `aurora_nexus_v3` and some in `server` and `aurora_x`; many are non-blocking but add debt.
- **Backup/old files:** Patterns like `*.aurora_backup`, `*_old*`, `*_backup*`; recommended to archive or remove.
- **Unused/experimental:** Large number of scripts/experiments (e.g. ask-aurora, fixers, one-off tools); could be moved to `archives/` or removed to reduce noise.

---

## 8. Summary table

| Area              | Status        | Notes                                              |
|-------------------|---------------|----------------------------------------------------|
| Knowledge snapshot| Broken (some) | Corrupt/empty JSON in some paths                   |
| Secrets/env       | Enforced      | JWT/ADMIN required; finish rotation + smoke tests   |
| Commands API      | Unavailable   | Fix PYTHONPATH / packaging for `aurora_unified_cmd` |
| NL compilation    | Fragile       | Depends on `spec_from_*` on path                  |
| RAG               | Working       | Local TF-IDF; optional: better embedder           |
| Synthesis engine  | Partial       | Core works; TODOs in universal_engine              |
| Refactor/Auto-fix | Placeholder   | Several methods stubbed in Nexus V3                |
| Hyperspeed        | Declared      | Real high-throughput path not fully proven        |
| 550 modules       | Scaffolding   | Mock resources by design                           |
| 66 AEMs           | Partial       | Manifest vs implementation gap                    |
| 300 workers       | Underused     | Routing/scheduling to be exercised                |
| Deployment        | Gaps          | Localhost, Flask dev server, startup order         |
| Edge runtimes     | Partial       | Not all integrated/tested                          |
| Vault             | Basic         | Not full “22-layer” design                        |
| Tests/health      | Incomplete    | Coverage and DB health check TODO                  |

---

## 9. Recommended order of work

1. **Security:** Finish secret rotation and runtime smoke tests (see `scripts/P0_SECURITY_COMPLETION_PLAN.md`).
2. **Knowledge:** Fix or regenerate `state_snapshot.json` and standardize path.
3. **Imports:** Fix Commands API and NL compilation by setting `PYTHONPATH` (or packaging) and documenting it.
4. **Synthesis:** Resolve high-value TODOs in `universal_engine.py` (e.g. CRUD and data-load paths).
5. **Deployment:** Replace localhost with config/base URLs; run Luminar behind a production WSGI server.
6. **Observability:** Add DB check to health endpoint; add log rotation; optionally add coverage reporting.

This document can be updated as items are fixed or re-prioritized.
