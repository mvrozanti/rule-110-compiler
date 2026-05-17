"""Find E via long random-IC evolution with period-15 disambiguation.

Strategy:
  - Random IC over a wide ether-bedded strip.
  - Evolve much longer than the existing track_gliders sweep (1500 steps).
  - For each tracked cluster with velocity matching E or Ē (-0.267):
      * verify period exactly 15 (not 30) at multiple snapshots
      * capture the minimal delta-from-ether
"""

import random
import sys

from core.ether import SPATIAL_PERIOD, ether_cell, ether_window
from core.rule110 import step


T_E = 15
D_E = -4
TARGET_VELOCITY = D_E / T_E
TOTAL_STEPS = 1500


def ether_at(pos, time):
    return ether_cell(pos + 4 * time)


def diff_clusters(state, time, gap=4):
    diffs = [i for i in range(len(state)) if state[i] != ether_at(i, time)]
    if not diffs:
        return []
    groups = [[diffs[0]]]
    for q in diffs[1:]:
        if q - groups[-1][-1] <= gap:
            groups[-1].append(q)
        else:
            groups.append([q])
    return groups


def cluster_signature(state, time, cluster):
    lo = cluster[0]
    return tuple((p - lo, state[p]) for p in cluster)


def evolve_one(state):
    return step(state, boundary="ether")


def verify_period(state, time, cluster_lo, cluster_hi, T, D, n_periods=4):
    """Place the captured cluster on clean ether, evolve T*k steps, and
    require the same delta reappears at cluster_lo + k*D for k = 1..n_periods."""
    span = cluster_hi - cluster_lo + 1
    halo = 30
    ambient = 4 * (TOTAL_STEPS + halo + span)
    ambient = max(ambient, SPATIAL_PERIOD * 200)
    captured = state[cluster_lo:cluster_hi + 1]
    anchor = ambient // 2
    anchor = anchor - (anchor % SPATIAL_PERIOD) + (cluster_lo + 4 * time) % SPATIAL_PERIOD
    s = list(ether_window(0, ambient))
    for j, b in enumerate(captured):
        s[anchor + j] = b
    s_tup = tuple(s)
    for k in range(1, n_periods + 1):
        for _ in range(T):
            s_tup = evolve_one(s_tup)
        moved = anchor + k * D
        shift = 4 * k * T
        for j in range(span):
            pos = moved + j
            if not (0 <= pos < ambient):
                return False
            if s_tup[pos] != captured[j]:
                return False
        for j in range(-halo, 0):
            pos = moved + j
            if not (0 <= pos < ambient):
                continue
            if s_tup[pos] != ether_cell(pos + shift):
                return False
        for j in range(span, span + halo):
            pos = moved + j
            if not (0 <= pos < ambient):
                continue
            if s_tup[pos] != ether_cell(pos + shift):
                return False
    return True


def search(seed):
    rng = random.Random(seed)
    width = SPATIAL_PERIOD * 200
    anchor = width // 2
    ic_bits = rng.choice([8, 12, 16, 24, 32, 48])
    s = list(ether_window(0, width))
    for k in range(ic_bits):
        s[anchor + k] = rng.randint(0, 1)
    state = tuple(s)

    snapshots = [state]
    for _ in range(TOTAL_STEPS):
        state = evolve_one(state)
        snapshots.append(state)

    candidates = []
    sample_times = list(range(800, TOTAL_STEPS - 50, 30))
    for t in sample_times:
        clusters = diff_clusters(snapshots[t], t, gap=6)
        clusters = [c for c in clusters if 4 <= len(c) <= 30]
        clusters = [c for c in clusters if c[0] > 100 and c[-1] < len(snapshots[t]) - 100]
        for c in clusters:
            ok = verify_period(snapshots[t], t, c[0], c[-1], T_E, D_E, n_periods=3)
            if not ok:
                continue
            ok_eb = verify_period(snapshots[t], t, c[0], c[-1], 30, -8, n_periods=2)
            if ok_eb:
                continue
            candidates.append((t, c[0], c[-1], tuple(snapshots[t][c[0]:c[-1] + 1])))
    return candidates


def main():
    n_seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    hits = []
    for seed in range(n_seeds):
        results = search(seed)
        if results:
            for r in results:
                print(f"seed={seed} t={r[0]} lo={r[1]} hi={r[2]} bits={r[3]}", flush=True)
            hits.extend((seed, r) for r in results)
    print(f"\n{len(hits)} candidate captures across {n_seeds} seeds")


if __name__ == "__main__":
    main()
