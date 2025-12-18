# Aurora-X System Status and Fix Plan

## What’s Already Built
- **Full-stack runtime is defined and running** with Express + Vite on port 5000, a Python FastAPI Aurora Nexus V3 on 5002, and Luminar Nexus V2 Flask service on 8000, giving a working multi-service baseline.
- **Extensive module inventory** documented: 3,226+ Python modules across V3 core, packs, phase-1 production, tools, and hybrid/support layers, including 550 numbered modules and 10 category groups (analyzer, connector, formatter, generator, integrator, monitor, optimizer, processor, transformer, validator).
- **Pack, worker, and self-healing concepts** are specified with counts (15 packs, 300 workers, 100 active self-healers) and lifecycle patterns (init/execute/cleanup) covered in the integration guide, so the platform has clear contracts for module loading and execution.

## Known Gaps Blocking Production
- **Database is not provisioned** even though secrets exist; migration (`npx drizzle-kit push`) and switching to `DatabaseStorage` are pending.
- **Missing backend endpoints** used by the UI/monitoring:
  - `/api/bridge/comparison/aurora-runs` for the Comparison Dashboard.
  - `/api/self-healing/status` for health/telemetry.
- **Packs are simulated** because `aurora_nexus_v3/packs/` is absent; pack definitions should be added or the simulation documented.
- **Workers show no active tasks**: task dispatch/queue wiring in `universal_core` and `workers/worker.py` needs verification.
- **Luminar Nexus V2 coherence warning**: coherence should be floored (e.g., `max(0.5, new_coherence)`) to avoid dropping to zero.

## Quick Fix Sequencing
1. **Provision database & flip storage**
   - Use the provisioning tool to create PostgreSQL and sync `DATABASE_URL`.
   - Run `npx drizzle-kit push`; update `server/storage.ts` to use `DatabaseStorage` once verified.
2. **Restore critical endpoints** in `server/routes.ts` (and wire to real data later):
   - Add `/api/bridge/comparison/aurora-runs` returning structured comparison data.
   - Add `/api/self-healing/status` returning healer metrics (stub from Aurora Core acceptable initially).
3. **Reintroduce pack definitions**
   - Create `aurora_nexus_v3/packs/` with JSON descriptors for all 15 packs; update `server/nexus-v3-routes.ts` to read them.
   - If simulation remains, document it prominently in `replit.md`.
4. **Enable worker task flow**
   - Check `aurora_nexus_v3/core/universal_core.py` for dispatch logic and ensure it feeds the shared queue.
   - Confirm `aurora_nexus_v3/workers/worker.py` polls/executes tasks and reports metrics.
5. **Stabilize Luminar coherence**
   - In `tools/luminar_nexus_v2.py`, clamp coherence in `update_coherence` to prevent zero values and investigate decay triggers.

## Integration References
- Module lifecycle, registry paths, and loader usage are defined in the Module Integration Guide (e.g., `aurora_nexus_v3/module_loader.py`, `modules_registry.json`) to align new endpoints and worker dispatching with existing contracts.
- The complete codebase documentation lists all module categories, packs, and running services—use it as the source of truth when wiring packs/workers and exposing telemetry endpoints.
