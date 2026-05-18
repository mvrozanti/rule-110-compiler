"""Multi-C2 tape traversal: one Ebar crosses N C2 gliders in sequence.

This is the structural primitive Cook's CTS-in-R110 construction needs
for moving data to traverse tape data. If the crossing collision in
`tests/test_cook_crossing.py` is robust, then a single Ebar should
successfully cross N consecutive C2 gliders, with all C2s and the Ebar
surviving on the far side.

Each successful traversal of one C2 by one Ebar is one "step" of Cook's
"moving data crosses one tape symbol" mechanic — direct evidence of
computation happening inside Rule 110.
"""

import pytest

from compiler.glider_detect import find_displaced_glider, is_stationary_glider
from core.cook_gliders import C2, Ebar, fresh_ether_state, place_cook_glider
from core.ether import SPATIAL_PERIOD
from core.rule110 import step


WIDTH = SPATIAL_PERIOD * 800
POST_STEPS = 3000
C2_SEP = 28
EBAR_TO_LAST_C2_GAP = 22  # a known crossing-phase gap


def _evolve(state, n):
    s = tuple(state)
    for _ in range(n):
        s = step(s, boundary="ether")
    return s


def _build_and_run(n_c2):
    state = fresh_ether_state(WIDTH, phase=0)
    tape_start = WIDTH * 3 // 4
    c2_anchors = []
    cw = 0
    target = tape_start
    for _ in range(n_c2):
        a, cw = place_cook_glider(state, target, C2, cumulative_width=cw)
        c2_anchors.append(a)
        target = a + C2_SEP
    place_cook_glider(state, c2_anchors[-1] + C2.extent + EBAR_TO_LAST_C2_GAP,
                      Ebar, cumulative_width=cw)
    s_t = _evolve(state, POST_STEPS)
    s_t_c2 = _evolve(s_t, C2.period_t)
    s_t_eb = _evolve(s_t, Ebar.period_t)
    return c2_anchors, s_t, s_t_c2, s_t_eb


@pytest.mark.parametrize("n_c2", [2, 3, 5, 10])
def test_ebar_crosses_n_c2_tape(n_c2):
    """All n_c2 stationary tape symbols survive AND a period-(30,-8)
    glider emerges to the far left of the leftmost C2."""
    c2_anchors, s_t, s_t_c2, s_t_eb = _build_and_run(n_c2)

    for i, ca in enumerate(c2_anchors):
        assert is_stationary_glider(s_t, s_t_c2, ca, C2.extent, POST_STEPS), (
            f"C2[{i}] at anchor {ca} did not survive {n_c2}-C2 traversal"
        )

    safe_lo = POST_STEPS + 50
    safe_hi = c2_anchors[0] - 20
    eb_at = find_displaced_glider(
        s_t, s_t_eb, displacement=Ebar.displacement, time_t=POST_STEPS,
        extent=Ebar.extent, search_left=safe_lo, search_right=safe_hi,
    )
    assert eb_at is not None, (
        f"Ebar did not emerge on the left after crossing {n_c2} C2s"
    )


def test_ten_c2_traversal_is_real_computation():
    """A 10-C2 tape crossed by one Ebar is 10 sequential glider collisions
    inside Rule 110. This is the structural primitive for moving data
    traversing tape data in Cook's CTS construction."""
    c2_anchors, s_t, s_t_c2, s_t_eb = _build_and_run(10)
    surviving = sum(
        1 for ca in c2_anchors
        if is_stationary_glider(s_t, s_t_c2, ca, C2.extent, POST_STEPS)
    )
    assert surviving == 10, f"only {surviving}/10 C2s survived"

    safe_lo = POST_STEPS + 50
    safe_hi = c2_anchors[0] - 20
    eb_at = find_displaced_glider(
        s_t, s_t_eb, displacement=Ebar.displacement, time_t=POST_STEPS,
        extent=Ebar.extent, search_left=safe_lo, search_right=safe_hi,
    )
    assert eb_at is not None
