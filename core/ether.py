"""Rule 110 ether background: spatial period 14, temporal period 7.

A single step of Rule 110 translates the ether pattern left by 4 cells, so
after 7 steps the cumulative shift is 28 = 2 * 14 and the pattern returns to
itself. Reference: Cook (2004) §3.2; Wolfram, A New Kind of Science, p. 282.
"""

ETHER: tuple[int, ...] = (1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0)
SPATIAL_PERIOD: int = 14
TEMPORAL_PERIOD: int = 7
SHIFT_PER_STEP: int = 4


def ether_cell(i: int) -> int:
    return ETHER[i % SPATIAL_PERIOD]


def ether_window(start: int, length: int) -> tuple[int, ...]:
    return tuple(ether_cell(start + k) for k in range(length))
