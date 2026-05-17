"""Brainfuck parser. AST is a flat list with `Loop` nodes containing nested
ASTs. Unbalanced brackets raise. The subset supported is the canonical
8 instructions; `.` and `,` are parsed but emit no I/O in MVP-B.
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
