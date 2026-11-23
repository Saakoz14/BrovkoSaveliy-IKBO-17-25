#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"
mkdir -p output

for example in vector_mod_1 vector_mod_2 vector_mod_3; do
    ./run.sh "examples/${example}.csv" "output/${example}.bin"
    python3 -m src.interpreter \
        "output/${example}.bin" \
        "output/${example}_dump.csv" \
        --start 200 \
        --end 206
done

