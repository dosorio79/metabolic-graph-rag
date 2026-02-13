#!/usr/bin/env bash
set -euo pipefail

DAG_ID=${1:-}
TASK_ID=${2:-}

if [[ -z "$DAG_ID" ]]; then
  echo "Usage: $0 <dag_id> [task_id]"
  echo "Example: $0 kegg_ingestion ingest_kegg_pathway"
  exit 1
fi

BASE_DIR="airflow/logs/dag_id=${DAG_ID}"
if [[ ! -d "$BASE_DIR" ]]; then
  echo "No logs found for DAG: ${DAG_ID}"
  exit 1
fi

if [[ -z "$TASK_ID" ]]; then
  echo "Available runs for ${DAG_ID}:"
  ls -1 "$BASE_DIR"
  exit 0
fi

LATEST_LOG=$(find "$BASE_DIR" -path "*task_id=${TASK_ID}*" -name "attempt=*.log" -printf "%T@ %p\n" | sort -n | tail -n 1 | cut -d' ' -f2-)

if [[ -z "$LATEST_LOG" ]]; then
  echo "No task logs found for ${DAG_ID}.${TASK_ID}"
  exit 1
fi

echo "Showing: ${LATEST_LOG}"
cat "$LATEST_LOG"
