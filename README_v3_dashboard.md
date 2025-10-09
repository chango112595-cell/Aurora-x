# Aurora-X Ultra v3 - FastAPI Dashboard Commands

## 🚀 Quick Start

### Using Makefile (if tabs work correctly):
```bash
make serve-v3          # Start FastAPI server
make open-dashboard    # Print & open dashboard URL
make spec3             # Compile a v3 spec
make spec3-all         # Full pipeline with Discord
```

### Using Shell Script (recommended):
```bash
./make_v3.sh - serve-v3         # Start FastAPI server
./make_v3.sh - open-dashboard   # Print & open dashboard URL
./make_v3.sh specs/check_palindrome.md spec3      # Compile spec
./make_v3.sh specs/fibonacci_sequence.md spec3-all # Full pipeline
```

## 🌌 Dashboard URL Detection

The `open-dashboard` command automatically detects your environment:

- **Local**: `http://localhost:5000/dashboard/spec_runs`
- **Replit**: `https://YOUR-REPL.YOUR-USERNAME.repl.co/dashboard/spec_runs`
- **Custom Port**: `PORT=8080 make open-dashboard`

## 📊 Dashboard Features

- **Live Updates**: WebSocket with 1.5s AJAX fallback
- **Persistent Logging**: All runs saved to `runs/spec_runs.jsonl`
- **Dark Futuristic UI**: JARVIS-inspired cyan theme
- **Pass/Fail Status**: Visual badges for each run
- **Bias Tracking**: Ready for EMA drift monitoring

## 🔧 One-Tap Mobile Launch

On Replit mobile:
1. Run: `make serve-v3` (starts server)
2. Run: `make open-dashboard` (opens in browser)

The dashboard URL is automatically constructed based on:
- `REPL_SLUG` and `REPL_OWNER` env vars (Replit)
- `PORT` env var (default: 5000)
- Falls back to localhost for local development

## 📝 Spec Compilation Pipeline

```bash
# Compile → Test → Discord Notify
make spec3-all SPEC3=specs/your_spec.md

# Or using script:
./make_v3.sh specs/your_spec.md spec3-all
```

Each run:
- Generates code in `runs/run-YYYYMMDD-HHMMSS/`
- Logs to `runs/spec_runs.jsonl`
- Sends Discord notification on success/failure
- Appears live on dashboard

## 🔌 API Endpoints

- `/` - API root with routes list
- `/dashboard/spec_runs` - Web dashboard
- `/api/spec_runs` - JSON API (last 50 runs)
- `/ws/spec_updates` - WebSocket for live updates

## 💾 Persistence

All runs are persisted to `runs/spec_runs.jsonl`:
```json
{
  "run_id": "run-20251009-231411",
  "spec": "check_palindrome.md",
  "ok": true,
  "report": "/runs/run-20251009-231411/report.html",
  "bias": null,
  "spark": null
}
```

Dashboard loads this file on startup, maintaining history across restarts.