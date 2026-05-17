# 0001 — TM → CTS via Neary-Woods 2006

## Status

Accepted. Implements Phase 5.

## Context

Cook's 2004 paper proves Rule 110 universality by reducing CTS to Rule 110. To
run a Turing machine in Rule 110, we still need TM → CTS. Cook's own paper does
not give a direct, complete TM → CTS construction; his §5 sketches a
TM-via-tag-system route that is intricate and lightly documented.

Neary and Woods, "Small fast universal Turing machines" (Theoretical Computer
Science, 2006), give a clean reduction from any TM to a CTS with polynomial-time
slowdown and explicit size bounds. Multiple independent re-implementations
exist for cross-reference.

## Decision

Use the Neary-Woods 2006 TM → CTS reduction at the Phase 5 boundary. The Rule
110 layer (Phases 1-4) remains pure Cook.

## Consequences

- The composition `BF → TM → (Neary-Woods) → CTS → (Cook) → Rule 110` is
  universal end-to-end.
- Strict "Cook-only" purity is relaxed at exactly one stage. AGENTS.md calls
  this out under "Cook faithfulness."
- The polynomial blowup factor is recorded in CTS metadata so Phase 7 can size
  the evolution cell budget.
- Anyone wanting a pure-Cook path can swap in a `tm_to_cts_cook.py`
  implementation later; the interface is fixed.

## References

- Neary, T. and Woods, D. (2006). Small fast universal Turing machines.
  *Theoretical Computer Science*, 362(1-3), 171-195.
- Cook, M. (2004). Universality in elementary cellular automata. `15-1-1.pdf`
  in this repo, §5.
