---
type: concept
era: side-projects
tags: [rule-110, cook, universality, theory]
date: 2026-05
---

# Cook universality proof

Matthew Cook's 2004 proof that [[Rule 110]] is computationally universal, by reducing the [[Cyclic tag system]] (CTS) — itself reducible from Turing machines — to a specific arrangement of [[Cook-faithful glider catalogue|Cook gliders]] in Rule 110's spacetime. The paper is `15-1-1.pdf` in the [[Rule 110 compiler]] repo.

The proof is famously **a poor implementation spec**. Cook proves the conditions are jointly satisfiable; he does not ship:
- bit-exact glider patterns (only pictures in Figure 4),
- the α/β-to-cell-coordinate translation,
- a collision lookup table,
- a worked end-to-end example,
- an algorithm for converting a CTS to an R110 initial condition.

Every empirical implementation has had to **redo Cook's empirical work** in machine-readable form. The vault note [[Cook-inspired vs Cook-faithful]] captures the spectrum of how literal the reproduction can be.

Key sub-mechanisms (Cook §3.5):
- **Crossing** ([[Cook crossing window]]) — moving data Ē crosses tape data C2 ; both survive with their local left_phase shifted.
- **Leader hits character** — 8 Ē × 4 C2 → emits acceptor (Y) or rejector (N) made of As.
- **Acceptor × component** → 2 moving-data Ēs.
- **Ossifier** — 16 As converts 4 moving-data Ēs into a new 4-C2 tape character. Implemented at the left of the tape; CTS state "consumed" tape symbols become Cook's "invisibles" floating leftward as a permanent history record.

## Connects to

- [[Rule 110]]
- [[Cyclic tag system]]
- [[Cook-faithful glider catalogue]]
- [[Cook ether lattice]]
- [[Cook glider width]]
- [[Cook crossing window]]
- [[Cook-inspired vs Cook-faithful]]
- [[Rule 110 compiler]]
