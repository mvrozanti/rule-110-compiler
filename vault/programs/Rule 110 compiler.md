---
type: program
era: side-projects
tags: [rule-110, compiler, brainfuck, cellular-automaton, cook]
date: 2026-05
---

# Rule 110 compiler

A Brainfuck → Rule 110 initial-conditions compiler at `/home/m/Projects/rule-110-compiler`, built around Matthew Cook's 2004 universality proof of the elementary cellular automaton [[Rule 110]]. The mission: take BF source through TM → 2-tag → CTS → glider arrangement, evolve Rule 110 forward, and decode the result back.

This project has been **restarted multiple times**. Earlier attempts shipped scaffolding without verifying any layer empirically, then collapsed under the load of un-verified primitives. The current incarnation enforces an [[Honesty mandate]] — no layer claims `verified` without a green test that fails loudly when the layer is wrong.

The pipeline runs:

```
BF source → TM → CTS → Cook-faithful R110 IC → evolution → decoded tape
```

Big arcs of progress:

- [[Cook-faithful glider catalogue]] — A (width 6), C2 (width 3), Ē (width 7), placed via [[Two-phase ether placement]].
- [[Cook crossing window]] — C2 × Ē strict-real crossing happens only at gap 36..49.
- [[Structural glider detector]] — needed because every Cook glider's `(T, D)` satisfies `4T + D ≡ 0 (mod 14)`, so weak displacement checks confuse real gliders with [[Phase-shifted ether]].
- [[Detector audit reversal]] — discovering the above invalidated months of "verified Cook crossings" that were ether false positives.
- [[EBAR_GAP=40 calibration]] — the scanner-Ebar tape spacing that produced 7 strict-real Cook crossings inside R110 from BF '++'.

Headline result: **BF '++' yields 7 strict-real Cook §3.2.4 crossings inside R110.** End goal for the 2026-05-31 deadline target met under the structural-primitive reading.

## Connects to

- [[Rule 110]]
- [[Cook universality proof]]
- [[Cook-faithful glider catalogue]]
- [[Cook crossing window]]
- [[Cook glider width]]
- [[Cook ether lattice]]
- [[Phase-shifted ether]]
- [[Structural glider detector]]
- [[Two-phase ether placement]]
- [[Detector audit reversal]]
- [[EBAR_GAP=40 calibration]]
- [[Cook-inspired vs Cook-faithful]]
- [[Ether false-positive in glider detection]]
- [[42-minute test ran on slow python evolver]]
- [[Glider E unfound after 172k-pattern sweep]]
- [[Honesty mandate]]
- [[Don't stop until goal reached]]
