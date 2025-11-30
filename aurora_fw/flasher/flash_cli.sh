#!/usr/bin/env bash
set -euo pipefail
PY="$(command -v python3 || echo python)"
case "$1" in
  stage)
    axf="$2"; target_type="$3"; reason="$4"
    $PY -c "from aurora_fw.flasher.flasher import stage_flash_job; print(stage_flash_job('$axf', {'type':'$target_type'}, '$reason'))"
    ;;
  flash)
    job="$2"
    $PY -c "from aurora_fw.flasher.flasher import flash_now; import json; print(json.dumps(flash_now('$job')))"
    ;;
  *)
    echo "usage: $0 {stage <axf> <target> <reason> | flash <job.json>}"
    ;;
esac
