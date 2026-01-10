# 🧹 Aurora Cleanup Execution Plan - Complete Analysis & Action Plan

**Date:** January 10, 2026
**Status:** Pre-Execution Analysis Complete
**Goal:** Organize file tree, preserve important code, clean up safely

---

## 🎯 WHAT WE'RE TRYING TO ACHIEVE

### Primary Goals:
1. **Clean Root Directory** - Only essential files (README, configs, scripts)
2. **Organize Documentation** - All docs in `docs/` with clear structure
3. **Archive Old Files** - Move logs, zips, backups to `archives/`
4. **Preserve Important Code** - Don't lose useful code from experiments
5. **Remove Truly Unnecessary Files** - Delete only what's safe to delete
6. **Fix Organization** - Better file structure for maintenance

### Success Criteria:
- ✅ Root directory clean and organized
- ✅ All docs easily findable in `docs/`
- ✅ All archives properly categorized
- ✅ No broken references
- ✅ System still works perfectly
- ✅ Important code preserved

---

## 📊 COMPLETE ANALYSIS RESULTS

### 1. LOG FILES (27 files) - ANALYSIS COMPLETE

**Recent Logs (< 7 days) - KEEP:**
- `logs/services/aurora_bridge.log` (Jan 10, 0.07 MB) ✅ KEEP
- `logs/aurora-heal.log` (Jan 10, 0.01 MB) ✅ KEEP
- `logs/services/aurora_nexus_v3.log` (Jan 10, 2.32 MB) ✅ KEEP
- `logs/x-start/*.log` (Jan 10, multiple files) ✅ KEEP

**Old Logs (7-30 days) - ARCHIVE:**
- `e2e-logs/*.log` (Jan 8-9, multiple files) → `archives/logs/e2e/`
- `main-e2e-*.log` (Jan 8, 0.06 MB) → `archives/logs/e2e/`
- `e2e-*.log` (Jan 8, multiple files) → `archives/logs/e2e/`

**Very Old Logs (> 30 days) - DELETE:**
- `aurora_self_healing_execution.log` (Nov 25, 0.29 MB) ❌ DELETE
- `aurora_ui_redesign.log` (Nov 22, 0.00 MB) ❌ DELETE
- `aurora_learning.log` (Nov 21, 0.03 MB) ❌ DELETE
- `aurora_docker_healing.log` (Nov 18, 0.00 MB) ❌ DELETE
- `luminar_v2_error.log` (Nov 16, 0.00 MB) ❌ DELETE
- `luminar_v2.log` (Nov 16, 0.00 MB) ❌ DELETE
- `logs/aurora-*.log` (Nov 21, multiple files) ❌ DELETE
- `.aurora_knowledge/autonomous_monitoring_*.log` (Nov 22-29) ❌ DELETE

**Action:** Archive 7-30 day logs, delete >30 day logs, keep recent logs

---

### 2. ZIP ARCHIVE FILES (14 files) - ANALYSIS COMPLETE

**Recent Archives (< 30 days) - ARCHIVE:**
- `aurora_phase1_production/aurora_x.zip` (Jan 8, 0.94 MB) → `archives/zips/production/`
- `tools/aurora_fixes_script.zip` (Jan 8, 0.00 MB) → `archives/zips/tools/`
- `aurora_hybrid_system.zip` (Jan 8, 0.02 MB) → `archives/zips/systems/`
- `aurora_modules_final_build_20251209_124336.zip` (Jan 8, 2.35 MB) → `archives/zips/modules/`
- `aurora_modules_v3_integration.zip` (Jan 8, 1.36 MB) → `archives/zips/modules/`
- `docker.zip` (Jan 8, 0.01 MB) → `archives/zips/docker/`

**Project Run Archives (KEEP in runs/) - These are system-generated:**
- `aurora_x/runs/*/project.zip` (multiple, small) ✅ KEEP (system data)
- `runs/*/project.zip` (multiple, small) ✅ KEEP (system data)

**Action:** Move root-level zips to `archives/zips/`, keep `runs/` zips

---

### 3. BACKUP/COMPARISON FILES (8 files) - ANALYSIS COMPLETE

**Backup Analysis Reports - ARCHIVE:**
- `AURORA_BACKUP_ANALYSIS_REPORT.txt` (Jan 8) → `archives/backups/analysis/`
- `AURORA_BACKUP_COMPARISON_REPORT.json` (Jan 9) → `archives/backups/analysis/`
- `AURORA_BACKUP_COMPARISON_REPORT.txt` (Jan 9) → `archives/backups/analysis/`
- `AURORA_BACKUP_COMPARISON_SUMMARY.txt` (Jan 8) → `archives/backups/analysis/`
- `AURORA_BACKUP_COMPARISON_SYMBOLS.json` (Jan 9) → `archives/backups/analysis/`
- `AURORA_BACKUP_REVIEW_TARGETS.txt` (Jan 8) → `archives/backups/analysis/`
- `AURORA_IDENTICAL_BACKUP_CONSOLIDATION_REPORT.txt` (Jan 9) → `archives/backups/analysis/`
- `AURORA_ATTACHED_ASSETS_IDENTICAL_BACKUP_CONSOLIDATION_REPORT.txt` (Jan 8) → `archives/backups/analysis/`

**System State Files - KEEP:**
- `aurora/knowledge/TEST_BACKUP_RESTORE_SYSTEM.completed` ✅ KEEP (system state)
- `aurora/knowledge/IMPLEMENT_BACKUP_DISASTER_RECOVERY.completed` ✅ KEEP (system state)

**Action:** Move backup reports to `archives/backups/analysis/`, keep system state files

---

### 4. DOCUMENTATION FILES (100+ files) - NEEDS ORGANIZATION

**Categories Identified:**

**Analysis Reports (30+ files):**
- `AURORA_*.md` files → `docs/analysis/`
- `PRODUCTION_*.md` files → `docs/analysis/production/`
- `NEXUS_*.md` files → `docs/analysis/nexus/`

**User Guides (10+ files):**
- `HOW_TO_*.md` → `docs/guides/`
- `START_*.md` → `docs/guides/startup/`
- `QUICK_START.md` → `docs/guides/`

**Architecture Docs (15+ files):**
- `*_ARCHITECTURE*.md` → `docs/architecture/`
- `*_BRIDGE*.md` → `docs/architecture/bridges/`

**Integration Docs (10+ files):**
- `*_INTEGRATION*.md` → `docs/integration/`
- `*_WIRING*.md` → `docs/integration/wiring/`

**Status Reports (20+ files):**
- `*_STATUS.md` → `docs/status/`
- `*_SUMMARY.md` → `docs/status/summaries/`
- `*_COMPLETE.md` → `docs/status/completion/`

**Duplicates to Consolidate:**
- `NO_SCAFFOLDING_VERIFICATION.md` vs `NO_SCAFFOLDING_VERIFIED.md` → Keep one
- `PRODUCTION_READINESS_100_PERCENT.md` vs `PRODUCTION_READINESS_FINAL.md` vs `PRODUCTION_READY_SUMMARY.md` → Keep latest
- `HOW_TO_START_AURORA.md` vs `START_AURORA_WINDOWS.md` vs `START_AURORA.md` → Consolidate

**Action:** Organize into `docs/` subdirectories, consolidate duplicates

---

### 5. FAILED EXPERIMENTS - PRESERVATION CHECK

**From FAILED_EXPERIMENTS_ARCHIVE.md:**
- 370+ Python scripts (failed experiments)
- 48 shell scripts (failed experiments)
- 179 markdown reports (analysis without execution)
- 20+ directories (failed experiments)

**Decision:**
- ✅ **PRESERVE:** Useful code patterns, algorithms, utilities
- ✅ **ARCHIVE:** Move to `archives/experiments/` with categorization
- ✅ **DOCUMENT:** What was tried, why it failed, what was learned
- ❌ **DELETE:** Truly broken code with no value (after review)

**Action:** Review experiments, preserve useful code, archive rest

---

### 6. DUPLICATE FILES - VERIFICATION NEEDED

**Potential Duplicates:**
- `.aurora/config.yml` vs `aurora_x/.aurora/config.yml` → Fixed typo, need to check if both needed
- Multiple `aurora_core.py` files → Check if different versions
- Multiple startup scripts → Check which is current

**Action:** Compare duplicates, merge if different, delete if identical

---

## 🚀 EXECUTION PLAN (Step-by-Step)

### PHASE 1: CREATE DIRECTORY STRUCTURE (Safe - No Deletions)

**Step 1.1: Create Archive Directories**
```bash
archives/
├── logs/
│   ├── e2e/
│   └── old/
├── zips/
│   ├── production/
│   ├── tools/
│   ├── systems/
│   ├── modules/
│   └── docker/
├── backups/
│   └── analysis/
└── experiments/
    ├── code/
    ├── docs/
    └── configs/
```

**Step 1.2: Create Documentation Structure**
```bash
docs/
├── analysis/
│   ├── production/
│   └── nexus/
├── guides/
│   └── startup/
├── architecture/
│   └── bridges/
├── integration/
│   └── wiring/
└── status/
    ├── summaries/
    └── completion/
```

**Step 1.3: Create Log Archive Directory**
```bash
logs/
└── archive/
    ├── e2e/
    └── old/
```

---

### PHASE 2: MOVE FILES (Safe - No Deletions Yet)

**Step 2.1: Archive Old Logs**
- Move logs 7-30 days old to `archives/logs/e2e/`
- Move logs >30 days old to `archives/logs/old/` (for review before deletion)

**Step 2.2: Move Zip Files**
- Move root-level zips to `archives/zips/` by category
- Keep `runs/` zips (system data)

**Step 2.3: Move Backup Files**
- Move backup reports to `archives/backups/analysis/`
- Keep system state files in `aurora/knowledge/`

**Step 2.4: Organize Documentation**
- Move docs to `docs/` by category
- Keep essential docs in root (README.md, etc.)

---

### PHASE 3: CONSOLIDATE DUPLICATES (Careful Comparison)

**Step 3.1: Compare Duplicate Docs**
- Compare `NO_SCAFFOLDING_VERIFICATION.md` vs `NO_SCAFFOLDING_VERIFIED.md`
- Compare production readiness docs
- Compare startup guides

**Step 3.2: Merge or Delete**
- If identical → Delete duplicate
- If different → Merge content, keep best version
- If both needed → Rename for clarity

---

### PHASE 4: CLEANUP (After Verification)

**Step 4.1: Delete Very Old Logs**
- Delete logs >90 days old (after verification)
- Keep recent logs for debugging

**Step 4.2: Archive Failed Experiments**
- Move failed experiments to `archives/experiments/`
- Preserve useful code patterns
- Document learnings

**Step 4.3: Remove Truly Unnecessary Files**
- Delete broken/incomplete code with no value
- Delete duplicate files (after comparison)
- Delete outdated docs (after consolidation)

---

### PHASE 5: VERIFICATION & DOCUMENTATION

**Step 5.1: Verify System**
- Test that system still works
- Check for broken references
- Verify no code depends on moved files

**Step 5.2: Update Documentation**
- Create `docs/README.md` with navigation
- Update `.gitignore` if needed
- Document cleanup actions

**Step 5.3: Create Index**
- Create `CLEANUP_COMPLETE.md` report
- Document what was moved/deleted
- Create file organization guide

---

## ⚠️ SAFETY CHECKS (Before Each Action)

### Before Moving Files:
- ✅ Check if file is referenced in code
- ✅ Check if file is referenced in docs
- ✅ Verify file is not system-critical
- ✅ Check file timestamps

### Before Deleting Files:
- ✅ Verify file is truly unnecessary
- ✅ Check if file contains unique code/data
- ✅ Ensure file is not referenced anywhere
- ✅ Double-check file purpose

### Before Consolidating:
- ✅ Compare files to ensure they're duplicates
- ✅ Verify which version is most current
- ✅ Check if both versions have unique content
- ✅ Merge carefully if different

---

## 📋 DETAILED FILE INVENTORY

### Logs to Keep (< 7 days):
- `logs/services/aurora_bridge.log` ✅
- `logs/aurora-heal.log` ✅
- `logs/services/aurora_nexus_v3.log` ✅
- `logs/x-start/*.log` ✅

### Logs to Archive (7-30 days):
- `e2e-logs/*.log` → `archives/logs/e2e/`
- `main-e2e-*.log` → `archives/logs/e2e/`
- `e2e-*.log` → `archives/logs/e2e/`

### Logs to Delete (> 30 days):
- `aurora_self_healing_execution.log` ❌
- `aurora_ui_redesign.log` ❌
- `aurora_learning.log` ❌
- `aurora_docker_healing.log` ❌
- `luminar_v2_error.log` ❌
- `luminar_v2.log` ❌
- `logs/aurora-*.log` (Nov 21) ❌
- `.aurora_knowledge/autonomous_monitoring_*.log` ❌

### Zips to Archive:
- `docker.zip` → `archives/zips/docker/`
- `aurora_hybrid_system.zip` → `archives/zips/systems/`
- `aurora_modules_v3_integration.zip` → `archives/zips/modules/`
- `aurora_modules_final_build_20251209_124336.zip` → `archives/zips/modules/`
- `tools/aurora_fixes_script.zip` → `archives/zips/tools/`
- `aurora_phase1_production/aurora_x.zip` → `archives/zips/production/`

### Zips to Keep:
- `runs/*/project.zip` ✅ (system data)
- `aurora_x/runs/*/project.zip` ✅ (system data)

### Backup Files to Archive:
- All `AURORA_BACKUP_*.txt` → `archives/backups/analysis/`
- All `AURORA_BACKUP_*.json` → `archives/backups/analysis/`

### Backup Files to Keep:
- `aurora/knowledge/*.completed` ✅ (system state)

---

## ✅ READY TO EXECUTE

**Status:** ✅ Analysis Complete
**Next Step:** Begin Phase 1 - Create directory structure
**Safety:** All actions are reversible (move before delete)

---

**Last Updated:** January 10, 2026
**Status:** Ready for Execution
