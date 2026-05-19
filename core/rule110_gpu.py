"""CUDA-accelerated Rule 110 evolution via CuPy.

Mirrors core.rule110.step (rule 110, "ether" boundary) and matches the
output of core.rule110_fast.evolve_numpy bit-for-bit. Adds a batch
variant `evolve_batch_gpu` that evolves N independent initial conditions
in parallel — the win for exhaustive-search scripts that today loop
over thousands of ICs serially.

CuPy is imported lazily. Callers should catch `ImportError` and fall
back to evolve_numpy.
"""

from __future__ import annotations

from core.ether import ether_cell

_RULE_TABLE = (0, 1, 1, 1, 0, 1, 1, 0)


def _require_cupy():
    import cupy as cp
    return cp


def evolve_gpu(state: tuple[int, ...], steps: int) -> tuple[int, ...]:
    """Evolve one state forward `steps` Rule 110 steps with ether boundary.

    Parity guarantee: returns the same tuple as evolve_numpy(state, steps).
    """
    cp = _require_cupy()
    lut = cp.asarray(_RULE_TABLE, dtype=cp.uint8)
    n = len(state)
    arr = cp.asarray(state, dtype=cp.uint8)
    left_b = cp.asarray([ether_cell(-1)], dtype=cp.uint8)
    right_b = cp.asarray([ether_cell(n)], dtype=cp.uint8)
    for _ in range(steps):
        L = cp.concatenate((left_b, arr[:-1]))
        R = cp.concatenate((arr[1:], right_b))
        idx = (L << 2) | (arr << 1) | R
        arr = lut[idx]
    return tuple(int(b) for b in cp.asnumpy(arr))


def evolve_history_gpu(state: tuple[int, ...], steps: int) -> list[tuple[int, ...]]:
    """Evolve and return every intermediate frame.

    Useful for the viz/decode pipelines. Frame [0] is the initial state;
    output length is steps + 1.
    """
    cp = _require_cupy()
    lut = cp.asarray(_RULE_TABLE, dtype=cp.uint8)
    n = len(state)
    arr = cp.asarray(state, dtype=cp.uint8)
    left_b = cp.asarray([ether_cell(-1)], dtype=cp.uint8)
    right_b = cp.asarray([ether_cell(n)], dtype=cp.uint8)
    history_gpu = cp.empty((steps + 1, n), dtype=cp.uint8)
    history_gpu[0] = arr
    for t in range(steps):
        L = cp.concatenate((left_b, arr[:-1]))
        R = cp.concatenate((arr[1:], right_b))
        idx = (L << 2) | (arr << 1) | R
        arr = lut[idx]
        history_gpu[t + 1] = arr
    host = cp.asnumpy(history_gpu)
    return [tuple(int(b) for b in row) for row in host]


def evolve_batch_gpu(states, steps: int):
    """Evolve N states (each width n) in parallel.

    Input: numpy / cupy / nested-tuple iterable of shape (N, n) uint8.
    Output: cupy.ndarray of shape (N, n) holding the final state of each.
    The caller can cp.asnumpy(...) to host; we keep it on device because
    typical use case is to compute a reduction (detector match etc.)
    immediately.
    """
    cp = _require_cupy()
    lut = cp.asarray(_RULE_TABLE, dtype=cp.uint8)
    arr = cp.asarray(states, dtype=cp.uint8)
    if arr.ndim != 2:
        raise ValueError(f"states must be 2D (N, n); got shape {arr.shape}")
    n = arr.shape[1]
    left_b = cp.full((arr.shape[0], 1), ether_cell(-1), dtype=cp.uint8)
    right_b = cp.full((arr.shape[0], 1), ether_cell(n), dtype=cp.uint8)
    for _ in range(steps):
        L = cp.concatenate((left_b, arr[:, :-1]), axis=1)
        R = cp.concatenate((arr[:, 1:], right_b), axis=1)
        idx = (L << 2) | (arr << 1) | R
        arr = lut[idx]
    return arr
