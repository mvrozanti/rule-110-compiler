"""Cook's gliders for Rule 110.

Each Glider records the minimal delta from the ether background needed to
instantiate it, the ether phase at the glider's left edge, and its
(period_t, displacement) period in absolute Rule 110 coordinates.

To place glider G at position p: choose p such that p % 14 == G.left_phase,
then overwrite cells p+offset with the values in G.delta. The surrounding
ether at phase 0 (or any consistent phase derivable by translation) provides
the rest of the context.

A glider is admitted into this module only after its propagation test
(tests/test_gliders.py) passes in isolation: place on pure ether, evolve
period_t * n steps, the same delta must reappear at offset +n*displacement.

Status (2026-05-17):
    A    verified
    B    candidate identified, fails isolation verification
    C    candidate identified, fails isolation verification
    D    candidate identified, fails isolation verification
    E    candidate identified, fails isolation verification
    Ebar candidate identified, fails isolation verification

See docs/gliders_status.md for current candidates and known gaps. The
discovery scripts are scripts/discover_gliders.py, scripts/observe_gliders.py,
scripts/extract_gliders.py, scripts/verify_candidate.py.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Glider:
    name: str
    period_t: int
    displacement: int
    left_phase: int
    delta: tuple[tuple[int, int], ...]
    citation: str


A = Glider(
    name="A",
    period_t=3,
    displacement=2,
    left_phase=3,
    delta=((0, 0), (2, 1), (3, 1)),
    citation="Cook 2004 Fig 4 / Fig 5: (t,x) period (3, +2), width 6; "
             "delta empirically discovered (scripts/extract_gliders.py seed=0) "
             "and verified in isolation.",
)


ALL_VERIFIED: tuple[Glider, ...] = (A,)
