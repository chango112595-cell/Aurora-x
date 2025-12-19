# Aurora Supervisor Knowledge Snapshots

The runtime files under `aurora_supervisor/data/knowledge/` (events and state snapshots) change continuously during execution and are intentionally ignored by Git to avoid constant noise.
This directory contains the tracked snapshots that you can commit.

Use `python scripts/snapshot_supervisor_knowledge.py` from the repo root once per day (or when a meaningful change occurs) to copy the latest runtime artifacts into this folder.

The script uses a 24-hour cooldown between tracked snapshots unless you pass `--force`.
It also records copies under `daily/` so you can inspect previous versions without committing every minor change.
