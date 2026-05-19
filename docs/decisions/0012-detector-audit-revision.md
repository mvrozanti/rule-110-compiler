# 0012 — Detector audit: most "Cook crossing" claims were weak-detector false positives

## Status

Accepted. **Material revision** of every prior Cook-collision claim in this repo.

## The bug

For every Cook glider `(period_t T, displacement D)` in the catalogue:

```
4 * T + D ≡ 0  (mod 14)
```

Verified for A (3,+2), B (4,-2), C2 (7,0), D (10,+2), Ē (30,-8), E (15,-4).

This is the lattice condition that makes them gliders in the first place
(they live on the ether's diagonal/vertical period). But it also means:

**Pure Cook-shifted ether at any phase satisfies the displacement check**
`state_t[anchor + j] == state_t_plus_T[anchor + D + j]` because ether
shifts left by `4T` per `T` steps, and `4T ≡ -D (mod 14)` puts the bits
back where the displacement detector compares.

Both `is_stationary_glider` and `find_displaced_glider` were therefore
**unable to distinguish a real glider from a Cook-shifted ether region**.

## Revisions

`compiler/glider_detect.py` adds two strict variants:

- `is_real_stationary_glider`: rejects all 14 Cook-shifted ether phases.
- `is_real_displaced_glider`: rejects all 14 Cook-shifted ether phases,
  verifies persistence across multiple periods.

Both pass unit-tested sanity (solo gliders accepted; pure / shifted
ether rejected).

## What this means for prior claims

| Prior claim | Honest reality under strict detection |
|---|---|
| `test_c2_x_ebar_crossing_both_gliders_survive` — "C2 stationary at anchor after Ebar pass" | Cells at c2_anchor are **phase-shifted ether**, not a real C2. C2 effectively destroyed; weak check fooled by ether match. |
| `test_eight_crossings_from_bf_plusplus_cts_inside_r110` — "≥5 Ys survive scanner" | Strict check finds **0/8** real Y survivors. The "5+ Cook crossings inside R110" headline was a weak-detector artefact. |
| `test_all_four_c2_survive_ebar_pass` — "4 C2s survive" | Same — phase-shifted ether at anchors, not C2. |
| 4-C2 × Ebar **A emission** | **Real**, position different from old detector. Confirmed under strict detection. |
| Ossifier (16 As) + 4 Ēs → **new stationary C-class glider** | **Real**. Test already used `is_real_stationary_glider`. |

## What survives the audit (genuinely Cook-verified)

1. **Cook-faithful glider catalogue propagation** (`tests/test_cook_gliders.py`)
   — direct placement + evolution, no detector involved. Untouched.
2. **A emission** from 4-C2 × Ebar (`tests/test_cook_compound.py::test_ebar_produces_a_real_a_glider_on_the_right`) — strict-detector verified.
3. **Ossifier creates new stationary C-class glider** (`tests/test_cook_compound.py::test_ossifier_creates_new_stationary_c_class_glider`) — strict-detector verified.

The C2 × Ebar **crossing** as Cook describes (both gliders survive) is
**NOT** empirically reproducing with our Cook-faithful C2 + Ebar
variants. The reaction destroys the C2 and produces phase-shifted
ether at the anchor.

## Implications for the end goal

The "5 CTS steps inside R110" target was previously claimed as
"5+ Cook crossings inside R110 from BF '++'." Under strict detection,
**zero** Cook crossings reproduce; the underlying primitive doesn't
work for our specific gliders. The end goal is **further** from
achievement than the prior session-headline ADR (0010) claimed.

Honest current state:
- 1 of Cook's §3.5 sub-reactions verified under strict detection
  (4-C2 × Ebar → A).
- 1 ossifier-class reaction verified under strict detection
  (16-A + 4-Ē → new stationary glider).
- 0 verified Cook §3.2.4 crossing collisions under strict detection.

## Forward path

Find the actual C2 variant or spacings where Cook's crossing
reproduces under strict detection, OR find a different Cook-class
glider whose crossing IS preserved. The same empirical search
framework now has a correct detector to drive it.
