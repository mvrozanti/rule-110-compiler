"""Direct unit tests for compiler.glider_detect helpers.

Verify the structural detectors give expected outputs for solo Cook-
faithful glider placements, and reject pure ether (which is trivially
period-7 stationary at any position but lacks the non-ether condition).
"""

from compiler.glider_detect import is_stationary_glider, find_displaced_glider
from core.cook_gliders import C2, Ebar, fresh_ether_state, place_cook_glider
from core.ether import SPATIAL_PERIOD
from core.rule110 import step


WIDTH = SPATIAL_PERIOD * 200


def _evolve(state, n):
    s = tuple(state)
    for _ in range(n):
        s = step(s, boundary="ether")
    return s


def test_is_stationary_rejects_pure_ether():
    state = fresh_ether_state(WIDTH, phase=0)
    s0 = tuple(state)
    s7 = _evolve(s0, 7)
    anchor = WIDTH // 2
    assert not is_stationary_glider(s0, s7, anchor, extent=6, time_t=0)


def test_is_stationary_accepts_solo_c2():
    state = fresh_ether_state(WIDTH, phase=0)
    anchor = WIDTH // 3
    c2_anchor, _ = place_cook_glider(state, anchor, C2, cumulative_width=0)
    s0 = tuple(state)
    s7 = _evolve(s0, 7)
    assert is_stationary_glider(s0, s7, c2_anchor, extent=C2.extent, time_t=0)


def test_is_stationary_accepts_solo_c2_after_many_periods():
    state = fresh_ether_state(WIDTH, phase=0)
    anchor = WIDTH // 3
    c2_anchor, _ = place_cook_glider(state, anchor, C2, cumulative_width=0)
    s = _evolve(state, 1400)
    s_next = _evolve(s, 7)
    assert is_stationary_glider(s, s_next, c2_anchor, extent=C2.extent, time_t=1400)


def test_find_displaced_rejects_pure_ether():
    state = fresh_ether_state(WIDTH, phase=0)
    s0 = tuple(state)
    s30 = _evolve(s0, 30)
    found = find_displaced_glider(s0, s30, displacement=-8, time_t=0, extent=Ebar.extent)
    assert found is None


def test_find_displaced_locates_solo_ebar():
    state = fresh_ether_state(WIDTH, phase=0)
    anchor = WIDTH // 2
    eb_anchor, _ = place_cook_glider(state, anchor, Ebar, cumulative_width=0)
    s0 = tuple(state)
    s30 = _evolve(s0, 30)
    found = find_displaced_glider(s0, s30, displacement=Ebar.displacement,
                                  time_t=0, extent=Ebar.extent)
    assert found is not None
    assert abs(found - eb_anchor) <= Ebar.extent, (
        f"expected Ebar near {eb_anchor}, found at {found}"
    )


def test_find_displaced_handles_late_time_window():
    """At a late time still inside the boundary-safe central window, the
    detector locates the displaced Ē. Bounds are chosen so the displaced
    Ē position remains in the safe central region (boundary effects
    propagate inward at one cell per step)."""
    state = fresh_ether_state(WIDTH, phase=0)
    anchor = WIDTH // 2
    eb_anchor, _ = place_cook_glider(state, anchor, Ebar, cumulative_width=0)
    late_t = 420
    s_late = _evolve(state, late_t)
    s_next = _evolve(s_late, 30)
    eb_late = eb_anchor + late_t * Ebar.displacement // Ebar.period_t
    safe_lo = late_t + 50
    safe_hi = WIDTH - late_t - 50
    found = find_displaced_glider(s_late, s_next, displacement=Ebar.displacement,
                                  time_t=late_t, extent=Ebar.extent,
                                  search_left=safe_lo, search_right=safe_hi)
    assert found is not None
    assert abs(found - eb_late) <= Ebar.extent, (
        f"expected Ebar near {eb_late}, found at {found}"
    )
