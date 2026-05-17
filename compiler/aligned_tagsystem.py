"""Aligned 2-tag system: a 2-tag with an explicit `use_offset` ∈ {0, 1} that
tracks which symbol of the leading pair fires the production.

Standard 2-tag (compiler/tagsystem.py) hardcodes use_offset = 0. Cook's
TM-to-tag reduction (§2.1) needs us to start sometimes at use_offset = 1
(when the encoded head bit is 0), and the appendant lengths drive a parity
flip of use_offset after each step.
"""

from dataclasses import dataclass
from typing import Mapping

Symbol = str
Tape = tuple[Symbol, ...]
Appendant = tuple[Symbol, ...]


@dataclass(frozen=True)
class AlignedTagSystem:
    productions: Mapping[Symbol, Appendant]
    initial_tape: Tape
    initial_use_offset: int = 0


@dataclass(frozen=True)
class AlignedTagState:
    tape: Tape
    use_offset: int

    @property
    def halted(self) -> bool:
        return len(self.tape) < 2


def step(ts: AlignedTagSystem, st: AlignedTagState) -> AlignedTagState:
    if st.halted:
        return st
    sym = st.tape[st.use_offset]
    if sym not in ts.productions:
        return st
    appendant = ts.productions[sym]
    new_tape = st.tape[2:] + appendant
    new_offset = st.use_offset ^ (len(appendant) % 2)
    return AlignedTagState(new_tape, new_offset)


def run(ts: AlignedTagSystem, max_steps: int) -> list[AlignedTagState]:
    state = AlignedTagState(ts.initial_tape, ts.initial_use_offset)
    history = [state]
    for _ in range(max_steps):
        if state.halted:
            break
        new = step(ts, state)
        if new == state:
            break
        state = new
        history.append(state)
    return history
