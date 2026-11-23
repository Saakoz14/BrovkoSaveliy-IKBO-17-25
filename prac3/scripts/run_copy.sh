#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"
mkdir -p output
./run.sh examples/copy_array.csv output/copy_array.bin
python3 -m src.interpreter \
    output/copy_array.bin \
    output/copy_array_dump.csv \
    --start 100 \
    --end 202

