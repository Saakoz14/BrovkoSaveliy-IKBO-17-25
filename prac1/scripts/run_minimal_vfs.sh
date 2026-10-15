#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "$PROJECT_DIR/run.sh" \
    --vfs "$PROJECT_DIR/examples/vfs_minimal" \
    --script "$PROJECT_DIR/examples/startup_success.txt"

