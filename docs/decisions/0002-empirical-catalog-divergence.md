# 0002 — Empirical glider catalogue diverges from Cook's width convention

## Status

Accepted. Documents a discovery that changes M3-M5's tractability.

## Context

Cook's universality construction (§4) names specific glider variants by
their **width**: a number mod 14 encoding the ether-phase offset between
the ether to the right of the glider and the extrapolated continuation of
the ether to the left. Cook's Figure 5 tabulates widths: A=6, B=8, C1=9,
C2=3, C3=11, D1=11, D2=5, Ē=7, etc.

Cook's tape-data construction uses **C2 specifically** (width 3). The
specific C variant matters because collisions with Ē, A4 ossifiers, and
acceptors/rejectors depend on the diagonal ether-phase relationships.

## Discovery (2026-05-17)

Empirically inspecting our verified catalogue (`test_alpha_beta.py`):

- Our A glider: extent 4 cells, period (3, +2). When we compute "width"
  as (ether-right-shift mod 14) by placing on clean ether, evolving one
  period, and finding the offset that makes the right-side cells match
  the time-shifted ether, the answer is **0**. Cook says A = 6.
- Our C glider: same procedure gives width **0**. Cook says C1=9, C2=3,
  C3=11. None match.
- Random-IC scan of 400 seeds (`scripts/find_c_variants.py`) for any
  C-class (period 7, stationary) variant: 16 distinct (width, extent)
  classes found. **All have width 0.**

We are not measuring "Cook's width" the same way Cook defines it. Either:

1. Our `place_glider` overlays the delta on standard ether, so the ether
   on both sides of the glider is by construction the SAME standard
   ether — making the "shift" always 0 in our coordinate system.
2. Cook's width is measured in a co-moving frame or relative to the
   glider's internal structure, not against absolute ether positions.
3. Cook's width definition is conventional shorthand for some other
   geometric invariant (e.g., the glider's extent mod 14 in a specific
   frame) and our measurement is technically correct but answers a
   different question.

Without a worked example in Cook's paper that gives both bit pattern AND
width for any specific glider, we cannot reconcile.

## Consequences for the 2026-05-31 deadline

The cell-spacing recipes Cook gives in §4 (e.g., `C2 18 C2 18 C2 14 C2`
for a Y character) are anchored to his width convention. We do not have
his width convention, so the cell-equivalent spacings will not transfer
literally. Specifically:

- Cook's `C2 18 C2` minimum-distance constraint translates to OUR
  C-variant minimum of 28 cells (`test_alpha_beta.py`), but the precise
  α-unit mapping (Cook's α2 vs α6 vs α18) is undetermined.
- The collisions Cook documents (A4 × Ē → C2; leader × tape-Y; etc.)
  depend on his specific glider variants. With our catalogue, the SAME
  abstract setup produces different output gliders or wider
  perturbations. `scripts/probe_collisions.py` shows A4 × Ē produces a
  structured ~230-cell perturbation, not a recognisable C in our
  catalogue.

This means M3 (Cook's core 8 collision atlas) cannot be delivered as
**Cook-faithful** — the gliders we have don't reproduce Cook's
collisions. Two honest paths forward:

A. **Find Cook-faithful variants.** Extend search for A with width 6,
   C with width 3 (C2), etc. This is more glider-search work, similar
   in spirit to the unfinished E hunt. Estimated time: weeks of CPU
   plus careful bit-pattern reconstruction from Cook's figures.

B. **Plan B: build a Cook-inspired but not Cook-faithful demo.** Use
   our catalogue as-is; characterize collisions empirically (any
   collision, whether Cook documents it or not); construct a CTS
   emulator whose dynamics are verifiable end-to-end inside Rule 110,
   even if the specific gliders/spacings don't match Cook's paper.

## Decision

We adopt Plan B for the 2026-05-31 deadline and keep Plan A as a
follow-on goal that requires its own deadline.

Plan B scope:

- M3 (2026-05-25): empirical collision atlas of OUR catalogue —
  document what collisions we can reproduce, what they produce. Includes
  C × Ē crossing (already done), C × Ē head-on residue, A4 × Ē residue,
  C × C and Ē × Ē minimum spacings (already done as `test_alpha_beta`).
- M4 (2026-05-28): the minimum verifiable CTS step inside R110. Likely
  a "delete-only" tag-system step (consume leftmost Y/N from tape) since
  appending requires Cook's full ossifier reflection mechanic.
- M5 (2026-05-31): end-to-end demo running ≥ 5 delete-only steps inside
  R110, decoded back to tape state.

Plan B is honest about limitations:
- It is NOT a proof of universality reproduction. Cook's universality
  requires CTS appending, which our delete-only model lacks.
- It IS a verifiable, observable, end-to-end demo of computation
  happening inside Rule 110 from a BF-derived starting tape.

## References

- `tests/test_alpha_beta.py` — width-0 measurement for C and Ē.
- `scripts/find_c_variants.py` — 16 classes of period-7 glider, all width 0.
- `Cook_2004_UniversalityInElementaryCellularAutomata.pdf` — Cook 2004, Figure 5 (glider widths), §4 (construction
  conditions using widths).
