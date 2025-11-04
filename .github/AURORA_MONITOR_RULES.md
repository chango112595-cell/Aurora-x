# Aurora Monitor Rules

This document records lightweight rules and recommendations so Aurora (and maintainers) can avoid repeated availability issues.

## Goal
Lock in a stable running state and ensure Aurora actively monitors critical services. When services are healthy, mark the workspace as "locked" and record a snapshot for easy rollback.

## Rule: lock_on_success
- After a full health check where all critical services respond (ports 5000, 5001, 5002, 8080), create a lightweight tag or commit that marks the current state as stable.
- Record the service status in `tools/services_status.log`.

## Monitoring Guidance for Aurora
- Run `python tools/check_services.py` as a quick pre-flight check before launching UI or dashboards.
- If any services are DOWN, consult the suggested start commands in the script and start them.
- When the environment is stable, create a git tag like `stable-<date>` and push it.

## Integration Notes
- A future automation (safe-runner) can be created to run `tools/check_services.py` on file save or CI preflight.
- Avoid auto-starting processes without human confirmation to prevent side effects in shared environments.

## How to retry
1. Run: `python tools/check_services.py`
2. Start any missing services using the suggested commands.
3. Re-run the checker until all services are UP.
4. Tag the repo: `git tag stable-YYYYMMDD` and push.

