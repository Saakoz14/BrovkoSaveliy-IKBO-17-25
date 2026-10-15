#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "$PROJECT_DIR/run.sh" \
    --vfs "$PROJECT_DIR/examples/directory-does-not-exist" \
    --script "$PROJECT_DIR/examples/startup_success.txt"

