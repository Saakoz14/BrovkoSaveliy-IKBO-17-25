#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"
mkdir -p output
./run.sh examples/modulo.csv output/modulo.bin
python3 -m src.interpreter \
    output/modulo.bin \
    output/modulo_dump.csv \
    --start 300 \
    --end 300

