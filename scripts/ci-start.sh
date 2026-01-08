#!/usr/bin/env bash
set -euo pipefail
LOG=/tmp/aurora.log
PID=/tmp/aurora.pid
TARGET=/tmp/aurora.target

: > "$LOG"

echo "[ci] python: $(python -V 2>&1)" | tee -a "$LOG"
echo "[ci] pip: $(pip --version 2>&1)" | tee -a "$LOG"

candidates=(
  "aurora_x.serve:app"
  "aurora_nexus_v3.main:app"
  "app.main:app"
)

probe() { python - "$1" <<'PY'
import sys, importlib
t=sys.argv[1]
mod, attr = t.split(":")
m = importlib.import_module(mod)
a = getattr(m, attr, None)
assert a is not None
print("OK")
PY
}

chosen=""
for t in "${candidates[@]}"; do
  echo "[ci-start] probing $t ..." | tee -a "$LOG"
  if probe "$t" >/dev/null 2>&1; then chosen="$t"; break; fi
done

if [ -z "$chosen" ]; then
  echo "[ci-start] no valid FastAPI app target found" | tee -a "$LOG" >&2
  exit 1
fi

echo "[ci-start] launching uvicorn $chosen" | tee -a "$LOG"
nohup uvicorn "$chosen" --host 127.0.0.1 --port 8000 --log-level info >>"$LOG" 2>&1 &
echo $! > "$PID"
echo "$chosen" > "$TARGET"