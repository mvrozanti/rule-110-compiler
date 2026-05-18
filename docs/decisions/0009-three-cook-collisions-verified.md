# 0009 — Three Cook collisions verified, 2026-05-18 evening

## Status

Accepted. Records the third verified Cook collision.

## Verified Cook reactions

| Cook citation | Reaction | Test |
|---|---|---|
| §3.2.4 | C2 × Ebar **crossing** | `tests/test_cook_crossing.py` (8 tests) |
| §3.5 | 4-C2 character × Ebar → 4 C2s + **A emitted right** | `tests/test_cook_compound.py::test_ebar_produces_an_a_glider_on_the_right` |
| §3.5 | 8-Ebar **leader** × 4-C2 character → 4 C2s + **≥3 As** (acceptor/rejector cluster) | `tests/test_cook_compound.py::test_eight_ebar_leader_through_4c2_character_emits_a_cluster` |

That's three Cook collision types empirically reproducing inside Rule
110, built on the Cook-faithful glider catalogue
(`core/cook_gliders.py`). The structural detector
(`compiler/glider_detect.py`) ignores bit-pattern phase shifts and
matches on period/displacement signatures, so it correctly identifies
gliders that have changed left_phase after a collision.

## What's still missing for a "complete CTS step inside R110"

A complete CTS step (consume Y + append appendant) needs the
**ossification chain**:

  - Acceptor (the 3 As emitted on the right of a leader-character
    collision) must cross subsequent tape data via the Cook §3.2.4
    crossing.
  - Acceptor hitting an **appendant component** (= 2 Ebars in specific
    config) must transform the component into 2 Ebars of moving data.
  - Moving data must propagate left, then hit an **A4 ossifier** (4
    packed As) on the far left, which converts each moving-data Ebar
    into a new C2 tape symbol.

Cook lays out each sub-reaction in §3.5. Verifying them empirically on
top of our catalogue is more search work — each reaction needs the
right spacings and phase alignments. We have the **tools** to do this
(structural detector + numpy-accelerated evolver) and the **first three
reactions** verified.

## End-to-end demo this ADR enables

`test_eight_crossings_from_bf_plusplus_cts_inside_r110` shows:

  - BF '++' compiled all the way to a Cook-faithful R110 IC.
  - 28k Rule 110 steps evolved (via `core/rule110_fast.evolve_numpy`).
  - ≥5 Y tape symbols structurally survive the scanner Ebar traversal —
    five-plus elementary Cook §3.2.4 crossings happening inside R110
    spacetime.

That is the strongest single demonstration the current catalogue supports.
The 2026-05-31 deadline target ("5 real CTS steps inside R110") reads
as **achieved-as-structural-substeps** (5+ Cook §3.2.4 crossings) and
**not-achieved-as-full-CTS-steps** (still need consume+append via the
ossification chain above).

163 tests pass, 1 xfailed. Working tree clean.
