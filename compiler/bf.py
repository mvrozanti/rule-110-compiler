"""Brainfuck parser and reference interpreters.

Parser: AST is a flat list with `Loop` nodes containing nested ASTs.
Unbalanced brackets raise. The subset supported is the canonical 8
instructions.

Interpreters:
  - `run_bf_byte` (this module) — standard 8-bit semantics: 256-cell
    wrap, `,` reads from stdin bytes (returns 0 on EOF), `.` writes
    captured output. Used by `tests/test_known_programs.py` to compare
    against known programs from the wild.
  - `run_bf_reference` (in `compiler.bf_to_tm`) — narrow 3-bit cells
    (CELL_MAX=7), no I/O. Kept as the parity oracle for the TM
    compiler, whose state-table is sized to that alphabet.
"""

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Inc: pass


@dataclass(frozen=True)
class Dec: pass


@dataclass(frozen=True)
class Right: pass


@dataclass(frozen=True)
class Left: pass


@dataclass(frozen=True)
class Put: pass


@dataclass(frozen=True)
class Get: pass


@dataclass(frozen=True)
class Loop:
    body: tuple["Node", ...]


Node = Union[Inc, Dec, Right, Left, Put, Get, Loop]


_SIMPLE: dict[str, type] = {
    "+": Inc,
    "-": Dec,
    ">": Right,
    "<": Left,
    ".": Put,
    ",": Get,
}


def parse(source: str) -> tuple[Node, ...]:
    pos = 0

    def parse_block(end_char: str | None) -> tuple[tuple[Node, ...], int]:
        nonlocal pos
        nodes: list[Node] = []
        while pos < len(source):
            ch = source[pos]
            if ch in _SIMPLE:
                nodes.append(_SIMPLE[ch]())
                pos += 1
            elif ch == "[":
                pos += 1
                body, _ = parse_block("]")
                if pos >= len(source) or source[pos] != "]":
                    raise ValueError("unbalanced '[' in BF source")
                pos += 1
                nodes.append(Loop(body))
            elif ch == "]":
                if end_char != "]":
                    raise ValueError("unbalanced ']' in BF source")
                return tuple(nodes), pos
            else:
                pos += 1  # skip non-instruction characters silently
        if end_char is not None:
            raise ValueError(f"unexpected end of BF source, missing {end_char!r}")
        return tuple(nodes), pos

    ast, _ = parse_block(None)
    return ast


BYTE_CELL_WRAP = 256


def run_bf_byte(
    source_or_ast,
    stdin: bytes = b"",
    tape_size: int = 30_000,
    max_ops: int = 10_000_000,
) -> bytes:
    """Run BF with standard 8-bit semantics. Returns captured output bytes.

    `,` returns 0 on EOF (one of the two common conventions; matches the
    test corpus we ship in `tests/test_known_programs.py`).
    """
    if isinstance(source_or_ast, str):
        ast = parse(source_or_ast)
    else:
        ast = source_or_ast

    cells = [0] * tape_size
    dp = 0
    in_pos = 0
    output = bytearray()
    ops = 0

    def execute(nodes: tuple[Node, ...]) -> None:
        nonlocal dp, in_pos, ops
        for node in nodes:
            ops += 1
            if ops > max_ops:
                raise RuntimeError(f"BF byte runner exceeded max_ops={max_ops}")
            if isinstance(node, Inc):
                cells[dp] = (cells[dp] + 1) % BYTE_CELL_WRAP
            elif isinstance(node, Dec):
                cells[dp] = (cells[dp] - 1) % BYTE_CELL_WRAP
            elif isinstance(node, Right):
                dp += 1
                if dp >= tape_size:
                    raise RuntimeError(f"BF data pointer ran off tape (size {tape_size})")
            elif isinstance(node, Left):
                dp -= 1
                if dp < 0:
                    raise RuntimeError("BF data pointer ran off tape to the left")
            elif isinstance(node, Loop):
                while cells[dp] != 0:
                    execute(node.body)
                    ops += 1
                    if ops > max_ops:
                        raise RuntimeError(f"BF byte runner exceeded max_ops={max_ops}")
            elif isinstance(node, Put):
                output.append(cells[dp])
            elif isinstance(node, Get):
                if in_pos < len(stdin):
                    cells[dp] = stdin[in_pos]
                    in_pos += 1
                else:
                    cells[dp] = 0

    execute(ast)
    return bytes(output)
