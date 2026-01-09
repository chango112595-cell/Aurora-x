#!/usr/bin/env bash
set -euo pipefail
LOG=/tmp/aurora.log
PID=/tmp/aurora.pid
TARGET=/tmp/aurora.target

# Always create the files so artifact upload never comes back empty
: > "$LOG"
: > "$TARGET"

{
  echo "[ci] python: $(python -V 2>&1)"
  echo "[ci] pip: $(pip --version 2>&1)"

  candidates=(
    "aurora_x.serve:app"
    "aurora_nexus_v3.main:app"
    "app.main:app"
  )

  probe() { python - "$1" <<'PY'
import sys, importlib
t=sys.argv[1]; mod, attr = t.split(":")
m = importlib.import_module(mod)
a = getattr(m, attr, None)
assert a is not None, f"Attribute {attr!r} not found in {mod!r}"
print("OK")
PY
  }

  chosen=""
  for t in "${candidates[@]}"; do
    echo "[ci-start] probing $t ..."
    if probe "$t" >/devnull 2>&1; then chosen="$t"; break; fi
  done

  if [ -z "$chosen" ]; then
    echo "[ci-start] no valid FastAPI app target found" >&2
    echo "none" > "$TARGET"
    exit 1
  fi

  echo "$chosen" > "$TARGET"
  echo "[ci-start] launching uvicorn $chosen"
  nohup uvicorn "$chosen" --host 127.0.0.1 --port 8000 --log-level info >>"$LOG" 2>&1 &
  echo $! > "$PID"
} | tee -a "$LOG"