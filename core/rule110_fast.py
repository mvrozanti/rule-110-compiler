"""Numpy-accelerated Rule 110 evolution for long simulations.

Mirrors `core.rule110.step` exactly (same rule table, same `boundary="ether"`
convention) but uses vectorised numpy ops so a 60k-cell state evolved for
28k steps runs in seconds instead of tens of minutes. Imported lazily so the
project's hard dependency stays numpy-free.
"""

import numpy as np

from core.ether import SPATIAL_PERIOD, ether_cell


_RULE_110_LUT = np.array(
    [0, 1, 1, 1, 0, 1, 1, 0], dtype=np.uint8
)


def evolve_numpy(state: tuple[int, ...], steps: int) -> tuple[int, ...]:
    """Evolve `state` forward `steps` Rule 110 steps with "ether" boundary.

    Same semantics as iterating `core.rule110.step(..., boundary="ether")`
    `steps` times; just vectorised. Returns a tuple in the same format.
    """
    n = len(state)
    arr = np.asarray(state, dtype=np.uint8)
    left_boundary = np.array([ether_cell(-1)], dtype=np.uint8)
    right_boundary = np.array([ether_cell(n)], dtype=np.uint8)
    for _ in range(steps):
        L = np.concatenate([left_boundary, arr[:-1]])
        R = np.concatenate([arr[1:], right_boundary])
        idx = (L << 2) | (arr << 1) | R
        arr = _RULE_110_LUT[idx]
    return tuple(int(b) for b in arr)
