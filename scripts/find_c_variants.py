"""Search for additional C-glider variants (Cook C1=width 9, C2=width 3, C3=width 11).

Our verified C has zero ether-width (compiler/cts_to_r110.py + test_alpha_beta.py).
Cook's tape-data construction uses C2 specifically. Locate a C2-class glider
empirically.

Strategy: random-IC track sweep with longer evolution, looking for any
stationary period-7 glider whose post-glider ether is OFFSET from the
pre-glider ether by some non-zero amount mod 14. Each hit is verified by
placement on clean ether and 4-period propagation.
"""

import random
import sys

from core.ether import SPATIAL_PERIOD, ether_cell, ether_window
from core.rule110 import step


T_C = 7
D_C = 0


def evolve_one(state):
    return step(state, boundary="ether")


def diff_clusters(state, time, gap=4):
    diffs = [i for i in range(len(state)) if state[i] != ether_cell(i + 4 * time)]
    if not diffs:
        return []
    groups = [[diffs[0]]]
    for q in diffs[1:]:
        if q - groups[-1][-1] <= gap:
            groups[-1].append(q)
        else:
            groups.append([q])
    return groups


def verify_period_7_stationary(captured_bits, anchor, capture_time):
    """Place captured bits on clean ether at the same ether phase as
    capture, evolve 7 steps, check the same bits reappear at the same
    position. Repeat for 4 periods to weed out coincidences.
    """
    halo = 20
    span = len(captured_bits)
    ambient = 4 * SPATIAL_PERIOD * 20
    base_phase = (anchor + 4 * capture_time) % SPATIAL_PERIOD
    place_anchor = ambient // 2
    place_anchor += (base_phase - place_anchor) % SPATIAL_PERIOD
    s = list(ether_window(0, ambient))
    for j, b in enumerate(captured_bits):
        s[place_anchor + j] = b
    s_tup = tuple(s)
    for k in range(1, 5):
        for _ in range(T_C):
            s_tup = evolve_one(s_tup)
        moved = place_anchor + k * D_C
        shift = 4 * k * T_C
        for j in range(span):
            pos = moved + j
            if not (0 <= pos < ambient):
                return None
            if s_tup[pos] != captured_bits[j]:
                return None
        for j in range(-halo, 0):
            pos = moved + j
            if 0 <= pos < ambient and s_tup[pos] != ether_cell(pos + shift):
                return None
        for j in range(span, span + halo):
            pos = moved + j
            if 0 <= pos < ambient and s_tup[pos] != ether_cell(pos + shift):
                return None
    return place_anchor


def compute_width(captured_bits, anchor, capture_time):
    """Width per Cook: ether offset (mod 14) of right-of-glider vs
    left-of-glider extrapolated.
    """
    base_phase = (anchor + 4 * capture_time) % SPATIAL_PERIOD
    pure_right_phase = (base_phase + len(captured_bits)) % SPATIAL_PERIOD
    place_anchor = verify_period_7_stationary(captured_bits, anchor, capture_time)
    if place_anchor is None:
        return None
    ambient = 4 * SPATIAL_PERIOD * 20
    s = list(ether_window(0, ambient))
    for j, b in enumerate(captured_bits):
        s[place_anchor + j] = b
    s_tup = tuple(s)
    for _ in range(T_C):
        s_tup = evolve_one(s_tup)
    shift = 4 * T_C
    right_start = place_anchor + len(captured_bits)
    for offset in range(SPATIAL_PERIOD):
        ok = True
        for i in range(20):
            pos = right_start + i
            if s_tup[pos] != ether_cell(pos + offset + shift):
                ok = False
                break
        if ok:
            return offset
    return None


def main():
    n_seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    found_widths = {}
    width = SPATIAL_PERIOD * 200
    anchor = width // 2

    for seed in range(n_seeds):
        rng = random.Random(seed)
        ic_bits = rng.choice([8, 12, 16, 24, 32, 48])
        s = list(ether_window(0, width))
        for k in range(ic_bits):
            s[anchor + k] = rng.randint(0, 1)
        state = tuple(s)
        snapshots = [state]
        for _ in range(500):
            state = evolve_one(state)
            snapshots.append(state)

        for t in range(300, 480, 30):
            clusters = diff_clusters(snapshots[t], t, gap=4)
            for c in clusters:
                if len(c) < 3 or c[-1] - c[0] > 30:
                    continue
                if c[0] < 100 or c[-1] >= len(snapshots[t]) - 100:
                    continue
                lo, hi = c[0], c[-1]
                bits = tuple(snapshots[t][lo:hi + 1])
                ok = verify_period_7_stationary(bits, lo, t)
                if ok is None:
                    continue
                w = compute_width(bits, lo, t)
                if w is None:
                    continue
                key = (w, len(bits))
                if key not in found_widths or len(found_widths[key]["bits"]) > len(bits):
                    found_widths[key] = {
                        "bits": bits, "width": w, "seed": seed, "t": t, "lo": lo,
                    }
                    print(f"  width={w} extent={len(bits)} seed={seed} t={t}: bits={bits}", flush=True)

    print(f"\nDistinct (width, extent) classes found: {len(found_widths)}")
    for (w, ext), info in sorted(found_widths.items()):
        print(f"  width={w} extent={ext}: {info['bits']}")


if __name__ == "__main__":
    main()
