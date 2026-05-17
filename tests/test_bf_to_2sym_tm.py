"""2-symbol BF -> TM parity tests.

The 2-symbol lowering supports BF programs whose cells stay in {0, 1}
(wrap modulo 2). Parity is checked against a matching reference
interpreter restricted to {0, 1}.
"""

import pytest

from compiler.bf_to_2sym_tm import compile_bf_2sym, run_bf_2sym_reference
from compiler.tm import run


def tm_final_tape(tm, max_steps: int = 100_000) -> dict[int, int]:
    history = run(tm, max_steps)
    final = history[-1]
    assert final.halted, f"TM did not halt in {max_steps} steps"
    return {pos: val for pos, val in final.tape}


@pytest.mark.parametrize("source", [
    "",
    "+",
    "++",
    "+-",
    "+>+",
    "+>+>+",
    "+[-]",
    "+[->+<]",
    "++[->+<]",
])
def test_bf_to_2sym_tm_matches_reference(source):
    tm = compile_bf_2sym(source)
    final = tm_final_tape(tm)
    expected = run_bf_2sym_reference(source)
    assert final == expected, (
        f"BF {source!r}: 2sym TM tape {final}, reference {expected}"
    )


def test_2sym_tm_alphabet_is_binary():
    tm = compile_bf_2sym("+[->+<]")
    seen = set()
    for (_, sym), (_, write, _) in tm.transitions.items():
        seen.add(sym)
        seen.add(write)
    assert seen <= {0, 1}, f"2sym TM uses symbols outside {{0,1}}: {seen}"


def test_2sym_tm_directions_are_LRS():
    tm = compile_bf_2sym("+[->+<]")
    for _, (_, _, d) in tm.transitions.items():
        assert d in ("L", "R", "S")


def test_empty_program():
    tm = compile_bf_2sym("")
    history = run(tm, max_steps=10)
    assert history[0].halted or history[-1].halted
