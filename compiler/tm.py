"""Turing machine: deterministic single-tape, finite state, finite alphabet.

Tape is sparse: positions not explicitly stored are blank. Tape symbols are
integers; the blank symbol is configurable per machine. Directions are 'L',
'R', or 'S' (stay).

Transition lookup: if `(state, symbol)` has no entry, the machine halts.
"""

from dataclasses import dataclass
from typing import Mapping

Transition = tuple[str, int, str]


@dataclass(frozen=True)
class TM:
    transitions: Mapping[tuple[str, int], Transition]
    initial_state: str
    initial_tape: tuple[int, ...] = ()
    initial_head: int = 0
    blank: int = 0


@dataclass(frozen=True)
class TMState:
    state: str
    tape: tuple[tuple[int, int], ...]
    head: int
    halted: bool = False

    def read(self, blank: int) -> int:
        for pos, val in self.tape:
            if pos == self.head:
                return val
        return blank

    def tape_value(self, pos: int, blank: int) -> int:
        for p, v in self.tape:
            if p == pos:
                return v
        return blank


def initial(tm: TM) -> TMState:
    tape = tuple(
        sorted((i, v) for i, v in enumerate(tm.initial_tape) if v != tm.blank)
    )
    return TMState(tm.initial_state, tape, tm.initial_head)


def step(tm: TM, ts: TMState) -> TMState:
    if ts.halted:
        return ts
    sym = ts.read(tm.blank)
    key = (ts.state, sym)
    if key not in tm.transitions:
        return TMState(ts.state, ts.tape, ts.head, halted=True)
    new_state, write_sym, direction = tm.transitions[key]
    tape_dict = dict(ts.tape)
    if write_sym == tm.blank:
        tape_dict.pop(ts.head, None)
    else:
        tape_dict[ts.head] = write_sym
    new_tape = tuple(sorted(tape_dict.items()))
    delta = {"L": -1, "R": 1, "S": 0}[direction]
    return TMState(new_state, new_tape, ts.head + delta, halted=False)


def run(tm: TM, max_steps: int) -> list[TMState]:
    ts = initial(tm)
    history = [ts]
    for _ in range(max_steps):
        if ts.halted:
            break
        ts = step(tm, ts)
        history.append(ts)
    return history
