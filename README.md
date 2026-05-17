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
| 1 | `core/rule110.py` | not-started |
| 1 | `core/ether.py` | not-started |
| 2 | Cook gliders (C1, C2, A, B, E, Ebar) | not-started |
| 3 | verified collisions | not-started |
| 4 | `compiler/cts.py` pure simulator | not-started |
| 4 | `compiler/cts_to_r110.py` encoder | not-started |
| 5 | `compiler/tm_to_cts.py` (Neary-Woods) | not-started |
| 6 | `compiler/bf.py` + `compiler/bf_to_tm.py` | not-started |
| 7 | `runtime/evolve.py` + `runtime/decode.py` | not-started |
| 7 | end-to-end on `+`, `+++.`, `+[-]` | not-started |
| 8 | visualization (2-pane MVP) | not-started |
| 8 | visualization (4-pane full) | not-started |

A row flips to `verified` only when a green test proves it. `broken` is also a
valid state and must be named honestly.

## Quickstart

After Phase 1:

```sh
pytest tests/test_rule110.py tests/test_ether.py
```

After Phase 7 (the universality demonstration):

```sh
python scripts/verify_all.py
```

After Phase 8:

Open `viz/index.html` in a browser.

## See also

- `AGENTS.md` — project conventions for human and AI contributors
- `docs/pipeline.md` — pipeline diagram with per-arrow notes
- `docs/glider_atlas.md` — per-glider patterns and Cook citations (added in Phase 2)
- `docs/reference/working_rule110.html` — the only known-good Rule 110 sim from
  the previous attempt; kept as parity reference for the new Python core
- `15-1-1.pdf` — Cook's paper, the spec
