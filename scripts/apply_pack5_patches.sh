#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "Applying Pack5 wiring patches..."

# 1) ensure aurora_core in path and update orchestrator to optionally start operator dashboard and updater
# Insert import & thread start into aurora_core/orchestrator.py (if present)
ORI="$ROOT/aurora_core/orchestrator.py"
if [[ -f "$ORI" ]]; then
  grep -q "integration.dashboard.backend" "$ORI" || {
    echo "Patching orchestrator to start operator dashboard and updater service (dev only)"
    # append dev start snippet at end of file before main_loop exit
    cat >> "$ORI" <<'PY'
# --- Pack5 dev convenience: start operator dashboard and updater (dev only) ---
try:
    import threading
    def _start_aux_services():
        try:
            import integration.dashboard.backend as _db; threading.Thread(target=_db.run, daemon=True).start()
        except Exception:
            pass
        try:
            import integration.updater.updater_service as _up; threading.Thread(target=_up.run_server, daemon=True).start()
        except Exception:
            pass
    threading.Thread(target=_start_aux_services, daemon=True).start()
except Exception:
    pass
PY
  }
fi

echo "patches applied (double-check files)."
