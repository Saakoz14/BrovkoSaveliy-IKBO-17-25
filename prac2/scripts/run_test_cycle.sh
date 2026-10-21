#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "$PROJECT_DIR/run.sh" \
    --config "$PROJECT_DIR/examples/configs/test_cycle.csv"

