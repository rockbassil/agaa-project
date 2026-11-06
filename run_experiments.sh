#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -m unittest discover -s tests -v
python src/superfamilies.py --dataset all --repetitions 20 --seed 42 --swap-multiplier 5 --output results
