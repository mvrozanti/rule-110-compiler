"""Cyclic Tag System: a Turing-complete rewriting system.

A CTS has:
  - An alphabet (here always {'Y', 'N'} since Cook's encoding uses these).
  - A finite cyclic list of appendants, each a string over the alphabet.
  - A tape, a string over the alphabet.

One step:
  - If the tape is empty, the system halts.
  - Otherwise, look at the leftmost symbol of the tape:
      - If 'Y', pop it and append the current appendant to the tape's right.
      - If 'N', pop it (no append).
  - Advance the appendant cursor cyclically.

References: Cook 2004 §2.2; original CTS due to Wolfram (NKS p.95).
"""

from dataclasses import dataclass

Symbol = str
Tape = tuple[Symbol, ...]
Appendant = tuple[Symbol, ...]


@dataclass(frozen=True)
class CTSSpec:
    appendants: tuple[Appendant, ...]
    initial_tape: Tape

    def __post_init__(self) -> None:
        if not self.appendants:
            raise ValueError("CTS needs at least one appendant")
        for app in self.appendants:
            for s in app:
                if s not in ("Y", "N"):
                    raise ValueError(f"appendant symbol {s!r} not in {{Y, N}}")
        for s in self.initial_tape:
            if s not in ("Y", "N"):
                raise ValueError(f"tape symbol {s!r} not in {{Y, N}}")


@dataclass(frozen=True)
class CTSState:
    tape: Tape
    cursor: int

    @property
    def halted(self) -> bool:
        return len(self.tape) == 0


def step(spec: CTSSpec, state: CTSState) -> CTSState:
    if state.halted:
        return state
    head, rest = state.tape[0], state.tape[1:]
    if head == "Y":
        new_tape = rest + spec.appendants[state.cursor]
    else:
        new_tape = rest
    return CTSState(new_tape, (state.cursor + 1) % len(spec.appendants))


def run(spec: CTSSpec, max_steps: int) -> list[CTSState]:
    state = CTSState(spec.initial_tape, cursor=0)
    history = [state]
    for _ in range(max_steps):
        if state.halted:
            break
        state = step(spec, state)
        history.append(state)
    return history
