#!/usr/bin/env bash
set -euo pipefail
# Ensure bridge is up before the dashboard/API try to call it
make bridge-ensure