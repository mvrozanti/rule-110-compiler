"""Per-glider propagation tests. A glider must reproduce its delta shifted by
its displacement after each multiple of its period."""

import pytest

from core.ether import SPATIAL_PERIOD, ether_window
from core.gliders import A, ALL_VERIFIED, Glider
from core.rule110 import step


def place(g: Glider, state_periods: int = 20) -> tuple[tuple[int, ...], int]:
    width = SPATIAL_PERIOD * state_periods
    anchor = SPATIAL_PERIOD * (state_periods // 2) + g.left_phase
    state = list(ether_window(0, width))
    for offset, b in g.delta:
        state[anchor + offset] = b
    return tuple(state), anchor


def propagate(g: Glider, n_periods: int = 4) -> None:
    state, anchor = place(g)
    width = len(state)

    s = state
    for k in range(1, n_periods + 1):
        for _ in range(g.period_t):
            s = step(s, boundary="ether")
        for offset, b in g.delta:
            pos = anchor + offset + k * g.displacement
            assert 0 <= pos < width
            assert s[pos] == b, (
                f"{g.name} broke at period {k}: cell {pos} "
                f"(delta-offset {offset}, total shift {k * g.displacement}) "
                f"= {s[pos]}, expected {b}"
            )


@pytest.mark.parametrize("g", ALL_VERIFIED, ids=lambda g: g.name)
def test_glider_propagates_for_four_periods(g: Glider) -> None:
    propagate(g, n_periods=4)


def test_A_displaces_by_two_per_period():
    assert A.period_t == 3
    assert A.displacement == 2


def test_A_delta_has_three_cells():
    assert len(A.delta) == 3
