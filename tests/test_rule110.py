"""Parity tests for core/rule110.py against hand-traced Rule 110 evolutions."""

import pytest

from core.rule110 import RULE_TABLE, evolve, step


def test_rule_table_matches_published_rule():
    expected = {
        (1, 1, 1): 0,
        (1, 1, 0): 1,
        (1, 0, 1): 1,
        (1, 0, 0): 0,
        (0, 1, 1): 1,
        (0, 1, 0): 1,
        (0, 0, 1): 1,
        (0, 0, 0): 0,
    }
    assert RULE_TABLE == expected


def test_rule_number_is_110():
    bits = [RULE_TABLE[tuple((n >> k) & 1 for k in (2, 1, 0))] for n in range(8)]
    rule_number = sum(b << k for k, b in enumerate(bits))
    assert rule_number == 110


def test_single_cell_zero_boundary_first_five_steps():
    history = evolve((0, 0, 0, 1, 0, 0, 0), steps=5, boundary="zero")
    expected = [
        (0, 0, 0, 1, 0, 0, 0),
        (0, 0, 1, 1, 0, 0, 0),
        (0, 1, 1, 1, 0, 0, 0),
        (1, 1, 0, 1, 0, 0, 0),
        (1, 1, 1, 1, 0, 0, 0),
        (1, 0, 0, 1, 0, 0, 0),
    ]
    assert history == expected


def test_all_zeros_stay_zero():
    state = (0,) * 20
    for _ in range(50):
        state = step(state, boundary="zero")
    assert state == (0,) * 20


def test_all_ones_zero_boundary_one_step():
    state = (1,) * 5
    out = step(state, boundary="zero")
    assert out == (1, 0, 0, 0, 1)


def test_unknown_boundary_raises():
    with pytest.raises(ValueError):
        step((0, 1, 0), boundary="periodic")


@pytest.mark.parametrize("trio,expected", list(RULE_TABLE.items()))
def test_each_neighborhood_evaluates_to_table_entry(trio, expected):
    state = trio
    out = step(state, boundary="zero")
    assert out[1] == expected


def test_evolve_returns_initial_state_at_index_zero():
    initial = (0, 1, 0, 1, 1, 0)
    history = evolve(initial, steps=10, boundary="zero")
    assert history[0] == initial
    assert len(history) == 11
