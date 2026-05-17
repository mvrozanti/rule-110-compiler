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

## Why the gap

The exhaustive perturbation search (`scripts/discover_gliders.py`) covers
deltas up to width 12-14 across all 14 ether phases for the small-period
gliders. Only A appears. Random-IC observation
(`scripts/observe_gliders.py`) successfully detects the *presence* of all
gliders in chaotic Rule 110 evolution, but extracting their *minimal bit
pattern* from chaotic spacetime is producing false positives (3-cell
patterns that happen to satisfy the periodic-shift check inside the
chaotic field but do not propagate when placed in clean ether).

## What is needed

Cook's gliders have non-trivial spatial extent — Figure 4 in the paper
shows them spanning 6-30 pixels. To discover them empirically, the
search must:

1. Use wider candidate windows (16-30 cells) and search a larger phase
   space, possibly with smarter heuristics than exhaustive enumeration.
2. Or: extract patterns from cleanly-isolated late-time gliders in
   random simulations, after collisions have annihilated most activity.
3. Or: read the glider patterns directly from `15-1-1.pdf` Figure 4 or
   an external reference table (e.g., Wolfram Cellular Automaton Atlas,
   Martinez & McIntosh tables).

Approach 3 is the most reliable but requires either visual inspection
of the paper figures or finding an external source with the patterns
in machine-readable form. The remaining work is in progress; pipeline
phases that depend on Cook's collision atlas (Phase 3, Phase 4
`cts_to_r110.py`, Phase 7 end-to-end) are blocked behind this.

## What is unblocked

The pipeline above the Rule 110 layer does not need the gliders:

- Phase 4 `compiler/cts.py` (pure CTS simulator) — pure algorithmic
- Phase 5 `compiler/tm_to_cts.py` (Neary-Woods reduction) — pure algorithmic
- Phase 6 `compiler/bf.py` + `compiler/bf_to_tm.py` — pure algorithmic

These can proceed in parallel.
