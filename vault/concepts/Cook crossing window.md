---
type: concept
era: side-projects
tags: [rule-110, cook, crossing, collision]
date: 2026-05
---

# Cook crossing window

[[Cook universality proof|Cook §3.2.4]] claims a "crossing collision" where moving data (Ē) passes through tape data (C2) and both gliders survive. The crossing exists at one specific α-alignment among four possible C2 × Ē outcomes.

For our [[Cook-faithful glider catalogue]] variants (C2 width 3 at left_phase 2; Ē width 7 at left_phase 4), the empirical strict-real crossing window is **gap = 36..49 inclusive** (14 contiguous gap values). Outside that window — gaps 0..35 and 50..55 — the [[Structural glider detector|strict]] `is_real_stationary_glider` finds **no real C2 at the original anchor**; the cells become [[Phase-shifted ether]] and the C2 is effectively destroyed.

Verified in `tests/test_cook_crossing.py::test_c2_x_ebar_strict_real_c2_survival_at_specific_gaps` (14 parametrized passes) and the rejection counterpart at gaps 0..30.

Post-crossing C2 has a phase-shifted bit pattern (its local left_phase rotated by Ē's width = 7), so bit-exact detection would have missed it — that's why strict-real detection is structural ([[Structural glider detector]]).

The Ē side of the crossing — its emergence on the left of the C2 with the symmetric phase shift — remains a structural detection challenge: an "invisible Ē" with bits indistinguishable from phase-shifted ether at every phase tested. Cook explicitly names these "invisibles" — see [[Cook universality proof]].

The `EBAR_GAP=40` choice in `compiler/cook_tape.py` ([[EBAR_GAP=40 calibration]]) sits squarely in the strict-real crossing window. That single change took the BF '++' scanner pass from 0 strict-real Y survivors → 7.

## Connects to

- [[Cook universality proof]]
- [[Cook-faithful glider catalogue]]
- [[Cook glider width]]
- [[Phase-shifted ether]]
- [[Structural glider detector]]
- [[EBAR_GAP=40 calibration]]
- [[Rule 110 compiler]]
