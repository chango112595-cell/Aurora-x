aurora_auto_fix script bundle
=============================

This bundle contains a best-effort automated fixer script for the Aurora-X repo.

Files included:
- aurora_auto_fix.py  : the fixer script
- README.txt          : this document (how to use, limitations)

IMPORTANT: This script performs textual fixes and heuristics. Always review changes, test, and run your test-suite after running it. The script creates backups for every modified file with the suffix '.aurora_backup'.

Usage Example:
  cd /path/to/Aurora-x
  python3 /path/to/aurora_auto_fix.py --dry-run
  python3 /path/to/aurora_auto_fix.py