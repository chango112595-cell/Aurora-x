# Unused Folder

This folder contains archived files that are not actively used in the project.

## Purpose
- Archive old/deprecated code
- Store historical HTML files (now converted to TSX)
- Keep files for reference without cluttering the main project

## Contents
- `html_archive/` - Original HTML files (all converted to TSX)
  - Test reports from runs/
  - Old dashboards
  - Legacy frontend files

## Important
⚠️ This folder should NOT be imported or used by active code.
- Do not add this folder to build processes
- Do not import from this folder in active code
- Files here are for historical reference only

## Maintenance
- Can be safely deleted if disk space is needed
- Original HTML files have TSX equivalents in:
  - `client/src/` (working frontend)
  - `runs/*/` (test report TSX files)
