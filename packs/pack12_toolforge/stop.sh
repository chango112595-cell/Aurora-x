#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="${ROOT_DIR}/data/pack.pid"

if [[ ! -f "${PID_FILE}" ]]; then
  echo "[${ROOT_DIR##*/}] not running (no pid file)."
  exit 0
fi

PID="$(cat "${PID_FILE}")"
if kill -0 "${PID}" 2>/dev/null; then
  kill "${PID}"
  echo "[${ROOT_DIR##*/}] stopped (pid ${PID})."
else
  echo "[${ROOT_DIR##*/}] stale pid file found."
fi

rm -f "${PID_FILE}"
