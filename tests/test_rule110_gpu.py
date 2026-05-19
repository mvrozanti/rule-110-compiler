"""GPU evolver must match numpy evolver bit-for-bit.

If cupy is not installed the test suite skips silently. The intended
runtime is `bash scripts/setup_gpu.sh && source .venv-gpu/bin/activate`
on Blackwell-or-newer NVIDIA (compute 12.0); other GPUs need a wheel
matching their CUDA major.
"""

import random

import pytest

from core.ether import ETHER, ether_window
from core.rule110_fast import evolve_numpy


cp = pytest.importorskip("cupy")

from core.rule110_gpu import evolve_batch_gpu, evolve_gpu, evolve_history_gpu


def _rand_state(n: int, seed: int) -> tuple[int, ...]:
    rng = random.Random(seed)
    return tuple(rng.randint(0, 1) for _ in range(n))


@pytest.mark.parametrize("n,steps,seed", [
    (64, 50, 0),
    (200, 100, 1),
    (1000, 250, 2),
    (5000, 500, 3),
])
def test_gpu_matches_numpy_random(n, steps, seed):
    state = _rand_state(n, seed)
    assert evolve_gpu(state, steps) == evolve_numpy(state, steps)


def test_gpu_matches_numpy_ether_only():
    state = ether_window(0, 280)
    assert evolve_gpu(state, 300) == evolve_numpy(state, 300)


def test_history_first_and_last_match():
    state = _rand_state(512, 7)
    steps = 128
    hist = evolve_history_gpu(state, steps)
    assert len(hist) == steps + 1
    assert hist[0] == state
    assert hist[-1] == evolve_numpy(state, steps)


def test_batch_matches_serial_numpy():
    seeds = list(range(8))
    n, steps = 256, 60
    states = [_rand_state(n, s) for s in seeds]
    batch_final = cp.asnumpy(evolve_batch_gpu(states, steps))
    for i, s in enumerate(seeds):
        expected = evolve_numpy(states[i], steps)
        got = tuple(int(b) for b in batch_final[i])
        assert got == expected, f"batch row {i} (seed {s}) diverges"
