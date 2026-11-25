#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

for example in web_server database game; do
    echo "===== $example ====="
    ./run.sh < "examples/${example}.conf"
done

