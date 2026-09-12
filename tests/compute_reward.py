#!/usr/bin/env python3
"""Reads per-test pass/fail from the CTRF report, applies the weights in
test_weights.json, and writes the final weighted reward as required:
  reward = sum(earned weights) / sum(positive weights)
Negative-weight (penalty) tests subtract from the numerator only when they
pass; none are defined in this task's test_weights.json.
"""
import json
import os

LOGS_DIR = "/logs/verifier"
WEIGHTS_PATH = "/tests/test_weights.json"


def main():
    with open(WEIGHTS_PATH) as f:
        weight_rows = json.load(f)
    weights = {row["test_name"]: row["weight"] for row in weight_rows}

    ctrf_path = os.path.join(LOGS_DIR, "ctrf.json")
    with open(ctrf_path) as f:
        ctrf = json.load(f)

    results = {}
    for t in ctrf["results"]["tests"]:
        name = t["name"].split("::")[-1]
        results[name] = t["status"] == "passed"

    positive_total = sum(w for w in weights.values() if w > 0)
    earned = 0
    for name, passed in results.items():
        w = weights.get(name, 1)  # default weight 1 if not listed
        if w > 0 and passed:
            earned += w
        elif w < 0 and passed:
            # a passing penalty test means the defect it checks for is present
            earned += w  # subtracts

    reward = max(0.0, earned / positive_total) if positive_total else 0.0

    with open(os.path.join(LOGS_DIR, "reward.json"), "w") as f:
        json.dump({"reward": round(reward, 4)}, f)

    print(f"Weighted reward: {reward:.4f} ({earned}/{positive_total})")


if __name__ == "__main__":
    main()
