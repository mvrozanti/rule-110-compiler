# 0010 — Session headline summary, 2026-05-18

## What this session shipped

From `commit ca0f05b` (first Cook crossing) through `commit f0670a3`
(three cook collisions verified), the session moved from 122 to 163
passing tests and shipped:

### Cook-faithful glider catalogue
- `core/cook_gliders.py`: A (width 6), C2 (width 3), Ebar (width 7)
  with two-phase ether placement via `place_cook_glider`.

### Structural detectors
- `compiler/glider_detect.py`: `is_stationary_glider` and
  `find_displaced_glider`. Detect gliders by period+displacement
  signature, not bit pattern — essential because Cook crossings shift
  each glider's local left_phase, changing post-collision bit patterns.

### Numpy-accelerated evolver
- `core/rule110_fast.evolve_numpy`: 100× speedup over the pure-Python
  step. Made the 28k-step BF '++' → 8-crossings demo runnable in 18s
  (was 42 min).

### Three Cook collisions verified

1. **Cook §3.2.4 C2 × Ebar crossing** —
   `tests/test_cook_crossing.py` (8 tests)
2. **Cook §3.5 4-C2 character × Ebar → A emitted** —
   `tests/test_cook_compound.py::test_ebar_produces_an_a_glider_on_the_right`
3. **Cook §3.5 8-Ebar leader × 4-C2 character → ≥3 As** —
   `tests/test_cook_compound.py::test_eight_ebar_leader_through_4c2_character_emits_a_cluster`

### Cook-faithful CTS tape encoding
- `compiler/cook_tape.encode_tape` and `decode_tape`: encode a Y/N CTS
  tape as a Cook-faithful R110 IC with optional scanner Ebar.

### End-to-end BF → R110 universality demo
- `tests/test_bf_end_to_end_cook.py::test_eight_crossings_from_bf_plusplus_cts_inside_r110`
  — BF '++' compiles through tm → aligned tag → CTS, the CTS state at
  step 314 (8 Ys) encodes as a Cook-faithful R110 IC with a scanner
  Ebar, and 28k Rule 110 steps produce **≥5 verified Cook §3.2.4
  crossings inside R110 spacetime**, all driven by BF compilation
  upstream with no Python intervention between BF and the R110
  collisions.

### Multi-C2 traversal
- `tests/test_multi_c2_traversal.py`: ten sequential Cook crossings in
  one Rule 110 evolution.

### Cook-faithful round-trip
- `tests/test_cook_tape.py` + `tests/test_bf_end_to_end_cook.py`: BF
  programs and arbitrary CTS tapes encode to Cook-faithful R110 ICs
  and round-trip through evolution + decode without scanner.

## Where the deadline stands (per ADR 0007/0008)

The 2026-05-31 plan target "non-trivial CTS runs ≥ 5 real CTS steps
inside R110" is **achieved as 5+ Cook collisions inside R110 driven by
BF compilation** (the structural-primitive reading). It is **not yet
achieved as 5 full CTS steps with consume + append** (which would
require the ossification chain Cook describes in §3.5: acceptor ×
component → moving-data Ebars; moving-data × A4 → new C2). The
remaining empirical work to bridge that gap is well-defined and
tractable with the now-built tools (structural detector + fast
evolver) but is more research time than this session had.

163 tests pass, 1 xfailed. Working tree clean.
