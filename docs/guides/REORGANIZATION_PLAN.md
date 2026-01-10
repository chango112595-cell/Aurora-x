
# Aurora-X Project Reorganization Plan

## Current State Analysis
- **Total Files**: ~2,926+ files
- **Core Systems**: Distributed across 4+ main directories
- **Unused Items**: Mixed in `unused things/` without categorization
- **Duplicates**: Multiple copies of core files in `aurora/core/` and `tools/`

## New Organized Structure

```
aurora-x/
├── core/                           # Aurora's Core Intelligence (188 Tiers)
│   ├── intelligence/               # Knowledge & Tier Systems
│   │   ├── tiers/                 # 188 Individual Tiers
│   │   ├── knowledge_engine.py    # Knowledge management
│   │   ├── expert_knowledge.py    # Expert systems
│   │   └── universal_expert.py    # Universal expertise
│   ├── execution/                  # 66 Execution Methods
│   │   ├── methods/               # Individual execution methods
│   │   ├── parallel_executor.py   # Parallel execution
│   │   ├── autonomous_system.py   # Autonomous execution
│   │   └── hyperspeed/            # Hyperspeed execution
│   ├── modules/                    # 500+ Modules organized by function
│   │   ├── synthesis/             # Code synthesis modules
│   │   ├── analysis/              # Analysis modules
│   │   ├── learning/              # Learning modules
│   │   ├── communication/         # Chat/conversation modules
│   │   └── ...                    # Other module categories
│   ├── orchestration/              # Nexus Systems
│   │   ├── nexus_v3/              # Universal Consciousness System
│   │   ├── nexus_v2/              # AI-Driven Orchestrator
│   │   └── bridge/                # Integration bridge
│   └── utilities/                  # Core utilities
│       ├── logger.py
│       ├── port_manager.py
│       └── health_monitor.py

├── aurora_x/                       # Aurora-X Ultra Engine (Keep as-is mostly)
│   ├── synthesis/                  # Code synthesis
│   ├── reasoners/                  # Math/Physics reasoners
│   ├── learn/                      # Self-learning
│   ├── bridge/                     # Python-TypeScript bridge
│   └── ...                         # Other aurora_x components

├── aurora_nexus_v3/               # Nexus V3 (Keep separate - it's standalone)
│   ├── core/
│   ├── modules/
│   └── ...

├── frontend/                       # All UI Components
│   ├── app/                       # Next.js app (if used)
│   ├── client/                    # React client
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   └── hooks/
│   │   └── public/
│   └── shared/                    # Shared schemas

├── backend/                        # All Backend Services
│   ├── server/                    # TypeScript backend
│   ├── api/                       # API endpoints
│   └── services/                  # Backend services

├── infrastructure/                 # DevOps & Infrastructure
│   ├── docker/                    # Docker configs
│   ├── scripts/                   # All scripts
│   ├── workflows/                 # GitHub Actions (move from .github/)
│   └── deployment/                # Deployment configs

├── docs/                          # All Documentation
│   ├── technical/                 # Technical blueprints
│   ├── guides/                    # User guides
│   ├── api/                       # API documentation
│   └── archive/                   # Historical docs

├── archive/                       # Organized Unused Items
│   ├── experiments/               # Failed experiments
│   │   ├── code/                 # Experimental code files
│   │   ├── configs/              # Experimental configs
│   │   └── docs/                 # Experimental documentation
│   ├── deprecated/                # Deprecated but keep for reference
│   │   ├── v1_systems/           # Old v1 systems
│   │   ├── old_ui/               # Deprecated UI components
│   │   └── legacy_modules/       # Legacy modules
│   ├── duplicates/                # Duplicate files (to review/delete)
│   ├── drafts/                    # Draft files and prototypes
│   └── backups/                   # Backup files

├── tests/                         # All Tests
│   ├── unit/
│   ├── integration/
│   └── e2e/

└── config/                        # All Configuration Files
    ├── development/
    ├── production/
    └── testing/
```

## Categorization of `unused things/` Folder

### By File Type:

1. **Python Files** (.py)
   - Analysis scripts → `archive/experiments/code/analysis/`
   - Debug tools → `archive/deprecated/debug_tools/`
   - Prototypes → `archive/drafts/prototypes/`

2. **Markdown Files** (.md)
   - Technical docs → `archive/experiments/docs/technical/`
   - Reports → `archive/experiments/docs/reports/`
   - Analyses → `archive/experiments/docs/analysis/`

3. **JSON Files** (.json)
   - Configuration experiments → `archive/experiments/configs/`
   - Data files → `archive/experiments/data/`

4. **TypeScript/JavaScript** (.ts, .tsx, .js)
   - UI experiments → `archive/experiments/code/ui/`
   - Backend experiments → `archive/experiments/code/backend/`

5. **Configuration Files**
   - Docker → `archive/experiments/configs/docker/`
   - CI/CD → `archive/experiments/configs/cicd/`

## Migration Steps

### Phase 1: Core Intelligence Consolidation (CRITICAL - Don't Break 188 Tiers)
1. ✅ Map all 188 tiers locations
2. ✅ Consolidate into `core/intelligence/tiers/`
3. ✅ Update import paths
4. ✅ Test tier access

### Phase 2: Execution Methods (CRITICAL - Don't Break 66 Methods)
1. ✅ Map all 66 execution methods
2. ✅ Consolidate into `core/execution/methods/`
3. ✅ Update import paths
4. ✅ Test execution dispatch

### Phase 3: Module Organization (CRITICAL - Don't Lose 500+ Modules)
1. ✅ Inventory all modules
2. ✅ Categorize by function
3. ✅ Move to `core/modules/[category]/`
4. ✅ Update module registry
5. ✅ Test module loading

### Phase 4: Nexus Systems (CRITICAL - Preserve Both)
1. ✅ Keep Nexus V3 separate (standalone system)
2. ✅ Move Nexus V2 to `core/orchestration/nexus_v2/`
3. ✅ Update routing
4. ✅ Test both systems

### Phase 5: Frontend Consolidation
1. ✅ Merge `app/` and `client/` into `frontend/`
2. ✅ Remove duplicate components
3. ✅ Update build configs

### Phase 6: Backend Consolidation
1. ✅ Organize `server/` files
2. ✅ Consolidate API routes
3. ✅ Update paths

### Phase 7: Infrastructure
1. ✅ Move scripts to `infrastructure/scripts/`
2. ✅ Move workflows to `infrastructure/workflows/`
3. ✅ Organize Docker files

### Phase 8: Archive Organization
1. ✅ Categorize `unused things/` by type
2. ✅ Move to appropriate archive folders
3. ✅ Create index of archived items

## File Preservation Checklist

### Must Keep (Core Aurora Systems):
- ✅ All 188 tier definitions
- ✅ All 66 execution methods
- ✅ All 500+ module files
- ✅ Nexus V3 (8 modules)
- ✅ Nexus V2 (luminar_nexus_v2.py)
- ✅ Hyperspeed engine
- ✅ Hybrid execution system
- ✅ Knowledge engine
- ✅ Learning systems
- ✅ Bridge systems
- ✅ All core intelligence files

### Can Consolidate (Remove Duplicates):
- Duplicate Aurora core files in `tools/` and `aurora/core/`
- Multiple copies of same UI components
- Redundant configuration files

### Can Archive:
- Failed experiments
- Deprecated UI versions
- Old documentation
- Backup files with .bak, .aurora_backup extensions

## Verification Tests

After reorganization, run these tests:
```bash
# Test all 188 tiers load
python -c "from core.intelligence.knowledge_engine import verify_all_tiers; verify_all_tiers()"

# Test all 66 execution methods
python -c "from core.execution import verify_all_methods; verify_all_methods()"

# Test module count
python -c "from core.modules import count_modules; assert count_modules() >= 500"

# Test Nexus V3
python aurora_nexus_v3/test_nexus.py

# Test Nexus V2
python -c "from core.orchestration.nexus_v2 import test_nexus_v2; test_nexus_v2()"

# Test hyperspeed
python -c "from core.execution.hyperspeed import test_hyperspeed; test_hyperspeed()"
```

## Next Steps

1. Review this plan
2. Confirm preservation of all critical systems
3. Execute reorganization in phases
4. Test after each phase
5. Update all documentation
