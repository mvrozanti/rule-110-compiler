# 0004 — Cook-faithful glider variants found

## Status

Accepted. Reverses the structural pessimism in ADR 0003.

## Discovery

Today (later in session, after ADR 0003): the reason
`scripts/find_c_variants.py` and earlier search work found only width-0
gliders is that those scripts assumed standard ether on **both** sides
of the glider. A Cook width-W glider has different ether phases on its
two sides — its right halo matches ether **shifted by W cells**, not
standard ether.

A new search (`scripts/find_cook_variants.py`) sweeps the width
parameter W ∈ 0..13 and checks the right halo against ether shifted by
W. With this fix, Cook's specific widths are found:

  - **A glider, Cook width 6**: extent 6, L=4, delta=(1,0,1,1,1,0).
  - **C2 glider, Cook width 3**: extent 6, L=2, delta=(1,0,0,0,0,0).
    Multiple distinct variants exist within the (period=7, D=0, W=3)
    class — at least 9 — all valid period-(7,0) width-3 gliders.
  - **Ebar glider, Cook width 7**: extent 7, L=4,
    delta=(1,1,0,0,1,1,1).

These are codified in `core/cook_gliders.py` with `place_cook_glider`
that handles the right-side ether-phase shift. 9 propagation/halo
tests pass (`tests/test_cook_gliders.py`).

## Current state of the collision atlas

Cook's most-cited collision — C2 × Ebar crossing (§3.2.4) — does NOT
reproduce with the specific C2 and Ebar variants I selected, across
gap sweeps. Possible reasons:

1. Multiple width-3 C2 variants exist (we found 9). Cook's specific
   C2 may be one of the others.
2. The crossing requires specific α/β alignment that maps to specific
   cell offsets I haven't enumerated.
3. The crossing requires a specific PAIR of variants we haven't tried.

A partial cartesian sweep (5 C2 variants × 1 Ebar variant × 300 gaps)
was launched but did not complete in the session's compute budget.
Continuation is the next step.

## Effect on the 2026-05-31 deadline

This unblocks Plan A (Cook-faithful construction) from being structurally
impossible — the gliders exist; we just need to find the specific
configuration where Cook's documented collisions reproduce.

The path forward:

1. Continue the C2/Ebar variant cartesian sweep until a crossing is
   verified. Estimated 2-6 hours of CPU.
2. Once one crossing is verified, the same approach finds A4 × Ebar
   ossification, leader interactions, etc.
3. With ≥ 3 verified Cook collisions, build the §4 encoder.

Risk: if no variant pair produces a crossing, we still face a search
problem on the precise bit patterns Cook used. The cartesian sweep
gives us empirical signal either way.

The 2026-05-31 deadline remains under stress but is no longer blocked
on the structural obstacle named in ADR 0003.

## References

- `core/cook_gliders.py` — Cook-faithful glider catalogue.
- `scripts/find_cook_variants.py` — width-W search with two-phase ether.
- `tests/test_cook_gliders.py` — 9 propagation/halo tests.
- `Cook_2004_UniversalityInElementaryCellularAutomata.pdf` — Cook 2004, Figure 5 (widths), §3.2.4 (C2 × Ebar
  crossing collision).
