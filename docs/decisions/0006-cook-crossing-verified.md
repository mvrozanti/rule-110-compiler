# 0006 — Cook §3.2.4 C2 × Ebar crossing verified

## Status

Accepted. **First Cook-faithful collision codified as a passing test fixture.**

## What was verified

Six placement gaps (0, 5, 10, 22, 25, 30) for the variant pair
`(C2 width=3 L=2 delta=(1,0,0,0,0,0), Ebar width=7 L=4
delta=(1,1,0,0,1,1,1))` all produce a **crossing collision** in
Rule 110:

  - C2 survives at its original anchor. The cells `[c2_anchor,
    c2_anchor + 6)` are non-ether and identical between time
    `t = 1400` and time `t + 7`.
  - A new period-(30, -8) glider exists on the safe central left side
    of c2_anchor. Verified empirically by `find_displaced_glider`
    using `compiler.glider_detect` and pinned down further by
    `test_crossing_ebar_persists_over_eight_periods` — the same bit
    pattern continues displacing by -8 every 30 steps for 8 consecutive
    periods.

Empirical evidence: `tests/test_cook_crossing.py` (8 tests passing).

## The phase-shift discovery

The post-crossing Ebar's bit pattern at its new anchor is **NOT**
`Ebar.delta = (1, 1, 0, 0, 1, 1, 1)`. Empirically it is `(1, 0, 0, 0, 1, 0, 0)`
(pinned by `test_crossing_phase_shift_changes_ebar_bit_pattern`).

This is consistent with the prediction in ADR 0005: Cook's crossing
shifts each glider's *local left_phase* by the OTHER glider's width
mod 14. Before the crossing, Ebar sat at left_phase=4 with phase-3 ether
on its left (from C2's width=3). After the crossing, Ebar sits to the
left of C2 with phase-0 ether on its left — local left_phase shifted by
the cumulative-width difference. Same glider, different bit-pattern
representation.

This is why the previous bit-exact detector in
`scripts/find_cook_crossing.py:survives_collision` reported zero
crossings: it was looking for the pre-crossing pattern at a position
where the glider now has the post-crossing pattern. The structural
detector in `compiler/glider_detect.py` ignores bit pattern and matches
on period/displacement — robust to phase shift.

## What this unblocks

Plan A from ADR 0002 / ADR 0004 / ADR 0005 is no longer hypothetical.
At least one Cook-faithful collision reproduces. The remaining work
for M3 (Cook's core 8 collision atlas):

  - **Done:** C2 × Ebar crossing.
  - **Open:** A4 × Ebar ossification (Ebar → C); leader × tape-Y;
    leader × tape-N; primary component accept/reject; rejector ×
    component; acceptor × component.

Each of these is now empirical-search-and-verify work using the same
techniques: structural detectors via `compiler/glider_detect.py`, gap
sweeps via `scripts/find_cook_crossing.py` adapted per collision.

## References

- `compiler/glider_detect.py` — `is_stationary_glider`,
  `find_displaced_glider`.
- `tests/test_cook_crossing.py` — 8 tests pinning the crossing fixtures.
- `scripts/find_cook_crossing.py` — cartesian variant × gap sweep.
- ADR 0005 — predicted the post-crossing phase shift; this ADR confirms it.
