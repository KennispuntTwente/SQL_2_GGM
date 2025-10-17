#!/usr/bin/env bash
set -euo pipefail

# Run both smoke services sequentially, detached, and collect exit codes via docker wait.
# This avoids attaching to logs/TTY so the script returns cleanly without needing to press Enter.
# Usage:
#   bash docker/smoke/run_all.sh

run_service_detached() {
	local svc="$1"
	echo "[smoke] Building and starting $svc detached…"
	docker compose up --build -d "$svc"
	local cid
	cid=$(docker compose ps -q "$svc")
	echo "[smoke] Waiting for $svc (container $cid) to exit…"
	local code
	code=$(docker wait "$cid")
	echo "[smoke] $svc exited with code $code"
	echo "[smoke] ---- $svc logs (last run) ----"
	docker compose logs --no-color "$svc" || true
	return "$code"
}

overall=0

echo "[smoke] Running app (source_to_staging)"
if ! run_service_detached app; then
	overall=1
fi
echo "[smoke] Cleaning up…"
docker compose down -v --remove-orphans || true

echo "[smoke] Running app-getconn (connection roundtrip)"
if ! run_service_detached app-getconn; then
	overall=1
fi
echo "[smoke] Cleaning up…"
docker compose down -v --remove-orphans || true

echo "[smoke] Running app-cx (ConnectorX dump path)"
if ! run_service_detached app-cx; then
	overall=1
fi
echo "[smoke] Cleaning up…"
docker compose down -v --remove-orphans || true

if [[ "$overall" -eq 0 ]]; then
	echo "[smoke] All smoke tests passed"
else
	echo "[smoke] One or more smoke tests failed" >&2
fi
exit "$overall"