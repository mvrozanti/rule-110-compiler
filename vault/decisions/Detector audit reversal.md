---
type: decision
era: side-projects
tags: [rule-110, detector, audit, reversal]
date: 2026-05-18
---

# Detector audit reversal

Mid-session in the [[Rule 110 compiler]] push, an audit of the weak `is_stationary_glider` / `find_displaced_glider` checks (`compiler/glider_detect.py`) revealed they cannot distinguish a real glider from [[Phase-shifted ether]]. For every Cook glider's `(period_t T, displacement D)`, the [[Cook ether lattice|lattice]] condition `4T + D ≡ 0 (mod 14)` holds — that's the definition of a glider. But it also means pure phase-shifted ether moving at displacement `D` over `T` steps satisfies the same self-match check the detector uses.

Material consequence: every "Cook crossing verified" claim made earlier in the session was a **weak-detector false positive**. The [[Structural glider detector|strict]] `is_real_stationary_glider` found 0 real C2 survivors at the 6 gap values the weak detector had blessed.

ADR `docs/decisions/0012-detector-audit-revision.md` records the reversal honestly per [[Honesty mandate]]. Tests retained as `weak`-tagged historical pins, alongside new `strict` tests that show the negative result.

The fix had two parts:
1. Strict detectors that reject all 14 phase shifts of ether.
2. [[EBAR_GAP=40 calibration]] — discovering the gap range where strict-real C2 survival genuinely happens (the [[Cook crossing window]] 36..49).

After the audit + calibration, the BF '++' headline test went from "5/8 weak survivors → unrevised would have been a false claim" to "**7/8 strict-real survivors**." Real progress, found by listening to the strict detector.

## Connects to

- [[Structural glider detector]]
- [[Phase-shifted ether]]
- [[Cook ether lattice]]
- [[Ether false-positive in glider detection]]
- [[Cook crossing window]]
- [[EBAR_GAP=40 calibration]]
- [[Honesty mandate]]
- [[Rule 110 compiler]]
