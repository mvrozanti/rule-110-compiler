"""Find Cook gliders by isolating clean late-time structures and verifying
each in pure ether.

Strategy:
  1. Wide state (many ether periods), random initial perturbation.
  2. Evolve long enough that chaotic activity has annihilated, leaving a
     sparse field of separated gliders moving on a clean ether background.
  3. At several late times, look at diff-from-ether cells; cluster them
     into spatial groups separated by GAPS of pure ether.
  4. For each isolated cluster, capture the FULL window (with halo) of that
     stretch of tape.
  5. Re-place the captured window in a fresh ether context at the matching
     phase and probe (period, displacement) pairs from Cook's documented
     list. If the entire window reappears shifted by N*displacement after
     N*period steps for several N, the window IS that glider.
"""

import random
import sys

from core.ether import SPATIAL_PERIOD, ether_window
from core.rule110 import step


COOK = [
    ("A",   3, +2),
    ("B",   4, -2),
    ("C",   7,  0),
    ("D",  10, +2),
    ("E",  15, -4),
    ("Eb", 30, -8),
]


def diff_from_ether_at_t(state, t):
    width = len(state)
    ref = ether_window(t * 4, width)
    return [q for q in range(width) if state[q] != ref[q]]


def isolated_clusters(diffs, min_gap=30):
    if not diffs:
        return []
    diffs = sorted(diffs)
    groups = [[diffs[0]]]
    for q in diffs[1:]:
        if q - groups[-1][-1] >= min_gap:
            groups.append([q])
        else:
            groups[-1].append(q)
    return groups


def verify_window_as_glider(captured, capture_anchor, capture_t, T, D, n_periods=3):
    width = SPATIAL_PERIOD * 80
    window_len = len(captured)

    target_phase = (capture_anchor + capture_t * 4) % SPATIAL_PERIOD
    base = SPATIAL_PERIOD * 30
    place_anchor = base + ((target_phase - base % SPATIAL_PERIOD) % SPATIAL_PERIOD)

    state = list(ether_window(0, width))
    for j in range(window_len):
        if 0 <= place_anchor + j < width:
            state[place_anchor + j] = captured[j]
    s = tuple(state)

    for k in range(1, n_periods + 1):
        for _ in range(T):
            s = step(s, boundary="ether")
        for j in range(window_len):
            pos = place_anchor + k * D + j
            if not (0 <= pos < width):
                return None
            if s[pos] != captured[j]:
                return None
    return place_anchor, target_phase


def delta_signature(captured, capture_anchor, capture_t):
    ref = ether_window(capture_t * 4 + capture_anchor, len(captured))
    delta = tuple((j, captured[j]) for j in range(len(captured)) if captured[j] != ref[j])
    if not delta:
        return ()
    first = delta[0][0]
    return tuple((o - first, b) for o, b in delta)


def run_seed(seed, ic_bits=40, settle=400, observe_steps=(400, 500, 600, 700, 800)):
    random.seed(seed)
    width = SPATIAL_PERIOD * 200
    anchor = width // 2
    state = list(ether_window(0, width))
    for k in range(ic_bits):
        state[anchor + k] = random.randint(0, 1)
    state = tuple(state)

    snapshots = []
    for t in range(1, max(observe_steps) + 1):
        state = step(state, boundary="ether")
        if t in observe_steps:
            snapshots.append((t, state))

    found = {}
    for t, st in snapshots:
        diffs = diff_from_ether_at_t(st, t)
        clusters = isolated_clusters(diffs, min_gap=30)
        for c in clusters:
            extent = c[-1] - c[0] + 1
            if extent > 35:
                continue
            for halo in (4, 8):
                left = max(0, c[0] - halo)
                right = min(len(st), c[-1] + halo + 1)
                captured = st[left:right]
                for label, T, D in COOK:
                    result = verify_window_as_glider(captured, left, t, T, D, n_periods=4)
                    if result is None:
                        continue
                    sig = delta_signature(captured, left, t)
                    key = label
                    span_now = len(sig)
                    phase = (left + t * 4) % SPATIAL_PERIOD
                    if key in found and found[key][3] <= span_now:
                        continue
                    found[key] = (T, D, sig, span_now, halo, t, seed, captured, phase, left)
                    break
                else:
                    continue
                break
    return found


def main():
    seeds = list(range(120))
    if len(sys.argv) > 1:
        seeds = [int(x) for x in sys.argv[1:]]

    catalog = {}
    for seed in seeds:
        found = run_seed(seed)
        for label, info in found.items():
            existing = catalog.get(label)
            if existing is None or info[3] < existing[3]:
                catalog[label] = info

    print(f"\nverified gliders: {len(catalog)}/{len(COOK)}\n")
    for label, info in sorted(catalog.items()):
        T, D, sig, sig_len, halo, t, sd, captured, phase, left = info
        span = (max(o for o, _ in sig) - min(o for o, _ in sig) + 1) if sig else 0
        cells = ",".join(f"{o:+d}={b}" for o, b in sig)
        captured_str = "".join(str(b) for b in captured)
        print(f"{label:4s} T={T:>2d} D={D:+d}  span={span:>2d}  halo={halo:>2d}  "
              f"seed={sd:>3d} t={t}  phase={phase}")
        print(f"      delta:   {cells}")
        print(f"      window:  {captured_str}")
        print(f"      ether*:  {''.join(str(b) for b in ether_window(t*4 + left, len(captured)))}")
        print()


if __name__ == "__main__":
    main()
