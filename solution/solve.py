#!/usr/bin/env python3
"""Reference solution for the Batch 4471 acceptance review task.

Reads the raw data from /data, computes true position for each sampled
serial (handling the duplicate row, the inch-unit rows, and the corrupted
probe-fault row), cross-references the production traveler against the
material certification to find heat-lot traceability gaps, and writes the
three required deliverables to /output.
"""
import csv
import math
import os

DATA_DIR = "/data"
OUTPUT_DIR = "/output"

TOLERANCE_MM = 0.25
CERTIFIED_HEAT_LOT = "HL-2291"


def load_cmm_rows():
    path = os.path.join(DATA_DIR, "cmm_inspection_batch4471.csv")
    rows = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


def dedupe(rows):
    seen = set()
    deduped = []
    for row in rows:
        key = (row["serial"], row["dx"], row["dy"], row["units"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def evaluate_dimensional(rows):
    """Returns (dimensional_defects, inconclusive_serials)."""
    defects = {}
    inconclusive = []
    for row in rows:
        serial = row["serial"]
        dx_raw, dy_raw = row["dx"], row["dy"]
        if not _is_number(dx_raw) or not _is_number(dy_raw):
            inconclusive.append(serial)
            continue
        dx, dy = float(dx_raw), float(dy_raw)
        if row["units"].strip().lower() == "in":
            dx *= 25.4
            dy *= 25.4
        tp = 2 * math.sqrt(dx ** 2 + dy ** 2)
        if tp > TOLERANCE_MM:
            defects[serial] = tp
    return defects, inconclusive


def _is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def load_heat_lot_ranges():
    path = os.path.join(DATA_DIR, "production_traveler_batch4471.csv")
    ranges = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            ranges.append(
                (int(row["serial_range_start"]), int(row["serial_range_end"]), row["heat_lot"])
            )
    return ranges


def find_traceability_gaps(ranges):
    gaps = []
    for start, end, heat_lot in ranges:
        if heat_lot != CERTIFIED_HEAT_LOT:
            for n in range(start, end + 1):
                gaps.append((f"BR-4471-{n:03d}", heat_lot))
    return gaps


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    raw_rows = load_cmm_rows()
    rows = dedupe(raw_rows)
    dimensional_defects, inconclusive = evaluate_dimensional(rows)

    ranges = load_heat_lot_ranges()
    traceability_gaps = find_traceability_gaps(ranges)

    sample_size = len(rows)
    defect_count = len(dimensional_defects)

    # --- defect_serials.csv ---
    defect_rows = []
    for serial, tp in sorted(dimensional_defects.items()):
        defect_rows.append(
            (serial, "dimensional", f"True position {tp:.2f}mm exceeds 0.25mm tolerance (Note 12)")
        )
    for serial, heat_lot in traceability_gaps:
        defect_rows.append(
            (
                serial,
                "material_traceability",
                f"Produced from heat lot {heat_lot}, not covered by certification SMW-C-30456 ({CERTIFIED_HEAT_LOT} only)",
            )
        )
    for serial in inconclusive:
        defect_rows.append(
            (serial, "other", "CMM Y-axis reading not captured (probe fault) - remeasurement required")
        )

    with open(os.path.join(OUTPUT_DIR, "defect_serials.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["serial", "defect_type", "defect_detail"])
        for row in defect_rows:
            writer.writerow(row)

    # --- recommendation.md ---
    verdict = "REJECT"
    with open(os.path.join(OUTPUT_DIR, "recommendation.md"), "w") as f:
        f.write(f"# Batch 4471 Acceptance Recommendation\n\n")
        f.write(f"## Verdict: {verdict}\n\n")
        f.write(
            f"Lot size 200 units, General Inspection Level II, AQL 1.5% per the "
            f"quality manual sampling table gives a sample size of {sample_size} "
            f"units with Ac=1 / Re=2.\n\n"
        )
        f.write(
            f"{defect_count} of the {sample_size} sampled units exceed the "
            f"diameter 0.25mm true-position tolerance in drawing Note 12: "
            f"{', '.join(sorted(dimensional_defects))}. This meets the "
            f"rejection number (Re=2) for the sampling plan, so the batch "
            f"cannot be accepted on dimensional grounds as submitted.\n\n"
        )
        f.write(
            f"Separately, the production traveler shows serials "
            f"{traceability_gaps[0][0]} through {traceability_gaps[-1][0]} "
            f"were produced from heat lot {traceability_gaps[0][1]}, which is "
            f"not covered by the supplied material certification "
            f"(SMW-C-30456, heat lot {CERTIFIED_HEAT_LOT} only). Per drawing "
            f"Note 7, these units are non-conforming regardless of dimensional "
            f"results.\n\n"
        )
        f.write(
            "These are two independent, correctable issues rather than a "
            "batch-wide failure. The schedule pressure raised internally does "
            "not change either finding. Recommend the batch be returned to "
            "Sterling Machine Works for targeted rework and recertification "
            "(see supplier notice) rather than releasing it as-is or scrapping "
            "the full 200-unit lot.\n"
        )

    # --- supplier_notice.md ---
    with open(os.path.join(OUTPUT_DIR, "supplier_notice.md"), "w") as f:
        f.write("# Supplier Notice - Batch 4471\n\n")
        f.write("To: Sterling Machine Works\n")
        f.write("Re: PO-88213 / Batch 4471 - FX-220 Fixture Bracket\n\n")
        f.write(
            f"Batch 4471 cannot be closed out as submitted. Two items require "
            f"action before disposition:\n\n"
        )
        f.write(
            f"1. Rework and re-inspect true position on serials "
            f"{', '.join(sorted(dimensional_defects))} to conform with "
            f"diameter 0.25mm per drawing Note 12, or replace with conforming "
            f"units.\n"
        )
        f.write(
            f"2. Provide a corrected material certification covering heat lot "
            f"{traceability_gaps[0][1]}, used for serials "
            f"{traceability_gaps[0][0]} through {traceability_gaps[-1][0]} "
            f"following the mid-run stock changeover, per drawing Note 7.\n\n"
        )
        f.write(
            "The remainder of the batch is not affected by either finding and "
            "does not require return or rework.\n"
        )

    print(f"Sample size: {sample_size}")
    print(f"Dimensional defects: {sorted(dimensional_defects.keys())}")
    print(f"Traceability gap range: {traceability_gaps[0][0]}..{traceability_gaps[-1][0]} ({len(traceability_gaps)} serials)")
    print(f"Inconclusive: {inconclusive}")
    print("Wrote recommendation.md, defect_serials.csv, supplier_notice.md")


if __name__ == "__main__":
    main()
