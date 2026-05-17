"""Ether invariance tests: the period-14 ether reproduces under Rule 110.

The boundary in `step(..., boundary='ether')` supplies the *static* phase-0
ether, so after `t` steps the leftmost `t` and rightmost `t` cells may be
contaminated by phase mismatch. All multi-step assertions therefore restrict
to the safe interior `state[t:width-t]`.
"""

from core.ether import (
    ETHER,
    SHIFT_PER_STEP,
    SPATIAL_PERIOD,
    TEMPORAL_PERIOD,
    ether_window,
)
from core.rule110 import evolve, step


def test_ether_pattern_has_expected_shape():
    assert len(ETHER) == SPATIAL_PERIOD == 14
    assert sum(ETHER) == 8
    assert TEMPORAL_PERIOD == 7
    assert SHIFT_PER_STEP == 4


def test_ether_shifts_by_four_in_one_step():
    state = ether_window(0, SPATIAL_PERIOD)
    out = step(state, boundary="ether")
    expected = ether_window(SHIFT_PER_STEP, SPATIAL_PERIOD)
    assert out == expected


def test_ether_returns_to_itself_after_temporal_period_in_safe_interior():
    width = SPATIAL_PERIOD * 10
    state = ether_window(0, width)

    for _ in range(TEMPORAL_PERIOD):
        state = step(state, boundary="ether")

    expected = ether_window(0, width)
    safe = slice(TEMPORAL_PERIOD, width - TEMPORAL_PERIOD)
    assert state[safe] == expected[safe]


def test_ether_translation_accumulates_across_steps_in_safe_interior():
    width = SPATIAL_PERIOD * 20
    n_steps = 5

    state = ether_window(0, width)
    history = evolve(state, n_steps, boundary="ether")

    for t in range(n_steps + 1):
        expected = ether_window(t * SHIFT_PER_STEP, width)
        safe = slice(t, width - t)
        assert history[t][safe] == expected[safe], f"mismatch at t={t}"


def test_ether_under_zero_boundary_diverges_at_edges():
    width = SPATIAL_PERIOD * 4
    state = ether_window(0, width)
    out = step(state, boundary="zero")
    expected_with_ether = ether_window(SHIFT_PER_STEP, width)
    assert out != expected_with_ether
    margin = 2
    assert out[margin:width - margin] == expected_with_ether[margin:width - margin]
