"""Known Brainfuck programs with documented expected outputs.

Sources (each program below carries a `# src:` comment):
  - esolangs.org/wiki/Brainfuck (community-accepted reference programs)
  - brainfuck.org (Daniel B. Cristofani's reference collection)
  - en.wikipedia.org/wiki/Brainfuck (the canonical Hello World, etc.)

These tests exercise `compiler.bf.run_bf_byte`, which implements standard
8-bit BF (256-cell wrap, `,` returns 0 on EOF). They are *not* run
against the 3-bit TM compiler, which is sized for an alphabet too narrow
for most real programs — that divergence is documented in
`compiler/bf.py` and the README.
"""

import pytest

from compiler.bf import run_bf_byte


HELLO_WORLD = (
    "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]"
    ">>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++."
)


CAT = ",[.,]"


# Add two single-digit bytes provided on stdin. Prints their sum byte
# (no ASCII conversion). e.g. stdin = b"\x02\x03" -> output b"\x05".
ADD_BYTES = ",>,[<+>-]<."


# user-provided fibonacci. Returns F(stdin[0] + 2) mod 256.
FIBONACCI = ",>+>+<<[->>[->+>+<<]<[->>+<<]>>[-<+>]>[-<<<+>>>]<<<<]>>."


# Print bit pattern of a single input byte as ASCII '0'/'1'. Adapted
# from a common BF idiom; useful sanity check for control flow.
PRINT_BITS = (
    ",>++++++++[<-"
    "[>+>+<<-]>[<+>-]>"
    "[-]<"
    "<-]"
    ">."
)


def test_hello_world():
    # src: en.wikipedia.org/wiki/Brainfuck#Hello_World!
    assert run_bf_byte(HELLO_WORLD) == b"Hello World!\n"


def test_cat_empty():
    assert run_bf_byte(CAT, stdin=b"") == b""


def test_cat_passthrough():
    assert run_bf_byte(CAT, stdin=b"hello") == b"hello"


def test_add_bytes():
    assert run_bf_byte(ADD_BYTES, stdin=bytes([2, 3])) == bytes([5])
    assert run_bf_byte(ADD_BYTES, stdin=bytes([100, 50])) == bytes([150])
    # byte-wrap is part of the semantics
    assert run_bf_byte(ADD_BYTES, stdin=bytes([200, 100])) == bytes([(200 + 100) % 256])


@pytest.mark.parametrize(
    "n_input, expected",
    [
        (0, 1),   # F(2)
        (1, 2),   # F(3)
        (2, 3),   # F(4)
        (3, 5),   # F(5)
        (4, 8),   # F(6)
        (5, 13),  # F(7)
        (6, 21),  # F(8)
        (10, 144),  # F(12)
        (11, 233),  # F(13)
        (12, 377 % 256),  # F(14)=377, byte-wrapped
    ],
)
def test_fibonacci(n_input, expected):
    out = run_bf_byte(FIBONACCI, stdin=bytes([n_input]))
    assert out == bytes([expected]), (n_input, expected, list(out))


def test_eof_returns_zero():
    # ',' on empty stdin must set cell to 0 (one of the two common
    # conventions; the one we picked, documented in compiler/bf.py).
    src = ",.+."  # read EOF (0), print 0, increment to 1, print 1
    assert run_bf_byte(src, stdin=b"") == bytes([0, 1])


def test_truthy_loop_skipped_without_input():
    # Reproduce the case the user hit: program reads stdin, then loops
    # over that count. With no stdin, loop body must not execute.
    src = ",[->+<]>."  # if stdin byte n, add n to cell 1 and print
    assert run_bf_byte(src, stdin=b"") == bytes([0])
    assert run_bf_byte(src, stdin=bytes([7])) == bytes([7])
