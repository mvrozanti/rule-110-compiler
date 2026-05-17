# 0001 — TM → CTS reduction

## Status

Accepted. Implements Phase 5. Updated 2026-05-17 to reflect what actually
landed (Cook §2.1 + §2.2) rather than the originally-planned Neary-Woods
path.

## Context

Cook's 2004 paper proves Rule 110 universality by reducing CTS to Rule 110.
To run a Turing machine in Rule 110, we still need TM → CTS. Two known
paths:

1. **Cook §2.1 + §2.2** — Cook himself spells out the reduction in his
   universality paper: TM → 2-tag system (§2.1, with the "alignment"
   subtlety where the head bit z determines which symbol of each pair is
   "used") → cyclic tag system (§2.2, with the 2k-appendant structure
   where the second k appendants are empty).

2. **Neary-Woods 2006** — "Small fast universal Turing machines," gives a
   reduction with polynomial-time slowdown and explicit size bounds.
   Cleaner for some purposes, references an external paper.

Originally this ADR chose Neary-Woods for tractability.

## Decision (revised)

Implement Cook §2.1 + §2.2 because:

- It keeps the entire pipeline in one paper (the same `15-1-1.pdf` that
  specifies the Rule 110 layer).
- The "alignment" mechanism Cook describes turned out to be implementable
  as a simple parity bit (`use_offset`) on the 2-tag system; see
  `compiler/aligned_tagsystem.py`.
- The 2k-appendant structure for CTS encoding (k real + k empty) is
  identical to what a Neary-Woods → CTS reduction would need.

## Consequences

- The composition `BF → TM → (Cook §2.1) → aligned tag → (Cook §2.2) → CTS`
  is universal end-to-end. Verified for the trivial program `+` in
  `tests/test_chain_bf_to_cts.py`.
- Strict faithfulness to one paper across all layers.
- Polynomial blowup is recorded in CTS metadata if any phase needs it.

## Current limitations

- **Cook §2.1 with non-zero initial TL/TR** is currently xfailed; the
  alignment tracking through L/R-pair processing has subtleties not yet
  fully captured. For BF programs (which always start with all-zero
  tape), the reduction is sufficient.
- **Multi-symbol BF → 2-symbol TM** is not yet implemented. `compile_bf`
  produces TMs with alphabet `{0..7}`; Cook §2.1 needs `{0, 1}`. A unary
  cell-encoding pass would unblock all BF programs through the chain.

## References

- Cook, M. (2004). Universality in elementary cellular automata.
  `15-1-1.pdf` in this repo, §2.1-§2.2 for TM → tag → CTS, §3-§4 for
  the Rule 110 construction.
- Neary, T. and Woods, D. (2006). Small fast universal Turing machines.
  *Theoretical Computer Science*, 362(1-3), 171-195. Not used in the
  current implementation; available as an alternate path if Cook's
  reduction proves intractable for larger TMs.
