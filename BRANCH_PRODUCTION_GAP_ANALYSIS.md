# Branch vs. Code Aurora Version - Production Readiness Gap

**Scope:** Compare the `gpt-codex-break` branch to the current Aurora production codebase and call out what must change for production readiness.

## What the branch adds
- Service management via `x-start*` / `x-stop` / `x-nexus` scripts.
- Centralized control paths (`tools/aurora_core.py`, `tools/aurora_launcher.js`) and autonomous helpers (auto-fixers, approval flow).
- Validation utilities (`validate_production_ready.py`, `verify_memory_fabric.py`) and Memory Fabric V2 artifacts.

## Gaps blocking production
1) **Secrets and history risk**
   - Branch history references commits with embedded secrets and `.ssl/key.pem` (see security warnings in the branch analysis report).
   - Default `JWT_SECRET` / `ADMIN_PASSWORD` values remain in `server/auth.ts` and `server/users.ts`.

2) **Architecture mismatch**
   - Tiers are the ranked capability taxonomy that drives manifests, validators, and orchestration routing.
   - Branch shifts to a 33-tier model while production baseline and validators expect 188 tiers (manifests/tiers.manifest.json).
   - The reduction trades coverage for speed but diverges from the validated set and would drop most validated domain coverage/weights.
   - Dual cores (`aurora_core.py` vs. `aurora_nexus_v3/core/hybrid_orchestrator.py`) need alignment to avoid divergent control paths.

3) **Non-production runtime paths**
   - `tools/luminar_nexus_v2.py` still advertises a development server.
   - Hardware runtimes (aviation/automotive/maritime/satellite) include stubs and should be gated or disabled without real hardware.

4) **Placeholders and mock wiring**
   - Generated connectors default to mock resources; cleanup modules are empty (`generated_modules/*_cleanup.py`).
   - Placeholder tokens/values in integration code (e.g., updater token, VIN placeholders) remain.

5) **Package/scripts alignment**
   - `package.json` includes new `x-*` scripts that are not yet wired into the existing supervisor/startup flows; needs a single authoritative entrypoint.

## Minimum actions to reach production-ready
- Purge secret-bearing commits/files from the branch (.ssl/key.pem, conversation JSON with embedded credentials, and similar patterns) via history rewrite (e.g., BFG or git filter-repo) with a coordinated force-push.
- Align with all collaborators before rewriting history because it will require fresh clones/resets.
- Rotate all affected secrets after the purge.
- Enforce real secrets via environment (`JWT_SECRET`, `ADMIN_PASSWORD`, DSNs) and remove hardcoded defaults.
- Restore/align manifests to the 188-tier baseline (or update validators/config to the chosen target).
- Reconcile orchestrator ownership between Aurora Core and Hybrid Orchestrator after the manifest decision.
- Run `validate_production_ready.py`, `test_production_integration.py`, and `aurora_nexus_v3/test_nexus.py` after harmonizing tiers/core to confirm counts and integrations.
- Keep x-start/x-stop automation.
- Integrate those scripts with the existing supervisor and the HybridOrchestrator hyperspeed mode switch so only one startup path governs services.
- Gate or stub-skip hardware runtimes in production builds until real hardware endpoints are provided.
- Replace mock connectors/cleanup stubs with no-op-safe or real implementations.
