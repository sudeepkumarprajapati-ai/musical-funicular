# Task Description

The attempt acts as the Quality Engineer of record at a precision-parts
manufacturer, deciding whether an incoming batch of 200 machined fixture
brackets from a supplier should be accepted, rejected, or conditionally
accepted. The deliverables are a verdict memo, a per-serial defect list, and
a communication back to the supplier stating what is required of them.

# Complexity Justification

**Challenge 1 — True-position trap (dimensional analysis).**
What's planted: the CMM inspection sheet reports raw X/Y deviations per
sampled serial, not a pass/fail column. Two of the 32 sampled units fail the
drawing's actual GD&T true-position formula (TP = 2 x sqrt(dx^2+dy^2) <=
0.25mm), but one of the two (BR-4471-014, dx=0.100, dy=0.095) has both
individual axis deviations comfortably under a naive half-tolerance
threshold (0.125mm) and only fails when the two axes are combined correctly.
What a correct attempt does: applies the drawing's stated formula to every
sampled row and finds exactly two failures. What a careless attempt does:
eyeballs the individual dx/dy columns against an informal per-axis
threshold and misses the subtle failure, undercounting defects and
potentially concluding the sample is clean.

**Challenge 2 — Sampling-plan misapplication (quantitative decision rule).**
What's planted: the purchase order states the applicable AQL (1.5%) and
inspection level (II) in boilerplate contract language, not flagged as
significant; the actual sample-size and Ac/Re acceptance numbers live in a
separate quality-manual excerpt that must be cross-referenced by lot size.
What a correct attempt does: looks up the correct row (lot size 200 units,
sample size 32, Ac=1/Re=2) and compares the true defect count against Re.
What a careless attempt does: reasons informally ("2 out of 32 is a small
percentage, so accept") instead of applying the actual acceptance-number
rule, which reaches the opposite, incorrect conclusion.

**Challenge 3 — Heat-lot traceability (the crux; cross-document
reconciliation).** This is the reasoning challenge that decides the final
recommendation together with Challenge 1/2's dimensional finding, and it is
independent of both. What's planted: the supplier's material certification
covers only 180 of the 200 units' worth of material (heat lot HL-2291); the
internal production traveler — a separate document an analyst focused on the
CMM data or the contract terms would have no obvious reason to open — shows
a mid-run raw-stock changeover to an uncertified heat lot (HL-2305) for
serials 181-200. What a correct attempt does: reads the traveler alongside
the certification and flags all twenty changeover-lot serials as
nonconforming on traceability grounds regardless of their dimensional
results. What a careless attempt does: either never opens the traveler at
all (missing the issue entirely) or treats the material certification's
presence as sufficient proof of full-batch conformance without checking
which serials it actually covers.

A secondary, lower-weight distractor tests whether the attempt lets internal
schedule pressure (an email pushing for release before the data review is
finished) override the inspection findings, and whether it correctly
classifies data-quality issues in the raw CMM sheet (a duplicated row, two
rows recorded in inches instead of millimetres, and one row with a corrupted
sensor reading) rather than silently mishandling them.

# Taxonomy

- Category: Engineering — Manufacturing Quality
- Sub-domain: Incoming inspection, GD&T interpretation, sampling-plan
  application, supplier quality management
- Skills exercised: geometric dimensioning and tolerancing computation,
  attribute sampling-plan lookup and application, cross-document data
  reconciliation, prioritization under stakeholder pressure

# Expected Difficulty Range

Target: strong model mean reward at or under 0.6, weak model mean at or
under 0.35, across four sweep attempts each.

Why a strong attempt plausibly misses: the true-position trap (Challenge 1)
requires applying the stated formula to all 32 rows rather than
pattern-matching on individual axis values, which is an easy shortcut to
take when skimming a spreadsheet. The traceability finding (Challenge 3)
requires the attempt to independently think to open and reconcile the
production traveler against the material certification; nothing in the CMM
data or the purchase order points to this document directly, so an attempt
that treats the CMM sheet as the primary or sole source of truth will miss
it. Reaching the correct combined verdict requires catching both
independent findings, and the schedule-pressure email is a plausible
attractor toward an incorrect "accept" recommendation.

# Ground-Truth Recommendation

**Verdict: REJECT** (as submitted; correctable via targeted rework and
supplier recertification, not a blanket batch return).

Forcing figures:
- Lot size 200, AQL 1.5%, General Inspection Level II -> sample size 32,
  Ac=1/Re=2 per the quality manual sampling table.
- Correctly computed true position (TP = 2 x sqrt(dx^2+dy^2)) against the
  drawing's diameter 0.25mm tolerance yields exactly 2 failing serials in
  the 32-unit sample: BR-4471-014 (TP approximately 0.28mm) and
  BR-4471-108 (TP approximately 0.41mm). 2 defects meets the rejection
  number Re=2, so the sampling plan alone rejects the lot.
- The production traveler shows serials BR-4471-181 through BR-4471-200
  (20 units) were produced from heat lot HL-2305, following a mid-run
  stock changeover; the supplied material certification (SMW-C-30456)
  covers only heat lot HL-2291. Per drawing Note 7, these 20 units are
  non-conforming on traceability grounds independent of the dimensional
  result.

Why the plausible wrong answers are wrong:
- **ACCEPT** ignores both the sampling-plan rejection number and the
  traceability gap; it is only reachable by missing at least one of
  Challenges 1 and 3, or by letting the schedule-pressure email override
  the data.
- **Blanket REJECT / return the full 200-unit batch** overreaches: only 22
  of the 200 units (2 dimensional + 20 traceability, non-overlapping) have
  an identified nonconformance. The other 178 units have no finding against
  them in the provided data, so a full-batch return is not supported and
  should be flagged as such (see rubric items on the supplier notice not
  demanding full-batch return).
