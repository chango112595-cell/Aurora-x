# Aurora‑X Ultra — T07 Orchestrator (Autonomous Mode)

Aurora's orchestrator watches `/specs/*.md`, synthesizes code on changes/new specs, runs tests, persists run rows to `runs/spec_runs.jsonl`, updates `/dashboard/spec_runs`, optionally pushes to GitHub, and notifies Discord.

## Quick Start
```bash
make orchestrator          # foreground
make orchestrate-bg        # daemon (logs: /tmp/aurora_orch.log)
make open-dashboard        # print/open dashboard URL
```

## Configuration (env / Replit Secrets)
| Var | Default | Notes |
|-----|---------|------|
| `AURORA_ORCH_INTERVAL` | `300` | Poll interval (seconds) |
| `AURORA_GIT_AUTO` | `0` | `1` to enable auto-commit/push |
| `AURORA_GIT_URL` | — | e.g. `https://github.com/user/repo.git` |
| `AURORA_GIT_BRANCH` | `main` | Target branch |
| `DISCORD_WEBHOOK_URL` | — | Enables status alerts |

## Triggers
- New `.md` spec in `/specs`
- Any checksum change to an existing spec
- First-run (no prior row in `spec_runs.jsonl`)

## Outputs
- `runs/run-YYYYMMDD-HHMMSS/{src,tests,report.html}`
- `runs/spec_runs.jsonl` (dashboard rows)
- Optional Git push + Discord embed

## Safety
- Offline-first; Git/Discord gated by env.
- Generated code has no dynamic `eval/exec`, no external I/O.