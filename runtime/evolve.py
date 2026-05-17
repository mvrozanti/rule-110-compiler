"""Run Rule 110 forward from an encoded initial condition.

Scope: thin wrapper over core.rule110.step. The encoder
(compiler/cts_to_r110.py) emits a self-contained finite IC; the evolver
just advances it. The viz layer and decoder consume the returned
snapshots.
"""

from compiler.cts_to_r110 import R110Encoding
from core.rule110 import step


def evolve(encoding: R110Encoding, steps: int, boundary: str = "ether") -> list[tuple[int, ...]]:
    history = [encoding.initial]
    state = encoding.initial
    for _ in range(steps):
        state = step(state, boundary=boundary)
        history.append(state)
    return history


def evolve_one(state: tuple[int, ...], boundary: str = "ether") -> tuple[int, ...]:
    return step(state, boundary=boundary)
