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

71 tests pass (1 xfailed). Each row of the table flips to `verified` only
when a green test proves it. `not yet` means the path forward is clear but
the code/proof is pending.

| Phase | Component | Status |
|---|---|---|
| 0 | tabula rasa cleanup + scaffold | verified |
| 1 | `core/rule110.py` + `core/ether.py` | verified |
| 2 | Cook gliders A, B, C, D, Ebar (5 of 6) | verified |
| 2 | Cook glider E | not yet found (see `docs/gliders_status.md`) |
| 3 | `scripts/collide.py` sandbox | shipped |
| 3 | documented Cook collision atlas | not yet |
| 4 | `compiler/cts.py` pure simulator | verified |
| 4 | `compiler/cts_to_r110.py` encoder | blocked on Phase 2 (E) + Phase 3 |
| 5 | tag system + tag→CTS (1-tag) | verified |
| 5 | TM → aligned tag (Cook §2.1, all-zero initial tape) | verified |
| 5 | aligned tag → CTS with alignment prefix (Cook §2.2) | verified |
| 5 | **end-to-end BF → TM → tag → CTS for `+`** | **verified** |
| 5 | multi-cell BF → 2-symbol TM | not yet (unary encoding pass) |
| 6 | `compiler/bf.py` + `compiler/bf_to_tm.py` (8-symbol TM) | verified |
| 7 | `scripts/verify_all.py` status reporter | verified |
| 7 | end-to-end BF → R110 evolution | blocked on Phase 2 (E) + Phase 3 + Phase 4 |
| 8 | 4-pane visualization with demo dropdown | shipped, awaiting user review |
| 8 | cross-pane hover linking | blocked on Phase 4 emitting region_map |

## Quickstart

Enter the dev shell, then run the verifier:

```sh
nix develop --command python -m scripts.verify_all
```

Run a specific phase's tests directly:

```sh
nix develop --command pytest tests/test_gliders.py -v
nix develop --command pytest tests/test_chain_bf_to_cts.py -v
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

## What landed

- All 5 of 6 Cook gliders (A, B, C, D, Ebar) are present in `core/gliders.py`
  with minimal bit-pattern deltas, and each passes a propagation test that
  evolves it for 4 periods and checks it reappears at the expected
  displacement. The 6th glider (E) shares Ebar's velocity and was not
  isolated in 2000-seed random-IC sweeps nor 2-glider collision sweeps;
  its natural width per Cook is 11+8 cells, likely exceeding the 19-cell
  search window we exercised.
- The pipeline above the Rule 110 layer compiles end-to-end:
  `BF "+"` → 2-symbol TM → aligned 2-tag system → cyclic tag system,
  with the CTS terminating in finite steps. `tests/test_chain_bf_to_cts.py`
  asserts this.
- The visualization (browser-based, no server) renders all four layers
  with consistent color per concept (each glider gets a hue from Cook's
  Figure 4; ether recedes to dark gray; computation pops to bright).

## What's still pending

Three concrete blockers between here and the universality demo:

1. **Cook glider E.** A 6th glider in Cook's catalog. Not strictly needed
   for the simplest CTS encodings (which use C / Ē primarily) but
   completes the set.
2. **Verified collision atlas.** Cook §3.3-§3.5 documents a small set of
   glider collisions that the CTS encoder relies on. The collision
   sandbox (`scripts/collide.py`) exists; the documented collisions are
   not yet encoded as test fixtures.
3. **CTS → Rule 110 encoder.** Once (2) lands, this places C gliders for
   tape symbols and Ē/A gliders for "leaders" and "ossifiers" at
   Cook ether-distances. Then `runtime/evolve.py` and `runtime/decode.py`
   close the loop on `+`, `+++.`, `+[-]`.

## See also

- `AGENTS.md` — project conventions for human and AI contributors
- `docs/pipeline.md` — pipeline diagram with per-arrow notes
- `docs/gliders_status.md` — per-glider verification state
- `docs/decisions/0001-tm-to-cts-reduction.md` — why Cook §2.1+§2.2 over
  Neary-Woods 2006
- `docs/reference/working_rule110.html` — the only known-good Rule 110 sim
  from the previous attempt; kept as parity reference
- `15-1-1.pdf` — Cook's 2004 paper, the spec
