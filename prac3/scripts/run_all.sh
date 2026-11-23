#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

./scripts/run_stage2.sh
./scripts/run_copy.sh
./scripts/run_modulo.sh
./scripts/run_vectors.sh
python3 -m unittest discover -s tests -v

