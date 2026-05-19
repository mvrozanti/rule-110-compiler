---
type: incident
era: side-projects
tags: [rule-110, performance, numpy, test-suite]
date: 2026-05-18
---

# 42-minute test ran on slow python evolver

The headline BF '++' → 8-Cook-crossings test runs on a 28,000-step Rule 110 evolution over a ~12,500-cell state. Pure-Python `core/rule110.step` iterates per cell per step. First run: **2,559 seconds** (42 min 40 s) to verify a single empirical claim.

The test passed once empirically. Marked `@pytest.mark.slow` and excluded from the default suite via `addopts = "-m 'not slow'"` in `pyproject.toml`. But excluding the headline from CI was the wrong fix — slips of the test would go unnoticed.

> [!fix]
> `core/rule110_fast.evolve_numpy` — vectorised step using a length-8 uint8 lookup table. Same semantics (`boundary="ether"`), 100× speedup on benchmarks. The headline test re-runs in **18 seconds**. The `slow` marker and `addopts` exclusion were both removed.

`numpy` was already declared optional in `pyproject.toml` (`fast = ["numpy>=1.26"]`); the fast evolver imports lazily so the project's hard dependency stays numpy-free.

Lesson: when a test is too slow to run, the *test* isn't the problem — the simulator is. Excluding the test as `slow` masks the underlying tractability cost. Fix the simulator first.

## Connects to

- [[Rule 110 compiler]]
- [[Cook crossing window]]
