---
type: concept
era: side-projects
tags: [rule-110, detector, verification]
date: 2026-05
---

# Structural glider detector

`compiler/glider_detect.py` in the [[Rule 110 compiler]]. Detects gliders by *dynamical signature* (period T, displacement D) rather than bit-pattern match. Required because [[Cook universality proof|Cook's crossing]] shifts each glider's local left_phase by the other glider's [[Cook glider width|width]], changing the post-crossing bit pattern.

Two variants:

- `is_stationary_glider(state_t, state_t_plus_T, anchor, extent, time_t)` — weak. Checks cells differ from standard ether AND match themselves over T steps. Fast but vulnerable to [[Phase-shifted ether]] false positives.
- `is_real_stationary_glider(...)` — strict. Same plus rejects all 14 Cook-shifted ether phases.

Same two-tier setup for displaced gliders: `find_displaced_glider` (weak) and `is_real_displaced_glider(snapshots, ..., n_periods=3)` (strict, multi-period persistence).

The weak versus strict gap is real: the [[Detector audit reversal]] discovered that every "Cook crossing" claim in the codebase had been weak-verified, and strict detection found *zero* real C2 survival at the gaps weak detection had blessed. The strict detector was the fix and produced the actually-real findings at gaps 36..49 ([[Cook crossing window]]).

## Connects to

- [[Cook ether lattice]]
- [[Phase-shifted ether]]
- [[Ether false-positive in glider detection]]
- [[Detector audit reversal]]
- [[Cook crossing window]]
- [[Rule 110 compiler]]
