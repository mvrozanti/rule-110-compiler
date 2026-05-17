"""Track isolated diff clusters across time and classify by velocity.

For each random initial condition:
  - evolve a wide ether-bedded state for many steps;
  - at every step, find connected components of diff-from-ether;
  - greedy match clusters across consecutive steps by spatial overlap;
  - for each tracked cluster, fit a velocity from its center-of-mass trajectory;
  - if the velocity matches one of Cook's gliders, capture the cluster's
    spatial window at one of its instants and verify it propagates with the
    expected (period, displacement) when placed back in clean ether.
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


def diff_cells(state, t):
    width = len(state)
    ref = ether_window(t * 4, width)
    return [q for q in range(width) if state[q] != ref[q]]


def cluster(diffs, gap=4):
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


def center(c):
    return sum(c) / len(c)


def verify_window(captured, capture_anchor, capture_t, T, D, n_periods=3):
    width = SPATIAL_PERIOD * 80
    target_phase = (capture_anchor + capture_t * 4) % SPATIAL_PERIOD
    base = SPATIAL_PERIOD * 30
    place_anchor = base + ((target_phase - base % SPATIAL_PERIOD) % SPATIAL_PERIOD)
    s = list(ether_window(0, width))
    for j, b in enumerate(captured):
        if 0 <= place_anchor + j < width:
            s[place_anchor + j] = b
    s = tuple(s)
    for k in range(1, n_periods + 1):
        for _ in range(T):
            s = step(s, boundary="ether")
        for j in range(len(captured)):
            pos = place_anchor + k * D + j
            if not (0 <= pos < width):
                return None
            if s[pos] != captured[j]:
                return None
    return target_phase


def delta_signature(captured, capture_anchor, capture_t):
    ref = ether_window(capture_t * 4 + capture_anchor, len(captured))
    delta = tuple((j, captured[j]) for j in range(len(captured)) if captured[j] != ref[j])
    if not delta:
        return ()
    first = delta[0][0]
    return tuple((o - first, b) for o, b in delta)


def run_seed(seed, ic_bits=40, total_steps=200):
    random.seed(seed)
    width = SPATIAL_PERIOD * 200
    anchor = width // 2
    state = list(ether_window(0, width))
    for k in range(ic_bits):
        state[anchor + k] = random.randint(0, 1)
    state = tuple(state)

    snapshots = [state]
    for _ in range(total_steps):
        state = step(state, boundary="ether")
        snapshots.append(state)

    tracks = []
    prev_clusters_with_id = []
    next_id = 0

    for t in range(len(snapshots)):
        diffs = diff_cells(snapshots[t], t)
        cs = cluster(diffs, gap=4)
        cs_filtered = [c for c in cs if 1 <= len(c) and c[-1] - c[0] <= 40]
        ids = []
        used_prev = set()
        for cur in cs_filtered:
            cur_c = center(cur)
            best = None
            best_dist = 1e9
            for i, (pid, pc) in enumerate(prev_clusters_with_id):
                if i in used_prev:
                    continue
                d = abs(center(pc) - cur_c)
                if d < 8 and d < best_dist:
                    best = i
                    best_dist = d
            if best is None:
                cid = next_id
                next_id += 1
                tracks.append({"id": cid, "trajectory": [(t, cur_c, cur[0], cur[-1])]})
            else:
                pid = prev_clusters_with_id[best][0]
                used_prev.add(best)
                cid = pid
                for tr in tracks:
                    if tr["id"] == cid:
                        tr["trajectory"].append((t, cur_c, cur[0], cur[-1]))
                        break
            ids.append((cid, cur))
        prev_clusters_with_id = ids

    found = {}
    for tr in tracks:
        traj = tr["trajectory"]
        if len(traj) < 25:
            continue
        t0, c0, l0, r0 = traj[0]
        t1, c1, l1, r1 = traj[-1]
        if t1 - t0 < 20:
            continue
        v = (c1 - c0) / (t1 - t0)
        for label, T, D in COOK:
            target_v = D / T
            if abs(v - target_v) > 0.05:
                continue
            for try_idx in range(len(traj) // 4, len(traj) - 5, max(1, len(traj) // 5)):
                tm, cm, lm, rm = traj[try_idx]
                for halo in (3, 6, 10):
                    left = max(0, lm - halo)
                    right = min(len(snapshots[0]), rm + halo + 1)
                    captured = snapshots[tm][left:right]
                    phase = verify_window(captured, left, tm, T, D, n_periods=3)
                    if phase is None:
                        continue
                    sig = delta_signature(captured, left, tm)
                    key = label
                    span = len(sig)
                    if key in found and found[key]["span"] <= span:
                        break
                    ref_window = ether_window(tm * 4 + left, len(captured))
                    first_diff_offset = next(
                        (j for j in range(len(captured)) if captured[j] != ref_window[j]),
                        0,
                    )
                    left_phase = (left + first_diff_offset + tm * 4) % SPATIAL_PERIOD
                    found[key] = {
                        "T": T, "D": D, "phase": phase, "left_phase": left_phase,
                        "sig": sig, "span": span,
                        "halo": halo, "tm": tm, "seed": seed, "left": left,
                        "captured": captured,
                    }
                    break
                else:
                    continue
                break
    return found


def main():
    seeds = list(range(int(sys.argv[1]) if len(sys.argv) > 1 else 80))
    catalog = {}
    for seed in seeds:
        found = run_seed(seed)
        for label, info in found.items():
            existing = catalog.get(label)
            if existing is None or info["span"] < existing["span"]:
                catalog[label] = info

    print(f"\nverified gliders: {len(catalog)}/{len(COOK)}\n")
    for label, info in sorted(catalog.items()):
        cells = ",".join(f"{o:+d}={b}" for o, b in info["sig"])
        print(f"{label:4s} T={info['T']:>2d} D={info['D']:+d}  span={info['span']:>2d}  "
              f"left_phase={info['left_phase']:>2d}  seed={info['seed']:>3d}")
        print(f"      delta:  {cells}")
        print(f"      window: {''.join(str(b) for b in info['captured'])}")
        print()


if __name__ == "__main__":
    main()
