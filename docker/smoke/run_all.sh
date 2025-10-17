#!/usr/bin/env bash
set -euo pipefail

# Run both smoke services sequentially, detached, and collect exit codes via docker wait.
# This avoids attaching to logs/TTY so the script returns cleanly without needing to press Enter.
# Usage:
#   bash docker/smoke/run_all.sh

run_service_detached() {
	local svc="$1"
	echo "[smoke] Building and starting $svc detached…"
	docker compose -f docker/smoke/docker-compose.yml up --build -d "$svc"
	local cid
	cid=$(docker compose -f docker/smoke/docker-compose.yml ps -q "$svc")
	echo "[smoke] Waiting for $svc (container $cid) to exit…"
	local code
	code=$(docker wait "$cid")
	echo "[smoke] $svc exited with code $code"
	echo "[smoke] ---- $svc logs (last run) ----"
	docker compose -f docker/smoke/docker-compose.yml logs --no-color "$svc" || true
	return "$code"
}

overall=0

echo "[smoke] Running app-source-to-staging-sqlalchemy"
if ! run_service_detached app-source-to-staging-sqlalchemy; then
	overall=1
fi
echo "[smoke] Cleaning up…"
docker compose -f docker/smoke/docker-compose.yml down -v --remove-orphans || true

echo "[smoke] Running app-get-connection"
if ! run_service_detached app-get-connection; then
	overall=1
fi
echo "[smoke] Cleaning up…"
docker compose -f docker/smoke/docker-compose.yml down -v --remove-orphans || true

echo "[smoke] Running app-source-to-staging-connectorx"
if ! run_service_detached app-source-to-staging-connectorx; then
	overall=1
fi
echo "[smoke] Cleaning up…"
docker compose -f docker/smoke/docker-compose.yml down -v --remove-orphans || true

echo "[smoke] Running app-staging-to-silver"
if ! run_service_detached app-staging-to-silver; then
	overall=1
fi
echo "[smoke] Cleaning up…"
docker compose -f docker/smoke/docker-compose.yml down -v --remove-orphans || true

if [[ "$overall" -eq 0 ]]; then
	echo "[smoke] All smoke tests passed"
else
	echo "[smoke] One or more smoke tests failed" >&2
fi
exit "$overall"