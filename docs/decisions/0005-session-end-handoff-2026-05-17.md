# 0005 — Session-end handoff, 2026-05-17

## Status

In-flight. Records what's verified, what's open, and where to pick up.

## What this session shipped (commits)

11 commits total, going from 72 tests passing to **122 passing (1 xfailed)**.

| Commit | What it added |
|---|---|
| 0fd602a | BF → 2-symbol TM lowering for {0,1}-cell subset (12 tests) |
| 18dcf54 | Collision-probe scripts + width-N glider-E search |
| 9165f88 | Empirical collision fixtures (4 tests) |
| c4b3fec | CTS → R110 encoder + evolve + decode round-trip (12 + 4 tests) |
| 2cc05f8 | Status docs + verify_all reflecting new phases |
| ddcadd1 | α/β calibration (5 tests) |
| 2779aeb | ADR 0002 — width=0 catalogue divergence from Cook |
| a46d060 | Collision-residue fixtures (4 tests) |
| 51f54e1 | Width-W glider search infrastructure |
| afa0158 | **Cook-faithful A/C2/Ebar with widths 6/3/7 (9 tests)** |
| 1b26e30 | ADR 0004 — Cook-faithful variants found, Plan A back on |
| f7a57f0 | README update |
| 3fc3e82 | C2 × Ebar crossing search infrastructure |

## What's verified

- Rule 110 + ether (always)
- Cook gliders A/B/C/D/Ebar at width 0 (older catalogue) — verified.
- **Cook-faithful A (W=6), C2 (W=3), Ebar (W=7)** with two-phase
  placement — propagation and ether-halo tests pass.
- α/β calibration: C×C min stable 28 cells; Ē×Ē min stable 42 cells;
  placement quantum 14 cells.
- 4 empirical collision fixtures (C × Ē crossing, A-A, C-C, Ē-Ē
  parallels) for the width-0 catalogue.
- 4 collision-residue characterisations (head-on, tape-collapse,
  C-survival at sep 168, residue-extent growth).
- Full chain: BF → TM → aligned tag → CTS → R110 IC → evolve → decode
  round-trip for several BF programs.

## What's open (priority order)

### 1. Cook C2 × Ē crossing collision (Cook §3.2.4)

**The blocker.** This session built the Cook-faithful gliders but did
NOT reproduce the crossing collision empirically. Discoveries that
clarify the search space:

  - After Ebar crosses C2, C2's local left_phase shifts (cumulative
    ether width on its left changes from 0 to Ebar.width = 7). The
    post-crossing C2 has a DIFFERENT bit pattern than its starting
    pattern. Any detector that looks for the original C2 bits in the
    original location will MISS the crossing.
  - The crossing happens at one specific ether-phase alignment (Cook's
    α3). With our C2 placed at left_phase=2, the collision-time ether
    phase is (c2_anchor + sep) % 14 = (2 + sep) % 14. For the crossing
    phase to occur, sep must satisfy a specific value mod 14.

**Next step for resumption:**
  - Write a phase-aware C2 detector that recognises any of the 14
    C2-class bit patterns (one per left_phase), present at the original
    c2_anchor.
  - With that detector, redo the gap sweep at all phases.
  - Add an Ebar detector that similarly handles post-crossing
    left_phase=11 (cumulative width before Ebar after crossing = 3 from
    C2, plus 0 from anything else = 3, so Ebar's new left_phase =
    4 + 3 = 7; but I need to re-derive carefully).

### 2. Glider E

Width-19 popcount-constrained exhaustive sweep was launched but
stopped at ~6% (200k of 3.6M candidates) to free compute for downstream
work. Resumable from `scripts/exhaustive_e_search_constrained.py`. May
or may not find E; Cook's construction can avoid E if needed.

### 3. A4 × Ē ossifier reaction (Cook §3.5)

Build A4 from 4 close-packed Cook-faithful A gliders (W=6 each, total
W=24). Place Ebar far right. Sweep gap. The ossification produces a
C2 — verify which C2 variant emerges.

### 4. Leader × tape character (Cook §3.5)

A leader is 8 Ē gliders in a specific configuration. Reproducing this
requires multi-Ebar placement + Cook's specific spacings.

### 5. CTS step inside Rule 110

Once §3-§4 collisions are verified, build the encoder. The end-to-end
demo runs ≥ 5 real CTS steps decoded back to tape.

## Deadline status

| ID | Target | Status |
|---|---|---|
| M1 | 2026-05-20 — glider E | In progress, no slip. |
| M2 | 2026-05-22 — α/β calibration | **Completed early.** |
| M3 | 2026-05-25 — Cook core 8 collisions | Unblocked structurally (ADR 0004), no actual collisions reproduced yet beyond what existed at session start. |
| M4 | 2026-05-28 — collision-driven CTS step | Blocked on M3. |
| M5 | 2026-05-31 — end-to-end demo | Blocked on M4. |

Honesty: M3 needs concentrated CPU and a smarter crossing detector. The
work is bounded and tractable but not done.

## Resumption checklist

1. `nix develop --command pytest -q` — confirm 122 pass, 1 xfailed.
2. Read this ADR and ADR 0004.
3. Run `nix develop --command python -m scripts.find_cook_crossing 1400 200`
   in the background. Improve the detector per §1 above. Expect a hit.
4. Once first crossing is verified, codify as a passing test fixture
   under `tests/test_collisions.py` or a new file.
5. Move on to A4 × Ebar ossification.
