#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python data/prepare_data.py
python -m unittest discover -s tests -v
python src/superfamilies.py --dataset all --repetitions 100 --seed 42 --swap-multiplier 5 --output results
python src/superfamilies.py --dataset all --repetitions 100 --seed 43 --swap-multiplier 5 --output results/seed43
python src/superfamilies.py --dataset all --repetitions 100 --seed 42 --swap-multiplier 20 --output results/swaps20
python src/compare_profiles.py
