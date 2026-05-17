# Glider discovery status

Cook (2004) Figure 5 documents periods and widths for the following gliders,
all of which the universality construction depends on. Verification means:
the delta-from-ether pattern, when placed on pure ether and evolved
`period_t` Rule 110 steps, reproduces shifted by `displacement` cells. The
check passes against `core/rule110.py` and is asserted in
`tests/test_gliders.py`.

| Glider | (period_t, displacement) | Status                  | Notes |
|--------|--------------------------|-------------------------|-------|
| A      | (3, +2)                  | verified                | 3-cell delta at left_phase 3 |
| B      | (4, -2)                  | verified                | 10-cell delta at left_phase 9 |
| C      | (7, 0)                   | verified                | 4-cell delta at left_phase 3 |
| D      | (10, +2)                 | verified                | 8-cell delta at left_phase 0 |
| Ebar   | (30, -8)                 | verified                | 7-cell delta at left_phase 10 |
| E      | (15, -4)                 | not yet found           | same velocity as Ebar; rare in random ICs |
| F      | (36, -4)                 | not searched            |       |
| Gn     | (42, -14)                | not searched            |       |
| H      | (92, -18)                | not searched            |       |

## What we tried for E

Past sweeps:

- 2000-seed random-IC track sweep (`scripts/track_gliders.py`) found A,
  B, C, D, Ē in isolation but never E. With the velocity overlap (-0.267)
  E and Ē compete for the same tracks; the verifier biases toward
  whichever is checked first.
- 2-glider collision sweeps (`scripts/find_e_via_collisions.py`) over
  all pairs of verified gliders and a range of offsets — no clean E.

Latest escalations:

- `scripts/exhaustive_e_search.py` performs a width-N bitmask sweep over
  all 14 ether phases with strict ether-halo verification (the verifier
  requires both the captured delta and a 20-cell ether halo to reappear
  unchanged, eliminating false positives that disturb surrounding ether).
  Width-14 sweep across all 14 phases (172k candidates) returned **zero
  hits**.
- `scripts/exhaustive_e_search_constrained.py` extends to width 19
  (Cook's natural E1 extent) with a popcount-bounded combinatorial sweep
  (delta cardinality 5-13 cells, matching what other gliders show). The
  search space here is ~3.6M candidates; the sweep is partial.
- `scripts/long_random_e.py` runs 1500-step random-IC evolutions and
  applies the strict period-15 verifier with period-30 disambiguation
  (a captured cluster that also verifies under (30, -8) is rejected as
  Ē, not E).

## What is needed

The pragmatic options:

1. Continue the constrained width-19 (and width-27 for E2) exhaustive
   sweep on a machine that can run it to completion (hours of CPU).
2. Read the glider patterns directly from `15-1-1.pdf` Figure 4 or an
   external reference table (Wolfram Atlas, Martinez & McIntosh).
3. Accept that the construction does not strictly need E — Cook's
   §4 encoding uses C / Ē / A primarily — and document the
   incompleteness, which is what the README does.

## What is unblocked

The construction can proceed without E. The state-encoding round-trip
(C-glider tape data) is verified
(`tests/test_cts_to_r110.py`, `tests/test_end_to_end.py`). Closing the
**collision-driven** version of the CTS encoder remains gated on the
collision atlas, but that work is empirical — it doesn't need E to start.
