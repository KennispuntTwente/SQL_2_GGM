#!/usr/bin/env bash
set -euo pipefail

# Run both smoke services sequentially, detached, and collect exit codes via docker wait.
# This avoids attaching to logs/TTY so the script returns cleanly without needing to press Enter.
# Usage:
#   bash docker/smoke/run_all.sh

run_service_detached() {
	local svc="$1"
	local timeout_sec="${SMOKE_SERVICE_TIMEOUT:-300}"
	echo "[smoke] Building and starting $svc detached…"
	# Only force a build if explicitly requested; in CI we pre-build the image and rely on cache
	local build_flag=""
	if [[ "${SMOKE_FORCE_BUILD:-0}" == "1" ]]; then
		build_flag="--build"
	fi
	docker compose -f docker/smoke/docker-compose.yml up ${build_flag} -d "$svc"
	local cid
	cid=$(docker compose -f docker/smoke/docker-compose.yml ps -q "$svc")
	echo "[smoke] Waiting for $svc (container $cid) to exit… (timeout ${timeout_sec}s)"

	# Poll for exit with a timeout instead of blocking indefinitely on docker wait
	local start_ts now_ts elapsed status
	start_ts=$(date +%s)
	status="running"
	while true; do
		# Check current status
		status=$(docker inspect -f '{{.State.Status}}' "$cid" 2>/dev/null || echo "unknown")
		if [[ "$status" == "exited" || "$status" == "dead" ]]; then
			break
		fi
		now_ts=$(date +%s)
		elapsed=$(( now_ts - start_ts ))
		if (( elapsed >= timeout_sec )); then
			echo "[smoke] TIMEOUT after ${timeout_sec}s waiting for $svc (status=$status). Showing logs and stopping container…" >&2
			# Show logs to help debugging, then stop the container
			docker compose -f docker/smoke/docker-compose.yml logs --no-color "$svc" || true
			docker stop "$cid" >/dev/null 2>&1 || true
			# Return a distinctive exit code for timeout
			return 124
		fi
		sleep 2
	done

	# Get the actual exit code
	local code
	code=$(docker inspect -f '{{.State.ExitCode}}' "$cid" 2>/dev/null || echo 1)
	echo "[smoke] $svc exited with code $code"
	echo "[smoke] ---- $svc logs (last run) ----"
	docker compose -f docker/smoke/docker-compose.yml logs --no-color "$svc" || true
	return "$code"
}

overall=0

echo "[smoke] Running app-source-to-staging-sqlalchemy (dump)"
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

echo "[smoke] Running app-source-to-staging-connectorx (dump)"
if ! run_service_detached app-source-to-staging-connectorx; then
	overall=1
fi
echo "[smoke] Cleaning up…"
docker compose -f docker/smoke/docker-compose.yml down -v --remove-orphans || true

echo "[smoke] Running app-source-to-staging-direct (SQLAlchemy direct)"
if ! run_service_detached app-source-to-staging-direct; then
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