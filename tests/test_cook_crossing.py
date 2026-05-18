"""First verified Cook §3.2.4 collision: C2 × Ebar crossing.

When a Cook-faithful Ebar (period 30, displacement -8, width 7) collides
with a Cook-faithful C2 (period 7, displacement 0, width 3) at certain
placement gaps, BOTH gliders survive the collision — Cook's "crossing
collision" required for moving data to traverse tape data in his
universality construction.

The detectors live in `compiler/glider_detect.py` and recognise
post-crossing gliders by their period/displacement signature regardless
of bit-pattern phase shift (which Cook's crossing induces; see
ADR 0006).
"""

import pytest

from compiler.glider_detect import find_displaced_glider, is_stationary_glider
from core.cook_gliders import C2, Ebar, fresh_ether_state, place_cook_glider
from core.ether import SPATIAL_PERIOD
from core.rule110 import step


WIDTH = SPATIAL_PERIOD * 400
POST_STEPS = 1400


def _evolve(state, n):
    s = tuple(state)
    for _ in range(n):
        s = step(s, boundary="ether")
    return s


def _run_collision(gap):
    state = fresh_ether_state(WIDTH, phase=0)
    anchor = WIDTH // 3
    c2_anchor, cw = place_cook_glider(state, anchor, C2, cumulative_width=0)
    eb_anchor, cw = place_cook_glider(
        state, c2_anchor + C2.extent + gap, Ebar, cumulative_width=cw
    )
    s_t = _evolve(state, POST_STEPS)
    s_t_plus_c2 = _evolve(s_t, C2.period_t)
    s_t_plus_eb = _evolve(s_t, Ebar.period_t)
    return c2_anchor, s_t, s_t_plus_c2, s_t_plus_eb


@pytest.mark.parametrize("gap", [0, 5, 10, 22, 25, 30])
def test_c2_x_ebar_crossing_both_gliders_survive(gap):
    """At several gap values, the C2 × Ebar collision is a crossing: C2 is
    stationary at the original anchor AND a period-(30,-8) glider exists
    on the left side."""
    c2_anchor, s_t, s_t_plus_c2, s_t_plus_eb = _run_collision(gap)

    c2_stationary = is_stationary_glider(s_t, s_t_plus_c2, c2_anchor, C2.extent, POST_STEPS)
    assert c2_stationary, f"C2 not stationary at gap={gap}"

    safe_lo = POST_STEPS + 50
    safe_hi = c2_anchor - 20
    ebar_anchor = find_displaced_glider(
        s_t, s_t_plus_eb, displacement=Ebar.displacement,
        time_t=POST_STEPS, extent=Ebar.extent,
        search_left=safe_lo, search_right=safe_hi,
    )
    assert ebar_anchor is not None, f"no period-(30,-8) glider on left at gap={gap}"


def test_crossing_ebar_persists_over_eight_periods():
    """The post-crossing Ebar isn't a transient — verify the same pattern
    keeps displacing by -8 every 30 steps for 8 consecutive periods."""
    c2_anchor, s_t, _, s_t_plus_eb = _run_collision(gap=0)

    safe_lo = POST_STEPS + 50
    safe_hi = c2_anchor - 20
    eb_anchor = find_displaced_glider(
        s_t, s_t_plus_eb, displacement=Ebar.displacement,
        time_t=POST_STEPS, extent=Ebar.extent,
        search_left=safe_lo, search_right=safe_hi,
    )
    assert eb_anchor is not None

    snapshots = [s_t]
    for _ in range(8):
        snapshots.append(_evolve(snapshots[-1], Ebar.period_t))

    window = tuple(snapshots[0][eb_anchor + j] for j in range(Ebar.extent))
    for k in range(1, 9):
        moved_anchor = eb_anchor + k * Ebar.displacement
        observed = tuple(snapshots[k][moved_anchor + j] for j in range(Ebar.extent))
        assert observed == window, (
            f"Ebar pattern shifted at period {k}: expected {window}, got {observed}"
        )


def test_crossing_phase_shift_changes_ebar_bit_pattern():
    """ADR 0006: Cook's crossing shifts each glider's local left_phase
    by the other glider's width mod 14. The post-crossing Ebar's bit
    pattern at its new anchor is NOT the original Ebar.delta; this test
    pins down the empirical post-crossing pattern (1, 0, 0, 0, 1, 0, 0)
    so any future change is caught."""
    c2_anchor, s_t, _, s_t_plus_eb = _run_collision(gap=0)
    safe_lo = POST_STEPS + 50
    safe_hi = c2_anchor - 20
    eb_anchor = find_displaced_glider(
        s_t, s_t_plus_eb, displacement=Ebar.displacement,
        time_t=POST_STEPS, extent=Ebar.extent,
        search_left=safe_lo, search_right=safe_hi,
    )
    assert eb_anchor is not None
    bits = tuple(s_t[eb_anchor + j] for j in range(Ebar.extent))
    assert bits != Ebar.delta, (
        "post-crossing Ebar should have a phase-shifted bit pattern; "
        "if this assertion fires, our understanding of the phase shift is wrong"
    )
    assert bits == (1, 0, 0, 0, 1, 0, 0), (
        f"empirical post-crossing Ebar bit pattern changed: got {bits}, "
        "expected (1, 0, 0, 0, 1, 0, 0)"
    )
