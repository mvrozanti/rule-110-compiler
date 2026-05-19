"""Benchmark Rule 110 evolvers across CPU and GPU paths.

Compares:
  - pure-python   `core.rule110.step` looped (tuple-of-ints, ether boundary)
  - numpy         `core.rule110_fast.evolve_numpy`
  - cupy          `core.rule110_gpu.evolve_gpu`
  - cupy batch    `core.rule110_gpu.evolve_batch_gpu` over many ICs

Run with the GPU venv:
  source .venv-gpu/bin/activate
  python scripts/bench_gpu.py
"""

import random
import time

from core.rule110 import evolve as evolve_py
from core.rule110_fast import evolve_numpy


def _rand_state(n: int, seed: int):
    rng = random.Random(seed)
    return tuple(rng.randint(0, 1) for _ in range(n))


def _bench(label: str, fn, warmup: int = 1, runs: int = 1):
    for _ in range(warmup):
        fn()
    t0 = time.perf_counter()
    for _ in range(runs):
        fn()
    dt = (time.perf_counter() - t0) / runs
    print(f"  {label:<22} {dt*1000:>10.2f} ms")
    return dt


def main():
    print("=" * 64)
    print("Rule 110 evolver benchmark")
    print("=" * 64)

    try:
        from core.rule110_gpu import evolve_batch_gpu, evolve_gpu
        import cupy as cp
        has_gpu = True
        cp.cuda.runtime.deviceSynchronize()
    except Exception as e:
        has_gpu = False
        print(f"(no GPU path: {e})")

    cases = [
        ("small  ",   200,    300),
        ("medium ",  2000,   1000),
        ("large  ",  6000,   3000),
        ("xlarge ", 20000,   5000),
    ]

    for label, n, steps in cases:
        print(f"\n[{label.strip()}]  n={n} cells, steps={steps}")
        state = _rand_state(n, 0)

        if n <= 2000 and steps <= 1000:
            _bench("python    (step loop)", lambda: evolve_py(state, steps))
        else:
            print(f"  {'python    (step loop)':<22} {'(skipped — too slow)':>10}")

        t_np = _bench("numpy     (evolve)", lambda: evolve_numpy(state, steps))

        if has_gpu:
            def gpu_fn():
                r = evolve_gpu(state, steps)
                cp.cuda.runtime.deviceSynchronize()
                return r
            t_gpu = _bench("cupy      (evolve)", gpu_fn, warmup=2)
            print(f"  speedup vs numpy: {t_np / t_gpu:>4.1f}×")

    if has_gpu:
        print("\n[batch]  evolve 256 independent IC of 4096 cells × 1000 steps")
        seeds = list(range(256))
        states = [_rand_state(4096, s) for s in seeds]

        def serial_numpy():
            for s in states:
                evolve_numpy(s, 1000)
        t_serial = _bench("numpy serial loop  ", serial_numpy)

        def gpu_batch():
            r = evolve_batch_gpu(states, 1000)
            cp.cuda.runtime.deviceSynchronize()
            return r
        t_batch = _bench("cupy batch         ", gpu_batch, warmup=2)
        print(f"  speedup vs numpy serial: {t_serial / t_batch:>4.1f}×")


if __name__ == "__main__":
    main()
