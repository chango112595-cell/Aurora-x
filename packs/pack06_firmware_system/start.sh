#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="${ROOT_DIR}/data/pack.pid"
LOG_FILE="${ROOT_DIR}/data/pack.log"

mkdir -p "${ROOT_DIR}/data"

if [[ -f "${PID_FILE}" ]] && kill -0 "$(cat "${PID_FILE}")" 2>/dev/null; then
  echo "[${ROOT_DIR##*/}] already running (pid $(cat "${PID_FILE}"))."
  exit 0
fi

nohup python3 "${ROOT_DIR}/core/queue_worker.py" >> "${LOG_FILE}" 2>&1 &

echo $! > "${PID_FILE}"

echo "[${ROOT_DIR##*/}] started (pid $(cat "${PID_FILE}"))."
