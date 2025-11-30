
# Unused Things Folder - Detailed Categorization

## Analysis of Files in `unused things/`

### Category 1: Analysis & Documentation (Markdown Files)
**Purpose**: Technical analyses, blueprints, reports
**Action**: Move to `archive/experiments/docs/`

- Technical Blueprints → `archive/experiments/docs/technical/`
  - AURORA_TECHNICAL_BLUEPRINT.md
  - AURORA_NEXUS_V3_DRAFT_2_BEYOND_LIMITS.py (documentation in code)
  
- Analysis Reports → `archive/experiments/docs/analysis/`
  - AURORA_ARCHITECTURE_FIX.md
  - AURORA_AUTHENTICITY_ANALYSIS.md
  - AURORA_RAW_AUTHENTIC_ANALYSIS.md
  - AURORA_FULL_POWER_ANALYSIS.md
  - AURORA_FULL_POWER_STATUS.md
  
- Feature Previews → `archive/experiments/docs/previews/`
  - AURORA_ULTIMATE_NEXUS_V3_PREVIEW.md
  - AURORA_V3_20_SECOND_CHALLENGE_REPORT.md

### Category 2: Python Experimental Code
**Purpose**: Experimental implementations, prototypes
**Action**: Move to `archive/experiments/code/python/`

- Nexus Analysis → `archive/experiments/code/python/nexus/`
  - aurora_deep_nexus_analysis_hyper_speed.py
  
- Experimental Features → `archive/experiments/code/python/features/`
  - (Any .py files from unused things/)

### Category 3: TypeScript/JavaScript Experimental Code
**Purpose**: UI experiments, frontend prototypes
**Action**: Move to `archive/experiments/code/typescript/`

- UI Experiments → `archive/experiments/code/typescript/ui/`
- Backend Experiments → `archive/experiments/code/typescript/backend/`

### Category 4: Configuration Experiments
**Purpose**: Experimental configs, drafts
**Action**: Move to `archive/experiments/configs/`

- Docker configs → `archive/experiments/configs/docker/`
- CI/CD experiments → `archive/experiments/configs/cicd/`
- Environment configs → `archive/experiments/configs/env/`

### Category 5: Data & Assets
**Purpose**: Test data, experimental assets
**Action**: Move to `archive/experiments/data/`

- JSON data → `archive/experiments/data/json/`
- Images → `archive/experiments/data/images/`
- Other assets → `archive/experiments/data/assets/`

## Recommended Actions

### Keep in Main Tree:
- None from unused things (all are experimental or deprecated)

### Move to Archive:
- All files categorized above

### Can Delete (After Review):
- Duplicate files with .bak or .backup extensions
- Temporary test files
- Failed experiment files that have been superseded

## Detailed File-by-File Breakdown

```
unused things/
├── AURORA_TECHNICAL_BLUEPRINT.md           → archive/experiments/docs/technical/
├── AURORA_ULTIMATE_NEXUS_V3_PREVIEW.md     → archive/experiments/docs/previews/
├── AURORA_ARCHITECTURE_FIX.md              → archive/experiments/docs/analysis/
├── AURORA_AUTHENTICITY_ANALYSIS.md         → archive/experiments/docs/analysis/
├── AURORA_RAW_AUTHENTIC_ANALYSIS.md        → archive/experiments/docs/analysis/
├── AURORA_FULL_POWER_ANALYSIS.md           → archive/experiments/docs/analysis/
├── AURORA_FULL_POWER_STATUS.md             → archive/experiments/docs/analysis/
├── AURORA_V3_20_SECOND_CHALLENGE_REPORT.md → archive/experiments/docs/reports/
├── aurora_deep_nexus_analysis_hyper_speed.py → archive/experiments/code/python/nexus/
└── ... (other files as discovered)
```
