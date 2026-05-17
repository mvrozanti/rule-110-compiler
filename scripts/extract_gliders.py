"""Extract minimal bit patterns of Cook's gliders from random Rule 110 evolutions.

Approach:
  1. Run from a random IC in a *wide* ether context for a *short* settle time
     so boundary contamination cannot reach the central observation region.
  2. At the settle time, look at the (sparse) cells that differ from the
     correctly-phased ether and identify connected components.
  3. For each component, check against each Cook glider's known (period, disp).
     A match means: the component at t+period equals the component shifted by
     disp, *and* the same holds at t+2*period (sanity check against false
     positives from short patterns).
  4. Record the minimal cell-level delta and the ether-phase context.
"""

import random
import sys

from core.ether import SPATIAL_PERIOD, ether_window
from core.rule110 import step


COOK_TARGETS = [
    ("A",   3, +2),
    ("B",   4, -2),
    ("C",   7,  0),
    ("D",  10, +2),
    ("E",  15, -4),
    ("Eb", 30, -8),
]


def evolve_history(state, n_steps):
    history = [state]
    for _ in range(n_steps):
        state = step(state, boundary="ether")
        history.append(state)
    return history


def diff_from_ether(state, t):
    width = len(state)
    ref = ether_window(t * 4, width)
    return [q for q in range(width) if state[q] != ref[q]]


def connected_components(diffs, gap=3):
    if not diffs:
        return []
    diffs = sorted(diffs)
    groups = [[diffs[0]]]
    for q in diffs[1:]:
        if q - groups[-1][-1] <= gap:
            groups[-1].append(q)
        else:
            groups.append([q])
    return groups


def diffs_in_window(history, t, lo, hi):
    if lo < 0 or hi > len(history[0]):
        return None
    return tuple(q - lo for q in diff_from_ether(history[t], t) if lo <= q < hi)


def check_target(history, t0, group, T, D, halo=4, min_delta_cells=3, periods_to_check=5):
    left, right = group[0] - halo, group[-1] + halo + 1
    base = diffs_in_window(history, t0, left, right)
    if not base or len(base) < min_delta_cells:
        return False
    confirmations = 0
    for k in range(1, periods_to_check + 1):
        t_target = t0 + k * T
        if t_target >= len(history):
            break
        shifted = diffs_in_window(history, t_target, left + k * D, right + k * D)
        if shifted != base:
            return False
        confirmations += 1
    return confirmations >= 2


def extract(history, t0, group, halo=4):
    width = len(history[0])
    left = max(0, group[0] - halo)
    right = min(width, group[-1] + halo + 1)
    state = history[t0]
    ref = ether_window(t0 * 4, width)
    delta = tuple((q - left, state[q]) for q in range(left, right) if state[q] != ref[q])
    window = state[left:right]
    return delta, window, left


def normalize_minimal(delta):
    """Drop leading/trailing same-as-ether cells from a delta pattern."""
    if not delta:
        return delta
    first = delta[0][0]
    last = delta[-1][0]
    return tuple((o - first, b) for o, b in delta), first, last - first + 1


def run_seed(seed, ic_bits=24, settle=40, observe=80):
    random.seed(seed)
    width = SPATIAL_PERIOD * 80
    anchor = width // 2
    state = list(ether_window(0, width))
    for k in range(ic_bits):
        state[anchor + k] = random.randint(0, 1)
    state = tuple(state)

    history = evolve_history(state, settle + observe + 200)
    found = {}
    for t0 in (settle, settle + 20, settle + 40):
        diffs = diff_from_ether(history[t0], t0)
        for g in connected_components(diffs, gap=3):
            for label, T, D in COOK_TARGETS:
                if not check_target(history, t0, g, T, D):
                    continue
                delta, window, left = extract(history, t0, g)
                if not delta:
                    continue
                norm_delta, first_offset, span = normalize_minimal(delta)
                key = (label, norm_delta)
                if key in found:
                    continue
                found[key] = {
                    "t0": t0,
                    "T": T,
                    "D": D,
                    "left_phase": (left + first_offset + 4 * t0) % SPATIAL_PERIOD,
                    "span": span,
                    "window": window,
                    "first_offset": first_offset,
                }
                break
    return found


def visualize_delta(delta, span):
    glyphs = ["."] * span
    for o, b in delta:
        glyphs[o] = str(b)
    return "".join(glyphs)


def main():
    seeds = list(range(60))
    if len(sys.argv) > 1:
        seeds = [int(s) for s in sys.argv[1:]]

    catalog = {}
    for seed in seeds:
        found = run_seed(seed)
        for (label, norm_delta), info in found.items():
            key = label
            existing = catalog.get(key)
            if existing is None or info["span"] < existing["span"]:
                info["delta"] = norm_delta
                info["seed"] = seed
                catalog[key] = info

    for label, info in catalog.items():
        viz = visualize_delta(info["delta"], info["span"])
        cells = ",".join(f"{o:+d}={b}" for o, b in info["delta"])
        print(f"\n{label}  T={info['T']:>2d}  D={info['D']:+d}  span={info['span']:>2d}  "
              f"left_phase={info['left_phase']:>2d}  seed={info['seed']}")
        print(f"  delta vs ether: {viz}")
        print(f"  cells:          {cells}")


if __name__ == "__main__":
    main()
