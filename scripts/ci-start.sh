#!/usr/bin/env bash
set -euo pipefail

LOG=/tmp/aurora.log
PID=/tmp/aurora.pid
TARGETFILE=/tmp/aurora.target

# Candidate app targets to try in order
targets=(
  "aurora_x.serve:app"
  "server.main:app"
  "app.main:app"
)

function can_import() {
python - "$1" <<'PY'
import importlib, sys
t = sys.argv[1]
mod, attr = t.split(":")
m = importlib.import_module(mod)
a = getattr(m, attr, None)
assert a is not None, f"no attr {attr} in {mod}"
print("OK")
PY
}

for t in "${targets[@]}"; do
  echo "[ci-start] probing $t ..."
  if can_import "$t" >/dev/null 2>&1; then
    echo "[ci-start] launching uvicorn $t"
    nohup uvicorn "$t" --host 127.0.0.1 --port 8000 --log-level warning >"$LOG" 2>&1 &
    echo $! > "$PID"
    echo "$t" > "$TARGETFILE"
    exit 0
  fi
done

echo "[ci-start] no valid app target found" >&2
exit 1
