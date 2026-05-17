"""BF parser, BF -> TM lowering, and TM execution tests.

Reference interpreter parity: for each BF program, the TM produced by
compile_bf(...).run(...) must end with the same tape contents as
run_bf_reference(...).
"""

import pytest

from compiler.bf import Dec, Get, Inc, Left, Loop, Put, Right, parse
from compiler.bf_to_tm import compile_bf, run_bf_reference
from compiler.tm import run


def tm_final_tape(tm, max_steps=100000):
    history = run(tm, max_steps)
    final = history[-1]
    assert final.halted, f"TM did not halt in {max_steps} steps"
    return {pos: val for pos, val in final.tape}


def test_parse_simple_sequence():
    ast = parse("+-><.,")
    assert ast == (Inc(), Dec(), Right(), Left(), Put(), Get())


def test_parse_loop_nests():
    ast = parse("+[-]>")
    assert ast == (Inc(), Loop((Dec(),)), Right())


def test_parse_rejects_unbalanced_open():
    with pytest.raises(ValueError):
        parse("[+")


def test_parse_rejects_unbalanced_close():
    with pytest.raises(ValueError):
        parse("+]")


def test_parse_skips_unknown_characters():
    ast = parse("+ comments are skipped -")
    assert ast == (Inc(), Dec())


@pytest.mark.parametrize("source", [
    "",
    "+",
    "+++",
    "+++[-]",
    "++>++",
    "+++[->+<]",
    "++[->++<]",
    "+>+>+",
])
def test_bf_to_tm_matches_reference(source):
    tm = compile_bf(source)
    final_tape = tm_final_tape(tm)
    expected = run_bf_reference(source)
    assert final_tape == expected, (
        f"BF {source!r}: TM tape {final_tape}, reference {expected}"
    )


def test_empty_program_halts_immediately():
    tm = compile_bf("")
    history = run(tm, max_steps=10)
    assert history[0].halted or history[-1].halted


def test_increment_program_writes_one():
    tm = compile_bf("+")
    final = tm_final_tape(tm)
    assert final == {0: 1}


def test_three_increments_writes_three():
    tm = compile_bf("+++")
    final = tm_final_tape(tm)
    assert final == {0: 3}


def test_clear_loop_zeros_cell():
    tm = compile_bf("+++[-]")
    final = tm_final_tape(tm)
    assert final == {}


def test_move_cell_zero_to_cell_one():
    tm = compile_bf("+++[->+<]")
    final = tm_final_tape(tm)
    assert final == {1: 3}
