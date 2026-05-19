"""Known Brainfuck programs with documented expected outputs.

Sources: esolangs.org/wiki/Brainfuck, brainfuck.org (Cristofani),
en.wikipedia.org/wiki/Brainfuck. Exercises compiler.bf.run_bf_byte —
standard 8-bit semantics (256-cell wrap, `,` returns 0 on EOF). The
3-bit TM compiler (run_bf_reference) is too narrow for these and is
not used here; divergence is documented in compiler/bf.py.
"""

import pytest

from compiler.bf import run_bf_byte


HELLO_WORLD = (
    "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]"
    ">>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++."
)

CAT = ",[.,]"

ADD_BYTES = ",>,[<+>-]<."

FIBONACCI = ",>+>+<<[->>[->+>+<<]<[->>+<<]>>[-<+>]>[-<<<+>>>]<<<<]>>."


def test_hello_world():
    assert run_bf_byte(HELLO_WORLD) == b"Hello World!\n"


def test_cat_empty():
    assert run_bf_byte(CAT, stdin=b"") == b""


def test_cat_passthrough():
    assert run_bf_byte(CAT, stdin=b"hello") == b"hello"


def test_add_bytes():
    assert run_bf_byte(ADD_BYTES, stdin=bytes([2, 3])) == bytes([5])
    assert run_bf_byte(ADD_BYTES, stdin=bytes([100, 50])) == bytes([150])
    assert run_bf_byte(ADD_BYTES, stdin=bytes([200, 100])) == bytes([(200 + 100) % 256])


@pytest.mark.parametrize(
    "n_input, expected",
    [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 5),
        (4, 8),
        (5, 13),
        (6, 21),
        (10, 144),
        (11, 233),
        (12, 377 % 256),
    ],
)
def test_fibonacci(n_input, expected):
    out = run_bf_byte(FIBONACCI, stdin=bytes([n_input]))
    assert out == bytes([expected]), (n_input, expected, list(out))


def test_eof_returns_zero():
    src = ",.+."
    assert run_bf_byte(src, stdin=b"") == bytes([0, 1])


def test_truthy_loop_skipped_without_input():
    src = ",[->+<]>."
    assert run_bf_byte(src, stdin=b"") == bytes([0])
    assert run_bf_byte(src, stdin=bytes([7])) == bytes([7])
