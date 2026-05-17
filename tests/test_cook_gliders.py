"""Verification that the Cook-faithful catalogue propagates as advertised.

Each glider is placed on the boundary between two ether phases (left
phase L, right phase L + width), evolved for several periods, and checked
to reappear at offset (k * displacement) after k periods, with both halos
matching the time-shifted ether on the appropriate side.
"""

import pytest

from core.cook_gliders import A, C2, Ebar, COOK_CATALOG, place_cook_glider, fresh_ether_state
from core.ether import SPATIAL_PERIOD, ether_cell
from core.rule110 import step


@pytest.mark.parametrize("gl", list(COOK_CATALOG.values()), ids=lambda g: g.name)
def test_propagates_with_advertised_period_and_displacement(gl):
    width = SPATIAL_PERIOD * 200
    state = fresh_ether_state(width, phase=0)
    anchor = width // 2
    delta_anchor, new_width = place_cook_glider(state, anchor, gl, cumulative_width=0)
    s = tuple(state)
    for k in range(1, 4):
        for _ in range(gl.period_t):
            s = step(s, boundary="ether")
        moved = delta_anchor + k * gl.displacement
        for j in range(gl.extent):
            pos = moved + j
            if not (0 <= pos < width):
                pytest.fail(f"glider moved off the state at k={k}")
            assert s[pos] == gl.delta[j], (
                f"{gl.name}: after {k} periods, cell {pos} (offset {j} from new anchor) "
                f"should be {gl.delta[j]} (matching delta), got {s[pos]}"
            )


@pytest.mark.parametrize("gl", list(COOK_CATALOG.values()), ids=lambda g: g.name)
def test_left_halo_matches_left_phase_ether(gl):
    """Left of the glider, the state remains standard ether at phase 0."""
    width = SPATIAL_PERIOD * 200
    state = fresh_ether_state(width, phase=0)
    anchor = width // 2
    delta_anchor, _ = place_cook_glider(state, anchor, gl, cumulative_width=0)
    for j in range(-20, 0):
        pos = delta_anchor + j
        assert state[pos] == ether_cell(pos), (
            f"{gl.name}: left-side cell {pos} should be standard ether"
        )


@pytest.mark.parametrize("gl", list(COOK_CATALOG.values()), ids=lambda g: g.name)
def test_right_side_ether_is_shifted_by_width(gl):
    """Right of the glider, the cells should match ether shifted by gl.width."""
    width = SPATIAL_PERIOD * 200
    state = fresh_ether_state(width, phase=0)
    anchor = width // 2
    delta_anchor, _ = place_cook_glider(state, anchor, gl, cumulative_width=0)
    for j in range(gl.extent, gl.extent + 20):
        pos = delta_anchor + j
        expected = ether_cell(pos + gl.width)
        assert state[pos] == expected, (
            f"{gl.name}: right-side cell {pos} (offset {j} from anchor) should be "
            f"ether shifted by width={gl.width}: expected {expected}, got {state[pos]}"
        )
