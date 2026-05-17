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
    C    verified
    Ebar verified
    B    candidate identified, fails isolation verification
    D    candidate identified, fails isolation verification
    E    candidate identified, fails isolation verification

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


C = Glider(
    name="C",
    period_t=7,
    displacement=0,
    left_phase=8,
    delta=((0, 0), (4, 0), (8, 0), (10, 0), (12, 1), (13, 1)),
    citation="Cook 2004 Fig 5 (C-class: (7, 0)); discovered via "
             "scripts/isolate_gliders.py seed=51 t=700; verified in isolation.",
)


Ebar = Glider(
    name="Ebar",
    period_t=30,
    displacement=-8,
    left_phase=6,
    delta=(
        (0, 1), (2, 0), (3, 1), (4, 1), (5, 0), (7, 1),
        (10, 0), (11, 0), (13, 1), (17, 1), (19, 0), (20, 0), (21, 1),
    ),
    citation="Cook 2004 Fig 5 (Ē: (30, -8)); discovered via "
             "scripts/isolate_gliders.py seed=27 t=400; verified in isolation.",
)


B = Glider(
    name="B",
    period_t=4,
    displacement=-2,
    left_phase=3,
    delta=(
        (0, 0), (1, 0), (2, 1), (3, 1), (5, 0), (7, 1),
        (10, 1), (12, 0), (13, 0), (14, 0), (18, 1), (21, 1),
        (24, 1), (26, 0), (28, 0), (30, 1), (31, 1),
        (33, 0), (34, 1), (35, 1), (36, 0), (37, 0),
    ),
    citation="Cook 2004 Fig 5 (B: (4, -2)); discovered via "
             "scripts/track_gliders.py seed=106 (200 seeds); verified in isolation. "
             "This captured form likely contains extra ether ripples beyond the core "
             "B; minimal-pattern reduction is future work.",
)


ALL_VERIFIED: tuple[Glider, ...] = (A, B, C, Ebar)
