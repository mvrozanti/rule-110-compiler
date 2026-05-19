---
type: incident
era: side-projects
tags: [rule-110, detector, ether, false-positive]
date: 2026-05-18
---

# Ether false-positive in glider detection

For every [[Cook-faithful glider catalogue|Cook glider]] (period `T`, displacement `D`), the [[Cook ether lattice|lattice]] condition holds:

```
4T + D ≡ 0 (mod 14)
```

That is the very condition that makes a stable glider on the 14-cell-period, 4-cell-per-step ether possible. But it has a corollary the [[Rule 110 compiler]] detector code missed for an embarrassing stretch:

**Pure [[Phase-shifted ether|phase-shifted ether]] satisfies the displacement self-match check at every Cook glider's (T, D).**

State at time `t` at position `p` in shifted ether: `ether_cell(p + W + 4t)`. State at time `t + T` at position `p + D`: `ether_cell(p + D + W + 4(t + T))` = `ether_cell(p + W + 4t + (4T + D))`. With `4T + D ≡ 0 mod 14`, that equals the original. The displacement check `state_t[anchor + j] == state_t_plus_T[anchor + D + j]` is satisfied by pure ether — for **every** Cook glider's (T, D), at **every** of the 14 phase shifts.

The naive `is_stationary_glider` / `find_displaced_glider` could not distinguish a real glider from a region of phase-shifted ether. Months of "Cook crossing verified" claims were weak-detector positives produced by the [[Cook glider width|cum_w shift]] in the scanner Ebar's wake.

> [!fix]
> [[Structural glider detector|`is_real_stationary_glider` and `is_real_displaced_glider`]] reject all 14 phase shifts. Run the audit; the headline test went from a refuted claim to a real one once the strict detectors were used. [[Detector audit reversal]].

> [!aftermath]
> The strict-detector replay also revealed the [[Cook crossing window]] at gaps 36..49 — empirically known only after the audit forced the question.

## Connects to

- [[Cook ether lattice]]
- [[Phase-shifted ether]]
- [[Structural glider detector]]
- [[Detector audit reversal]]
- [[Cook crossing window]]
- [[EBAR_GAP=40 calibration]]
- [[Honesty mandate]]
- [[Rule 110 compiler]]
