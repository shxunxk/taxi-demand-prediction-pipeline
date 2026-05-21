#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose -f docker-compose.yaml -f ../minio/docker-compose.objectstore.yaml --env-file .env up -d "$@"
