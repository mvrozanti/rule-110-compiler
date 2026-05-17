"""Rule 110 elementary cellular automaton with selectable boundary."""

from core.ether import ether_cell

RULE_TABLE: dict[tuple[int, int, int], int] = {
    (1, 1, 1): 0,
    (1, 1, 0): 1,
    (1, 0, 1): 1,
    (1, 0, 0): 0,
    (0, 1, 1): 1,
    (0, 1, 0): 1,
    (0, 0, 1): 1,
    (0, 0, 0): 0,
}


def step(state: tuple[int, ...], boundary: str = "ether") -> tuple[int, ...]:
    n = len(state)
    if boundary == "zero":
        def outside(i: int) -> int:
            return 0
    elif boundary == "ether":
        def outside(i: int) -> int:
            return ether_cell(i)
    else:
        raise ValueError(f"unknown boundary {boundary!r}")

    def cell(i: int) -> int:
        return state[i] if 0 <= i < n else outside(i)

    return tuple(
        RULE_TABLE[(cell(i - 1), cell(i), cell(i + 1))]
        for i in range(n)
    )


def evolve(
    state: tuple[int, ...], steps: int, boundary: str = "ether"
) -> list[tuple[int, ...]]:
    history = [tuple(state)]
    for _ in range(steps):
        history.append(step(history[-1], boundary))
    return history
