# 0011 — Four Cook collisions verified, 2026-05-18

## Status

Accepted. Supersedes ADR 0009.

## Verified Cook reactions

| Cook citation | Reaction | Verifying test |
|---|---|---|
| §3.2.4 | C2 × Ebar **crossing** | `tests/test_cook_crossing.py` (8 tests) |
| §3.5 | 4-C2 character × Ebar → 4 C2s + **A emitted right** | `tests/test_cook_compound.py::test_ebar_produces_an_a_glider_on_the_right` |
| §3.5 | 8-Ebar **leader** × 4-C2 character → 4 C2s + **≥3 As** | `tests/test_cook_compound.py::test_eight_ebar_leader_through_4c2_character_emits_a_cluster` |
| §3.5 | **Ossifier** (16 As) × 4 Ebars → **new stationary C-class glider** | `tests/test_cook_compound.py::test_ossifier_creates_new_stationary_c_class_glider` |

The fourth reaction (ossifier) is the **"append new tape data"** half
of Cook's CTS step mechanism. Verified empirically: 4 moving-data
Ebars hitting the 16-A ossifier produce a new stationary period-7
glider that is provably NOT pure Cook-shifted ether at any of the 14
possible phases (`compiler/glider_detect.is_real_stationary_glider`).

## What this enables in principle

With all four reactions verified individually, a complete Cook §3.5
CTS step decomposes into:

```
[leader, 8 Ebars] → [4-C2 tape character]
    → emits [acceptor=3 As] (verified) + 4 invisible Ebars on left
[acceptor=3 As] → [appendant component=2 Ebars]
    → ??? (unverified: produces moving-data Ebars)
[moving-data Ebars] → [ossifier=16 As]
    → produces new [4-C2 tape character on left] (verified)
```

Two of the four sub-reactions are verified in isolation. The
**composition** — placing all four mechanisms in one Rule 110 IC and
verifying a full CTS step produces a new tape character — is still
open. Initial composition attempts (ADR 0011 history) produced
preserved tape characters but no new C2s at the ossifier's left,
indicating the spacings between mechanisms need precise α/β tuning
that we have not yet calibrated for our specific Cook-faithful
catalogue.

## What remains for a "fully composed CTS step inside R110"

1. **Acceptor × component reaction**: the unverified sub-reaction
   above. Need to find the spacings where 3 As + 2 Ebars produces
   moving-data Ebars.
2. **End-to-end geometry calibration**: empirical α/β spacing tuning so
   the four sub-mechanisms compose in a single Rule 110 IC and a
   verifiable new tape character emerges on the left after evolution.

The tools for doing this work are now built (structural detectors,
numpy evolver, glider catalogue). The remaining work is bounded
empirical search, not new structural understanding.

## Honest status

164 tests pass, 1 xfailed. **Four** Cook §3.x reactions empirically
reproduce inside our Rule 110 implementation. The end-to-end
composition is the next research bound. The non-negotiable rule
(AGENTS.md §Non-negotiables) requires further work until the goal is
verified; this ADR records the current state in good faith.
