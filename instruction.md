# Batch Acceptance Review — Fixture Bracket Batch 4471

You are the Quality Engineer of record for Acme Precision Fasteners. Batch 4471 of the FX-220 fixture bracket has arrived from Sterling Machine Works and is sitting in receiving inspection, blocking the next production run.

All of the batch's paperwork and inspection data are provided in `/data/`. The directory contains: the CMM inspection results, the applicable engineering drawing excerpt, the purchase order, the quality manual's sampling plan reference, the supplier's material certification, the internal production traveler, a recent email thread about the batch, and a rework cost reference.

Decide whether Batch 4471 should be accepted, rejected, or conditionally accepted, and produce the following three files under `/output/`:

1. `/output/recommendation.md` — a memo stating your overall verdict as exactly one of: `ACCEPT`, `REJECT`, or `CONDITIONAL ACCEPT`, clearly labeled near the top of the file, followed by your supporting rationale in prose.

2. `/output/defect_serials.csv` — a CSV with exactly the header `serial,defect_type,defect_detail`, listing every serial number in the batch you determine has a nonconformance. `defect_type` must be one of `dimensional`, `material_traceability`, or `other`. `defect_detail` is a one-line explanation of the specific issue for that serial. Serial numbers should be written in the form `BR-4471-XXX` (three-digit, zero-padded) matching the format used in the inspection data.

3. `/output/supplier_notice.md` — the communication you would send back to Sterling Machine Works, stating specifically what is required of them, if anything, before the batch can be closed out.

Base every conclusion strictly on the data provided in `/data/`. Do not assume information that isn't in the files, and do not rely on general industry knowledge in place of what the documents actually state.
