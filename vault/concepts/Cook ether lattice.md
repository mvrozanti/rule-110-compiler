---
type: concept
era: side-projects
tags: [rule-110, cook, ether, lattice]
date: 2026-05
---

# Cook ether lattice

The Rule 110 background. Spatial period **14**, temporal period **7**, translating **4 cells left per step**. After 7 steps the pattern has shifted 28 cells (2 spatial periods) and returns to itself.

Exact pattern: `(1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0)` — `core/ether.py:ETHER`. A prior incarnation of the [[Rule 110 compiler]] used a different 14-bit string that did **not** reproduce under Rule 110 — a load-bearing example of why every primitive needs an empirical test ([[Honesty mandate]]).

The lattice is what makes "gliders" a meaningful concept: a glider is a self-consistent disturbance that lives on this lattice and reappears at a fixed displacement after a fixed number of steps. Every Cook glider's `(period_t T, displacement D)` satisfies the lattice condition:

```
4T + D ≡ 0 (mod 14)
```

That algebra has a consequence: pure ether *moving at any displacement* trivially satisfies the displacement check that a glider should satisfy. This is the [[Ether false-positive in glider detection]] trap — see [[Structural glider detector]] for the resolution.

## Connects to

- [[Rule 110]]
- [[Cook universality proof]]
- [[Cook-faithful glider catalogue]]
- [[Cook glider width]]
- [[Phase-shifted ether]]
- [[Ether false-positive in glider detection]]
- [[Structural glider detector]]
- [[Honesty mandate]]
- [[Rule 110 compiler]]
