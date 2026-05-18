# rule-110-compiler

A compiler from Brainfuck source down to Rule 110 initial conditions,
following Matthew Cook's 2004 universality proof. The highlight is
visualization: colors and synchronized panes make the cross-layer
correspondence visible.

## Pipeline

```
BF source --> TM --> tag system --> CTS --> Rule 110 IC --> evolution --> output
```

## Status

136 tests pass (1 xfailed). Each row of the table flips to `verified` only
when a green test proves it. `not yet` means the path forward is clear but
the code/proof is empirically pending.

| Phase | Component | Status |
|---|---|---|
| 0 | tabula rasa cleanup + scaffold | verified |
| 1 | `core/rule110.py` + `core/ether.py` | verified |
| 2 | Cook gliders A, B, C, D, Ebar (5 of 6, width 0 variants) | verified |
| 2 | Cook glider E | not yet found (see `docs/gliders_status.md`) |
| 2 | Cook-faithful A (width 6), C2 (width 3), Ebar (width 7) | **verified** |
| 3 | Cook §3.2.4 C2 × Ebar **crossing collision** (with phase shift) | **verified** |
| 3 | Structural glider detectors (period/displacement-based) | **verified** |
| 3 | `scripts/collide.py` sandbox | shipped |
| 3 | empirical collision fixtures (C x Ē crossing, parallels) | **verified** |
| 3 | α/β calibration (C×C min 28, Ē×Ē min 42, placement quantum 14) | **verified** |
| 3 | C × Ē head-on residue characterised (NOT a Cook §3.2.4 crossing) | **verified** |
| 3 | full Cook collision atlas (s3.3-s3.5) | not yet |
| 4 | `compiler/cts.py` pure CTS simulator | verified |
| 4 | `compiler/cts_to_r110.py` state-encoding round-trip | **verified** |
| 4 | `compiler/cts_to_r110.py` collision-driven CTS steps in R110 | not yet |
| 5 | tag system + tag→CTS (1-tag) | verified |
| 5 | TM → aligned tag (Cook §2.1, all-zero initial tape) | verified |
| 5 | aligned tag → CTS with alignment prefix (Cook §2.2) | verified |
| 5 | end-to-end BF → TM → tag → CTS for `+` (manual 2-sym TM) | verified |
| 5 | 2-symbol BF → CTS chain on arbitrary programs | not yet |
| 6 | `compiler/bf.py` + `compiler/bf_to_tm.py` (8-symbol TM) | verified |
| 6 | `compiler/bf_to_2sym_tm.py` (2-symbol TM, {0,1} cells) | **verified** |
| 7 | `scripts/verify_all.py` status reporter | verified |
| 7 | `runtime/evolve.py` + `runtime/decode.py` | **verified** |
| 7 | end-to-end BF → R110 IC → evolve → decode round-trip | **verified** |
| 7 | CTS *step dynamics* executed inside R110 (full Cook §4) | not yet |
| 8 | 4-pane visualization with demo dropdown | shipped |
| 8 | cross-pane hover linking | not yet (encoder now emits region_map) |

## Quickstart

Enter the dev shell, then run the verifier:

```sh
nix develop --command python -m scripts.verify_all
```

Run a specific phase's tests directly:

```sh
nix develop --command pytest tests/test_gliders.py -v
nix develop --command pytest tests/test_end_to_end.py -v
```

Open the visualization:

```sh
xdg-open viz/index.html
```

The viz has four panes: BF source, TM trace, CTS evolution, Rule 110
spacetime. A `t` slider advances them all. The `demo…` dropdown picks
matching content for all panes; you can also paste BF code, a CTS spec,
or a Rule 110 initial bitstring / glider-placement string
(e.g. `A@30,Ebar@140`).

## What landed in this round

The pipeline now compiles end-to-end *in shape*:

```
BF source
  -> 2-symbol Turing machine     (compiler/bf_to_2sym_tm.py)
  -> aligned 2-tag system        (compiler/tm_to_tagsystem.py, Cook §2.1)
  -> cyclic tag system           (compiler/tagsystem_to_cts.py, Cook §2.2)
  -> CTS state                   (compiler/cts.py run to terminal)
  -> Rule 110 IC + region_map    (compiler/cts_to_r110.py)
  -> Rule 110 evolution          (runtime/evolve.py)
  -> decoded CTS tape            (runtime/decode.py)
```

`tests/test_end_to_end.py` chains every layer and asserts the round-trip
agrees with the upstream simulator.

The empirical collision atlas has its first four entries
(`tests/test_collisions.py`): the **C × Ē crossing collision** — central
to Cook's "moving data crosses tape data" construction — is verified at
offsets ≥ 23 with our verified glider patterns. Three parallel-pair
fixtures (A-A, C-C, Ē-Ē) confirm those gliders propagate independently
when not in collision range.

## What's still pending

The remaining work is concentrated on two genuinely-research-grade tasks:

1. **Cook glider E.** A 6th glider in Cook's catalog with the same
   velocity as Ē (-0.267) but period 15 instead of 30. Width-14 exhaustive
   sweeps over all 14 ether phases produced zero hits with strict halo
   verification. The next escalations
   (`scripts/exhaustive_e_search_constrained.py` over width 19,
   `scripts/long_random_e.py` over long random ICs) are coded but only
   sample subsets of the search space. The construction can avoid E
   (Cook's encoding uses C / Ē / A primarily), but completing the catalog
   would close phase 2.

2. **Collision-driven CTS step dynamics inside Rule 110.** Cook §3.3-§3.5
   documents ~30 collisions used by the construction (leaders firing,
   primary/standard components accepted or rejected, ossifiers producing
   new tape data). Building this atlas is empirical work: for each
   collision, place the participating gliders at Cook's α/β distances on
   ether, evolve, verify the produced glider set matches Cook's claim,
   codify as a test fixture. Today we have 4 such fixtures
   (`tests/test_collisions.py`); a faithful Cook §4 encoder needs the full
   set.

The round-trip pipeline today demonstrates the *encoding correspondence*
of every layer with green tests. CTS step dynamics execute in Python; the
unfinished work is moving that dynamics into Rule 110's spacetime, which
requires (2) above.

## See also

- `AGENTS.md` — project conventions for human and AI contributors
- `docs/pipeline.md` — pipeline diagram with per-arrow notes
- `docs/gliders_status.md` — per-glider verification state
- `docs/decisions/0001-tm-to-cts-reduction.md` — why Cook §2.1+§2.2 over
  Neary-Woods 2006
- `docs/reference/working_rule110.html` — the only known-good Rule 110 sim
  from the previous attempt; kept as parity reference
- `15-1-1.pdf` — Cook's 2004 paper, the spec
