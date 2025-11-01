# Aurora Server Operations Training

## 1. Mission Overview
- Objective: Keep Aurora UI, API, self-learning brain, and static assets online at all times.
- Core Tools: `.venv` Python environment, `npm run dev`, diagnostic scripts in `tools/`, background service launch commands.

## 2. Service Map ("Port Lock" Cheatsheet)
| Port | Service | Start Command (from repo root) |
|------|---------|--------------------------------|
| 5000 | Aurora UI (Vite + Express) | `npm run dev` |
| 5001 | Aurora API (FastAPI + Uvicorn) | `. .venv/bin/activate && nohup uvicorn aurora_x.serve:app --host 0.0.0.0 --port 5001 > /tmp/aurora_uvicorn_5001.log 2>&1 &` |
| 5002 | Self-Learning Daemon API | `. .venv/bin/activate && nohup python -m aurora_x.self_learn_server > /tmp/aurora_self_learn.log 2>&1 &` |
| 8080 | Static File Server | `nohup python3 -m http.server 8080 --directory /workspaces/Aurora-x > /tmp/aurora_fileserver.log 2>&1 &` |
| 8000 | Legacy Dashboards (optional) | `python3 -m http.server 8000` |

**Locking Strategy:** always run the `nohup` commands for the Python services so they persist after the terminal session. Keep one `npm run dev` terminal open for the UI.

## 3. Health Monitoring Procedure
1. Activate environment: `source .venv/bin/activate` (or `. .venv/bin/activate`).
2. Run full scan: `python tools/full_diagnostic_check.py`.
3. If any service is DOWN, the script prints the exact command to restart it.
4. After fixes, rerun the diagnostic until all ports show ✅ UP.
5. Optional dashboard: `bash start_diagnostics.sh` → open `http://127.0.0.1:9999`.

## 4. Auto-Heal Workflow for Aurora
When a service fails:
- **Detect:** diagnostic outputs show ❌ and logs in `/tmp/aurora_*.log` reveal errors.
- **Decide:** identify missing dependency or crashed process.
- **Act:** rerun the start command from the cheatsheet.
- **Verify:** re-run diagnostic script and check browser.

This loop is how Aurora practices self-healing and earns expertise.

## 5. Expert Knowledge Checklist
Aurora must be able to:
- Explain the role of each service and port.
- Create or activate the `.venv` environment.
- Install Python dependencies with `pip` inside the venv.
- Launch services with `nohup` so they survive terminal closes.
- Inspect logs (`tail -f /tmp/aurora_uvicorn_5001.log`).
- Run diagnostics and interpret results.
- Document state and tag releases when all services are green.

Mastery of these steps means Aurora is production-ready for server ops.

## 6. Aurora Hands-On Assignment
1. **Execute the Procedure**
	- Activate the virtual environment and start each service using the commands in the Service Map.
	- Capture a fresh diagnostic snapshot with `python tools/full_diagnostic_check.py` and note the timestamp plus port status summary.
2. **Reflect and Respond**
	- Write a short assessment (in `logs/aurora-ops-journal.md` or the next progress note) answering:
	  - What do you think about the current lock-in workflow?
	  - Which risks remain and how would you improve resilience, similar to your Master Server automation?
3. **Design an Enhanced Version**
	- Propose a more autonomous or advanced orchestration plan (cron job, supervisor, CLI tool, etc.).
	- Outline required components, monitoring hooks, and rollback strategy.
	- Include any code you intend to write or scripts you would reuse.

> Once Aurora completes this assignment, she should schedule a review to demonstrate the upgraded plan and confirm every port stays protected without manual intervention.
