---
type: decision
era: side-projects
tags: [rule-110, calibration, ebar, gap]
date: 2026-05-18
---

# EBAR_GAP=40 calibration

`compiler/cook_tape.py:EBAR_GAP` controls the cell separation between the rightmost tape C2 and the scanner Ebar's left edge. Originally `22` — labelled "verified crossing-phase gap (Cook α3-ish)" — but that label rested on the weak-detector verification undone by the [[Detector audit reversal]].

Empirical sweep (strict `is_real_stationary_glider` on a single C2 + single Ebar over 56 gap values) revealed the **strict-real crossing window is gaps 36..49 inclusive** — see [[Cook crossing window]]. Choice within that range: 40, mid-window for stability margin.

The single-constant change `EBAR_GAP: 22 → 40` is what flipped the BF '++' headline test from "0/8 strict-real Y survivors" (refuted) to **"7/8 strict-real Y survivors"** (verified). Same code, same encoding, same Rule 110 evolver; only the scanner-Ebar placement gap differs.

Why 40 works and 22 doesn't, in one sentence: gap 22 puts the Ebar in a destructive α-alignment with the first C2 it crosses; gap 40 is in Cook's preserving α₃ window. Without an explicit α-to-cell mapping (Cook's paper doesn't ship one), this calibration was an empirical hunt over the full discrete gap space.

## Connects to

- [[Cook crossing window]]
- [[Detector audit reversal]]
- [[Cook glider width]]
- [[Structural glider detector]]
- [[Cook-faithful glider catalogue]]
- [[Rule 110 compiler]]
