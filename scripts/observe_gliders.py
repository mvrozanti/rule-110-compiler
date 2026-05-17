"""Observe Rule 110 evolution from a random initial condition, then look for
emergent glider structures by scanning the spacetime diagram for periodic
columns matching Cook's documented (period_t, displacement) pairs.

This complements `discover_gliders.py`: when exhaustive perturbation search
fails to find a glider directly (because the natural pattern is too wide for
brute force), we instead let Rule 110 evolve and watch for self-similar
structures.
"""

import random

from core.ether import SPATIAL_PERIOD, ether_window
from core.rule110 import step


COOK_GLIDERS = [
    ("C-class", 7, 0),
    ("A",       3, +2),
    ("B",       4, -2),
    ("D-class", 10, +2),
    ("Ebar",    30, -8),
]


def evolve_with_history(state, n_steps):
    history = [state]
    for _ in range(n_steps):
        state = step(state, boundary="ether")
        history.append(state)
    return history


def find_persistent_diffs(history, anchor, scan_radius=20):
    """Cells that differ from ether at *every* time in history; their relative
    positions across time describe a structure that might be a glider."""
    n_t = len(history)
    width = len(history[0])
    diff_columns = []
    for t in range(n_t):
        row = history[t]
        ether = ether_window(t * 4, width)
        diffs = [q for q in range(max(0, anchor - scan_radius),
                                  min(width, anchor + scan_radius + 1))
                 if row[q] != ether[q]]
        diff_columns.append(diffs)
    return diff_columns


def detect_glider(diff_columns, period_t, displacement, slack=2):
    """Does the diff pattern at time t equal the diff pattern at time t+period_t
    shifted by `displacement`, for the central portion of the trace?"""
    n_t = len(diff_columns)
    if n_t < 2 * period_t + 5:
        return False

    matches = 0
    for t in range(period_t, n_t - period_t):
        early = diff_columns[t]
        late = diff_columns[t + period_t]
        late_shifted = [q - displacement for q in late]
        if set(early) == set(late_shifted):
            matches += 1
    return matches >= 5


def run(seed, ic_bits=24, n_steps=300):
    random.seed(seed)
    width = SPATIAL_PERIOD * 20
    anchor = width // 2
    state = list(ether_window(0, width))
    for k in range(ic_bits):
        state[anchor + k] = random.randint(0, 1)
    state = tuple(state)

    history = evolve_with_history(state, n_steps)
    diff_cols = find_persistent_diffs(history, anchor, scan_radius=40)

    print(f"seed={seed}: {sum(1 for d in diff_cols if d)}/{len(diff_cols)} rows have non-ether cells")

    for label, t, d in COOK_GLIDERS:
        if detect_glider(diff_cols, t, d):
            print(f"  found {label} (period {t}, disp {d})")


def main():
    for seed in range(40):
        run(seed)


if __name__ == "__main__":
    main()
