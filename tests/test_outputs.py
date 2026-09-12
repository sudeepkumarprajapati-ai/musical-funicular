"""Verifier for the Batch 4471 acceptance review task.

Reads only the attempt's final output files under /output. The ground truth
below is fixed independently (matches solution/solve.py's derivation from
the shipped data) so grading does not depend on re-parsing /data.
"""
import csv
import os
import re

OUTPUT_DIR = "/output"

EXPECTED_DIMENSIONAL = {"BR-4471-014", "BR-4471-108"}
EXPECTED_TRACEABILITY = {f"BR-4471-{n:03d}" for n in range(181, 201)}
CONFORMING_TRAP_SERIALS = {"BR-4471-019", "BR-4471-057", "BR-4471-099"}  # dup / unit-converted, must NOT be flagged
VALID_SERIAL_RANGE = range(1, 201)


def _read_defect_csv():
    path = os.path.join(OUTPUT_DIR, "defect_serials.csv")
    assert os.path.exists(path), f"Missing output file: {path}"
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    return rows


def _read_text(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    assert os.path.exists(path), f"Missing output file: {path}"
    with open(path) as f:
        return f.read()


def test_defect_serials_exists_and_valid_header():
    rows = _read_defect_csv()
    path = os.path.join(OUTPUT_DIR, "defect_serials.csv")
    with open(path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
    assert header == ["serial", "defect_type", "defect_detail"], (
        f"Header must be exactly serial,defect_type,defect_detail, got {header}"
    )
    assert len(rows) > 0, "defect_serials.csv has no data rows"


def test_dimensional_defects_correct():
    rows = _read_defect_csv()
    found = {r["serial"] for r in rows if r["defect_type"] == "dimensional"}
    assert found == EXPECTED_DIMENSIONAL, (
        f"Dimensional defects should be exactly {EXPECTED_DIMENSIONAL}, got {found}"
    )


def test_material_traceability_defects_correct():
    rows = _read_defect_csv()
    found = {r["serial"] for r in rows if r["defect_type"] == "material_traceability"}
    assert found == EXPECTED_TRACEABILITY, (
        f"Material traceability defects should be exactly the 20 serials "
        f"BR-4471-181..BR-4471-200, got {len(found)} serials: "
        f"missing={EXPECTED_TRACEABILITY - found}, extra={found - EXPECTED_TRACEABILITY}"
    )


def test_no_extraneous_serials():
    rows = _read_defect_csv()
    for r in rows:
        m = re.match(r"^BR-4471-(\d{3})$", r["serial"])
        assert m, f"Serial '{r['serial']}' is not in the expected BR-4471-XXX format"
        n = int(m.group(1))
        assert n in VALID_SERIAL_RANGE, f"Serial {r['serial']} is outside the batch (1-200)"


def test_no_false_conforming_flagged():
    rows = _read_defect_csv()
    all_serials = {r["serial"] for r in rows}
    wrongly_flagged = all_serials & CONFORMING_TRAP_SERIALS
    assert not wrongly_flagged, (
        f"These serials are dimensionally conforming (duplicate row / unit-converted "
        f"inch readings) and should not appear as defects: {wrongly_flagged}"
    )


def test_recommendation_verdict_is_reject():
    text = _read_text("recommendation.md")
    upper = text.upper()
    # Look for a clearly labeled verdict token (ACCEPT/REJECT/CONDITIONAL ACCEPT)
    # near the word "verdict" rather than scanning the whole prose, since REJECT
    # or ACCEPT may appear informally elsewhere in the rationale.
    verdict_line_match = re.search(r"VERDICT\s*:?\s*\**\s*(ACCEPT|REJECT|CONDITIONAL ACCEPT)", upper)
    assert verdict_line_match, "Could not find a clearly labeled verdict (ACCEPT/REJECT/CONDITIONAL ACCEPT) in recommendation.md"
    assert verdict_line_match.group(1) == "REJECT", (
        f"Verdict should be REJECT, found '{verdict_line_match.group(1)}'"
    )


def test_supplier_notice_exists():
    text = _read_text("supplier_notice.md")
    assert len(text.strip()) > 0, "supplier_notice.md is empty"


def test_probe_fault_serial_handled():
    rows = _read_defect_csv()
    match = [r for r in rows if r["serial"] == "BR-4471-070"]
    if match:
        assert match[0]["defect_type"] != "dimensional", (
            "BR-4471-070 has no valid Y reading (probe fault) and should not be "
            "classified as a confirmed dimensional defect"
        )
