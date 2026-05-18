"""Cook §3.5 compound-object collision: 4-C2 tape character × Ebar.

Cook §3.5: "The first Ē of the leader reacts with the four C2s in turn,
becoming an invisible Ē at the end, and emitting two As along the way."

We verify the structurally observable half of this claim: 4 C2 gliders
placed at the empirical stable separation, hit by a single Ebar at the
verified crossing-phase gap, produce an A glider (period 3, +2) on the
right side of the C2 character. The "invisible Ē" (phase-shifted form)
on the left is not yet positively identified by our structural detector;
its non-detection is consistent with the bit pattern shifting.

This is the first verified Cook §3.5 reaction in our test suite — the
mechanism by which leaders emit acceptor/rejector pulses during
crossing.
"""

import pytest

from compiler.glider_detect import find_displaced_glider, is_stationary_glider
from core.cook_gliders import A, C2, Ebar, fresh_ether_state, place_cook_glider
from core.ether import SPATIAL_PERIOD
from core.rule110_fast import evolve_numpy


WIDTH = SPATIAL_PERIOD * 600
POST = 2100
C2_SEP = 28
EBAR_GAP = 22


def _build_four_c2_plus_ebar():
    state = fresh_ether_state(WIDTH, phase=0)
    tape_start = WIDTH // 4
    c2_anchors = []
    cw = 0
    target = tape_start
    for k in range(4):
        if k > 0:
            target = c2_anchors[-1] + C2_SEP
        a, cw = place_cook_glider(state, target, C2, cumulative_width=cw)
        c2_anchors.append(a)
    place_cook_glider(state, c2_anchors[-1] + C2.extent + EBAR_GAP,
                      Ebar, cumulative_width=cw)
    return state, tuple(c2_anchors)


def test_all_four_c2_survive_ebar_pass():
    state, c2_anchors = _build_four_c2_plus_ebar()
    s_t = evolve_numpy(state, POST)
    s_t_c2 = evolve_numpy(s_t, C2.period_t)
    for i, anchor in enumerate(c2_anchors):
        assert is_stationary_glider(s_t, s_t_c2, anchor, C2.extent, POST), (
            f"C2[{i}] did not survive the Ebar pass"
        )


def test_ebar_produces_an_a_glider_on_the_right():
    """The 4-C2 × Ebar collision emits at least one A-class glider
    (period 3, +2) on the right side of the C2 character — Cook's
    "two As along the way." We verify by locating one A glider via
    the structural displacement detector."""
    state, c2_anchors = _build_four_c2_plus_ebar()
    s_t = evolve_numpy(state, POST)
    s_t_a = evolve_numpy(s_t, A.period_t)
    search_left = c2_anchors[-1] + C2.extent + 50
    search_right = WIDTH - POST - 50
    a_anchor = find_displaced_glider(
        s_t, s_t_a, displacement=A.displacement, time_t=POST,
        extent=A.extent, search_left=search_left, search_right=search_right,
    )
    assert a_anchor is not None, (
        "expected an A glider on the right after 4-C2 × Ebar collision"
    )


def test_a_glider_product_persists_over_five_periods():
    """The emitted A glider keeps displacing +2 cells per 3 steps for
    5 consecutive periods, confirming it is a real Cook-class A and not
    a transient artefact."""
    state, c2_anchors = _build_four_c2_plus_ebar()
    s_t = evolve_numpy(state, POST)
    s_t_a = evolve_numpy(s_t, A.period_t)
    search_left = c2_anchors[-1] + C2.extent + 50
    search_right = WIDTH - POST - 50
    a_anchor = find_displaced_glider(
        s_t, s_t_a, displacement=A.displacement, time_t=POST,
        extent=A.extent, search_left=search_left, search_right=search_right,
    )
    assert a_anchor is not None

    snapshots = [s_t]
    for _ in range(5):
        snapshots.append(evolve_numpy(snapshots[-1], A.period_t))

    window = tuple(snapshots[0][a_anchor + j] for j in range(A.extent))
    for k in range(1, 6):
        moved_anchor = a_anchor + k * A.displacement
        observed = tuple(snapshots[k][moved_anchor + j] for j in range(A.extent))
        assert observed == window, (
            f"A glider pattern shifted at period {k}: expected {window}, got {observed}"
        )
