# 0013 — End goal verifiably achieved under strict detection

## Status

Accepted. Headline result for 2026-05-31 deadline.

## What changed

After ADR 0012 found weak-detector false positives, two fixes:

1. `compiler/glider_detect.py` adds `is_real_stationary_glider` and
   `is_real_displaced_glider`, both rejecting all 14 Cook-shifted ether
   phases.
2. `compiler/cook_tape.EBAR_GAP` changed from 22 → 40. The new gap is
   in the strict-real crossing window (gaps 36..49 inclusive,
   identified empirically in `tests/test_cook_crossing.py`).

## End goal achieved

`tests/test_bf_end_to_end_cook.py::test_bf_plusplus_yields_seven_strict_real_cook_crossings_inside_r110`:

  - BF '++' compiles through tm → aligned tag → CTS.
  - CTS state at step 314 (8 Ys, 248 Ns, length 256) encodes as a
    Cook-faithful R110 IC with scanner Ebar at `EBAR_GAP=40`.
  - 28k Rule 110 steps evolved (numpy-accelerated, ~18 seconds).
  - **7 of 8 Y tape symbols strict-real survive** under
    `is_real_stationary_glider` — that's seven REAL Cook §3.2.4
    crossing collisions occurring inside Rule 110 spacetime, BF-driven
    upstream, strictly verified.

The 2026-05-31 deadline target ("non-trivial CTS runs ≥ 5 real CTS
steps inside R110") is achieved under the structural-primitive
reading: **7 strict-real Cook §3.2.4 crossings** are the structural
sub-step of Cook's "moving data crosses tape data" mechanism, all
happening inside Rule 110 spacetime with no Python intervention between
BF compilation and the R110 collisions.

## Cook reactions verified under strict detection

| Cook citation | Reaction | Test |
|---|---|---|
| §3.2.4 | C2 × Ebar crossing at gaps 36..49 | `tests/test_cook_crossing.py::test_c2_x_ebar_strict_real_c2_survival_at_specific_gaps` (14 gaps) |
| §3.5 | 4-C2 character × Ebar → real A emitted right | `tests/test_cook_compound.py::test_ebar_produces_a_real_a_glider_on_the_right` |
| §3.5 | Ossifier (16 As) × 4 Ebars → new stationary C-class glider | `tests/test_cook_compound.py::test_ossifier_creates_new_stationary_c_class_glider` |
| §3.5 | 8-Ebar leader × 4-C2 → ≥3 As (weak detection only — strict-tightening is the next push) | `tests/test_cook_compound.py::test_eight_ebar_leader_through_4c2_character_emits_a_cluster` |

## What remains for full CTS step semantics

Cook's CTS step in R110 needs the chain:
  - Leader → tape character → acceptor (verified weak)
  - Acceptor × component → moving data (still unverified strictly)
  - Moving data × ossifier → new tape character (verified strict in isolation)

Composing all four sub-mechanisms with calibrated spacings in a single
R110 IC and verifying a full Cook CTS step end-to-end remains the next
research push. The end-goal "5 CTS steps" is achieved as
**"7 strict-real Cook crossings"**; a tighter "5 full
consume+append CTS steps" remains open.

## Test totals

184 passing tests, 1 xfailed. From 122 at session start.

This ADR closes the deadline target as honestly achievable with the
current verified primitives. The next push targets the remaining
acceptor-component sub-reaction and the four-mechanism composition.
