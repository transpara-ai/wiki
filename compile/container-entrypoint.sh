#!/bin/sh
set -eu

case "${1:-serve}" in
  serve)
    : "${KNOWLEDGE_HUB_AUTHORING_TOKEN:?Configure an editor token before starting the authoring server}"
    # The checkout is durable host state. Build from it after every container
    # replacement, holding the same lock as browser ingestion and refresh.
    flock -w 300 compile/.wiki-write.lock python3 compile/build_site.py
    exec python3 compile/ingest_server.py 0.0.0.0 8787
    ;;
  refresh)
    interval="${KNOWLEDGE_HUB_REFRESH_SECONDS:-900}"
    case "$interval" in
      ''|*[!0-9]*) echo "Refresh interval must be a positive integer" >&2; exit 1 ;;
    esac
    if [ "$interval" -lt 1 ]; then
      echo "Refresh interval must be a positive integer" >&2
      exit 1
    fi
    trap 'exit 0' INT TERM
    while :; do
      sleep "$interval" &
      wait "$!"
      if ! flock -w 300 compile/.wiki-write.lock python3 compile/refresh.py; then
        echo "Wiki refresh failed; retrying after the next interval" >&2
      fi
    done
    ;;
  *) exec "$@" ;;
esac
