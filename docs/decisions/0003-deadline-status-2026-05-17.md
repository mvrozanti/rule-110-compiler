# 0003 — Deadline status snapshot, 2026-05-17

## Status

In-flight. Recording the state of the 2026-05-31 milestone plan after the
first day's work so the slip-tracking commitment from the deadline
discussion is observable.

## Milestones today

| ID | Target | Status |
|---|---|---|
| M1 | 2026-05-20 — glider E resolved | **partial / at risk**. Width-14 exhaustive sweep over all 14 phases (172k candidates) returned zero hits. Width-19 popcount 5-11 sweep (~3.6M candidates, ~90 min CPU) was launched but stopped at 200k scanned to free the session for downstream work. Resolution path open but unfinished. |
| M2 | 2026-05-22 — α/β calibration | **completed early**. `tests/test_alpha_beta.py` (5 tests) records: C×C min stable 28 cells; Ē×Ē min stable 42 cells; placement quantum 14 cells; C-variant width 0 (does not match Cook C1/C2/C3). |
| M3 | 2026-05-25 — Cook's core 8 collision atlas | **scope changed**, see ADR 0002. Pivoted to Plan B: empirical collision atlas of OUR catalogue (`tests/test_collision_residue.py`, 4 tests). 8 total empirical collision fixtures green. Cook-faithful atlas remains blocked on width-3 C variant discovery. |
| M4 | 2026-05-28 — collision-driven CTS step | **at risk**. Today's empirical work revealed the C × Ē collision is an *expanding chaotic disturbance*, not a clean post-collision glider set. Constructing a selective CTS step (where Y consumed and appendant placed) is therefore not reachable with current gliders. |
| M5 | 2026-05-31 — end-to-end universality demo | **at risk**. Blocked on M4. |

## What today established

1. The chain BF → TM → aligned tag → CTS → R110 IC → evolve → decode
   round-trips end-to-end for several BF programs (`tests/test_end_to_end.py`,
   already verified before today's work).
2. Empirical α/β calibration for our catalogue, recorded as fixtures.
3. Discovery that our entire empirical glider catalogue (A, B, C, D, Ē)
   measures width 0 mod 14 by the procedure we use, while Cook's table
   gives nonzero widths for each. The catalogue is not Cook's specific
   variants. See ADR 0002.
4. Empirical: C × Ē produces a destructive expanding disturbance, not
   a Cook §3.2.4 crossing. The disturbance consumes neighbouring Cs as
   it grows. A "delete-rightmost" primitive exists for C tapes at
   ≥ 168-cell separation *for the first collision only*; subsequent
   disturbance expansion consumes additional Cs.

## What today did NOT establish

- A Cook-faithful collision atlas (C₂ × Ē crossing; A₄ × Ē → C₂; etc.).
  Blocked on glider variant discovery.
- A selective CTS step inside Rule 110. Blocked on collision-atlas
  control.
- The full universality demo. Blocked on the above.

## Slip honesty

Per the deadline commitment:
> "If any milestone slips by 48 hours, the README and verify_all flip
> that row to RED in the same commit that acknowledges the slip."

M1 (2026-05-20) is not yet slipped. M3 (2026-05-25) is on a different
scope (Plan B vs Plan A) but its Plan B form is achievable on time.
M4-M5 are at structural risk because the path through collision-driven
CTS execution depends on Cook-faithful gliders we don't have.

## Honest forward path

Two-week deadline framing assumed Cook's collision atlas could be
empirically reproduced on top of our gliders. Today's work shows that
assumption is wrong: our gliders are not Cook's. To meet 2026-05-31
faithfully, we'd need to first find Cook's specific glider variants
(width-3 C, width-7 Ē — we have Ē at width 7? need to recheck — width-6
A, etc.), which is a separate research thread.

To meet 2026-05-31 with a less-faithful but still real demonstration,
the scope reduction in ADR 0002 (Plan B: delete-only tag step inside
R110) is the path. Whether that scope reduction is acceptable is the
user's call, not mine.

I have not unilaterally cut the deadline. I have surfaced the obstacle
so the deadline can be re-evaluated with full information.
