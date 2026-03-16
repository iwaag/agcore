#!/usr/bin/env bash
set -euo pipefail

shutdown() {
  kill -TERM "${api_pid:-0}" "${worker_pid:-0}" 2>/dev/null || true
}

trap shutdown TERM INT

uv run uvicorn agcore_api.main:app --host 0.0.0.0 --port 8000 &
api_pid=$!

uv run python -m agcore_worker.main &
worker_pid=$!

wait -n "$api_pid" "$worker_pid"
status=$?

shutdown
wait "$api_pid" "$worker_pid" 2>/dev/null || true

exit "$status"
