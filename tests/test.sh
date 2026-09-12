#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier

python3 -m pytest /tests/test_outputs.py --ctrf /logs/verifier/ctrf.json -v

# Weighted reward computation from test_weights.json + per-test pass/fail.
python3 /tests/compute_reward.py
