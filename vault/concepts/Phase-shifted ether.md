---
type: concept
era: side-projects
tags: [rule-110, cook, ether, phase]
date: 2026-05
---

# Phase-shifted ether

Pure [[Cook ether lattice|ether]] at non-zero phase relative to the global reference. Bits at position `p` are `ETHER[(p + W) % 14]` for shift `W ∈ {0..13}`. There are 14 distinguishable phases; standard ether is `W = 0`.

Phase-shifted ether arises naturally between [[Cook-faithful glider catalogue|Cook gliders]] because each glider carries a non-zero [[Cook glider width]]. Place a C2 (width 3) on phase-0 ether → cells right of the C2 are phase-3 ether. Place an Ebar (width 7) to the right of that → cells right of the Ebar are phase-10 ether. Cumulative widths add mod 14 along the tape.

The trap: pure phase-shifted ether *looks like a stationary period-7 structure* and *also satisfies the period-30 displacement-(−8) check*. Worse: it satisfies the check **for every Cook glider's (T, D)** because `4T + D ≡ 0 (mod 14)` is the [[Cook ether lattice|lattice]] condition that defines a glider. Naive detectors confuse phase-shifted ether with a real glider — see [[Ether false-positive in glider detection]].

The fix: [[Structural glider detector]] strict variants reject all 14 phase shifts.

## Connects to

- [[Cook ether lattice]]
- [[Cook glider width]]
- [[Ether false-positive in glider detection]]
- [[Structural glider detector]]
- [[Detector audit reversal]]
- [[Two-phase ether placement]]
- [[Rule 110 compiler]]
