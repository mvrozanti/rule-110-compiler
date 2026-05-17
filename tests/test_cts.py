"""Cyclic Tag System tests against hand-traced runs."""

import pytest

from compiler.cts import CTSSpec, CTSState, run, step


def tape(s: str) -> tuple[str, ...]:
    return tuple(s)


def test_empty_tape_halts_immediately():
    spec = CTSSpec(appendants=(tape("Y"),), initial_tape=())
    history = run(spec, max_steps=10)
    assert len(history) == 1
    assert history[0].halted


def test_n_symbol_is_consumed_without_append():
    spec = CTSSpec(appendants=(tape("YY"),), initial_tape=tape("NNN"))
    history = run(spec, max_steps=10)
    assert [h.tape for h in history] == [
        tape("NNN"), tape("NN"), tape("N"), (),
    ]
    assert [h.cursor for h in history] == [0, 0, 0, 0]


def test_y_appends_current_appendant_and_advances_cursor():
    spec = CTSSpec(appendants=(tape("Y"), tape("N")), initial_tape=tape("Y"))
    history = run(spec, max_steps=10)
    assert history[0] == CTSState(tape("Y"), 0)
    assert history[1] == CTSState(tape("Y"), 1)
    assert history[2] == CTSState(tape("N"), 0)
    assert history[3] == CTSState((), 1)
    assert history[3].halted


def test_two_appendants_two_y_initial():
    spec = CTSSpec(
        appendants=(tape("YN"), tape("N")),
        initial_tape=tape("YY"),
    )
    history = run(spec, max_steps=20)
    expected_tapes = [
        tape("YY"),
        tape("YYN"),
        tape("YNN"),
        tape("NNYN"),
        tape("NYN"),
        tape("YN"),
        tape("NN"),
        tape("N"),
        (),
    ]
    assert [h.tape for h in history] == expected_tapes


def test_appendant_cursor_cycles_modulo_length():
    spec = CTSSpec(
        appendants=(tape("Y"), tape("Y"), tape("Y")),
        initial_tape=tape("YYY"),
    )
    history = run(spec, max_steps=10)
    cursors = [h.cursor for h in history]
    assert cursors[:6] == [0, 1, 2, 0, 1, 2]


def test_step_is_idempotent_on_halted_state():
    spec = CTSSpec(appendants=(tape("Y"),), initial_tape=())
    s = CTSState((), 0)
    assert step(spec, s) == s


def test_rejects_invalid_symbols_in_tape():
    with pytest.raises(ValueError):
        CTSSpec(appendants=(tape("Y"),), initial_tape=tape("X"))


def test_rejects_invalid_symbols_in_appendant():
    with pytest.raises(ValueError):
        CTSSpec(appendants=(tape("Z"),), initial_tape=tape("Y"))


def test_rejects_zero_appendants():
    with pytest.raises(ValueError):
        CTSSpec(appendants=(), initial_tape=tape("Y"))
