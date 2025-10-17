#!/bin/sh
set -eu

# Simple dispatcher to run one of the two pipelines.
# Usage:
#   docker run ggmpilot                 # runs source_to_staging by default
#   docker run ggmpilot staging-to-silver -c /cfg.ini
#   docker run -e PIPELINE=staging-to-silver ggmpilot -- -c /cfg.ini

# If the first CLI arg looks like a pipeline name, use it; otherwise fall back to $PIPELINE.
PIPELINE_ARG="${1:-}"
case "$PIPELINE_ARG" in
  source-to-staging|staging-to-silver)
    PIPELINE="$PIPELINE_ARG"
    shift
    ;;
  *)
    PIPELINE="${PIPELINE:-source-to-staging}"
    ;;
esac

# Allow double dash to separate pipeline selector from module args when using env var mode.
if [ "${1:-}" = "--" ]; then
  shift
fi

case "$PIPELINE" in
  source-to-staging)
    exec python -m source_to_staging.main "$@"
    ;;
  staging-to-silver)
    exec python -m staging_to_silver.main "$@"
    ;;
  *)
    echo "Unknown PIPELINE: $PIPELINE" >&2
    echo "Valid options: source-to-staging | staging-to-silver" >&2
    exit 1
    ;;
ese