"""Tag system simulator (Cook 2004 §2.1; original due to Post).

A p-tag system removes `delete_count` symbols from the front of the tape per
step and uses *only the first* of them to look up the appendant in a finite
map. Cook uses p=2 throughout.

Halting: when the tape has fewer than `delete_count` symbols, or when the
first symbol has no production.
"""

from dataclasses import dataclass
from typing import Mapping

Symbol = str
Tape = tuple[Symbol, ...]
Appendant = tuple[Symbol, ...]


@dataclass(frozen=True)
class TagSystem:
    productions: Mapping[Symbol, Appendant]
    initial_tape: Tape
    delete_count: int = 2


@dataclass(frozen=True)
class TagState:
    tape: Tape

    @property
    def halted(self) -> bool:
        return len(self.tape) == 0


def step(ts: TagSystem, st: TagState) -> TagState:
    if len(st.tape) < ts.delete_count:
        return TagState(())
    head = st.tape[0]
    if head not in ts.productions:
        return TagState(())
    rest = st.tape[ts.delete_count:]
    return TagState(rest + ts.productions[head])


def run(ts: TagSystem, max_steps: int) -> list[TagState]:
    st = TagState(ts.initial_tape)
    history = [st]
    for _ in range(max_steps):
        if st.halted:
            break
        new = step(ts, st)
        if new == st:
            break
        st = new
        history.append(st)
    return history
