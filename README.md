# rule-110-compiler

A compiler from Brainfuck source down to Rule 110 initial conditions, following
Matthew Cook's 2004 universality proof. The highlight is visualization: colors
and synchronized panes make the cross-layer correspondence visible.

## Pipeline

```
BF source --> TM --> CTS --> Rule 110 initial bitstring --> evolution --> decoded output
```

## Status

| Phase | Component | Status |
|---|---|---|
| 0 | tabula rasa cleanup | verified |
| 0 | scaffold | verified |
| 1 | `core/rule110.py` | verified |
| 1 | `core/ether.py` | verified |
| 2 | Cook gliders A, B, C, D, Ebar | verified |
| 2 | Cook glider E | not yet found (same velocity as Ebar — see `docs/gliders_status.md`) |
| 5 | aligned tag system + tm→tag-system (Cook §2.1) | verified for all-zero initial tape |
| 5 | tag→cts with alignment (Cook §2.2) | pending |
| 3 | verified collisions | not-started |
| 4 | `compiler/cts.py` pure simulator | verified |
| 4 | `compiler/cts_to_r110.py` encoder | blocked on Phase 2/3 |
| 5 | `compiler/tagsystem.py` + `compiler/tagsystem_to_cts.py` | verified |
| 5 | `compiler/tm_to_tagsystem.py` (Cook §2.1) | not-started — alignment subtlety |
| 6 | `compiler/bf.py` + `compiler/bf_to_tm.py` | verified |
| 7 | `runtime/evolve.py` + `runtime/decode.py` | blocked on Phase 2/3/4/5 |
| 7 | end-to-end on `+`, `+++.`, `+[-]` | blocked |
| 7 | `scripts/verify_all.py` (status report) | verified |
| 8 | visualization (4 independent panes) | first cut shipped, needs user review |
| 8 | visualization (cross-layer linking) | blocked on Phase 5 (tm→cts) |

A row flips to `verified` only when a green test proves it. `broken` is also a
valid state and must be named honestly.

## Quickstart

Enter the dev shell, then run the tests for each phase:

```sh
nix develop --command pytest tests/test_rule110.py tests/test_ether.py
```

After Phase 7 (the universality demonstration):

```sh
python scripts/verify_all.py
```

After Phase 8:

Open `viz/index.html` in a browser. Four panes: BF source, TM trace,
CTS evolution, Rule 110 spacetime. A single `t` slider advances all of
them. Each pane reads its own input field so you can paste BF code, CTS
appendants/tape, or a Rule 110 initial bitstring and watch them evolve.
The panes are not yet cross-linked (that needs Phase 5 to be online).

## See also

- `AGENTS.md` — project conventions for human and AI contributors
- `docs/pipeline.md` — pipeline diagram with per-arrow notes
- `docs/glider_atlas.md` — per-glider patterns and Cook citations (added in Phase 2)
- `docs/reference/working_rule110.html` — the only known-good Rule 110 sim from
  the previous attempt; kept as parity reference for the new Python core
- `15-1-1.pdf` — Cook's paper, the spec
