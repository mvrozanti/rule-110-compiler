"""Targeted search for E glider (15, -4) via collisions of verified gliders.

Random-IC tracking (scripts/track_gliders.py) at 2000 seeds did not surface E.
Either E is exceedingly rare from random starts, or its velocity (-0.267,
identical to Ebar) makes it consistently mis-identified as Ebar.

This script tries: for each pair of verified gliders and a sweep of relative
positions, evolve long enough that the collision products separate, then run
the cluster tracker on the result. Any cluster moving at velocity matching E
and verifying against (T=15, D=-4) is saved.
"""

import sys

from core.ether import SPATIAL_PERIOD, ether_window
from core.gliders import ALL_VERIFIED
from core.rule110 import step
from scripts.track_gliders import (
    COOK, cluster, center, diff_cells, verify_window, delta_signature,
)


def place_glider(state, g, anchor):
    target_phase = g.left_phase
    here = anchor % SPATIAL_PERIOD
    if here != target_phase:
        anchor += (target_phase - here + SPATIAL_PERIOD) % SPATIAL_PERIOD
    for offset, b in g.delta:
        if 0 <= anchor + offset < len(state):
            state[anchor + offset] = b
    return state, anchor


def evolve_history(state, n_steps):
    history = [state]
    for _ in range(n_steps):
        state = step(state, boundary="ether")
        history.append(state)
    return history


def track_in_history(history, COOK_filter):
    tracks = []
    prev = []
    next_id = 0
    for t in range(len(history)):
        diffs = diff_cells(history[t], t)
        cs = cluster(diffs, gap=4)
        cs = [c for c in cs if c[-1] - c[0] <= 40]
        ids = []
        used = set()
        for cur in cs:
            cc = center(cur)
            best = None; bd = 1e9
            for i, (pid, pc) in enumerate(prev):
                if i in used: continue
                d = abs(center(pc) - cc)
                if d < 8 and d < bd:
                    best = i; bd = d
            if best is None:
                cid = next_id; next_id += 1
                tracks.append({"id": cid, "trajectory": [(t, cc, cur[0], cur[-1])]})
            else:
                cid = prev[best][0]; used.add(best)
                for tr in tracks:
                    if tr["id"] == cid:
                        tr["trajectory"].append((t, cc, cur[0], cur[-1]))
                        break
            ids.append((cid, cur))
        prev = ids

    found = {}
    for tr in tracks:
        traj = tr["trajectory"]
        if len(traj) < 25:
            continue
        t0, c0, _, _ = traj[0]
        t1, c1, _, _ = traj[-1]
        if t1 - t0 < 20:
            continue
        v = (c1 - c0) / (t1 - t0)
        for label, T, D in COOK_filter:
            target_v = D / T
            if abs(v - target_v) > 0.05:
                continue
            for ti in range(len(traj) // 4, len(traj) - 5, max(1, len(traj) // 5)):
                tm, cm, lm, rm = traj[ti]
                for halo in (3, 6, 10):
                    left = max(0, lm - halo)
                    right = min(len(history[0]), rm + halo + 1)
                    cap = history[tm][left:right]
                    phase = verify_window(cap, left, tm, T, D, n_periods=4)
                    if phase is None:
                        continue
                    sig = delta_signature(cap, left, tm)
                    if label in found and len(found[label]["sig"]) <= len(sig):
                        break
                    found[label] = {
                        "T": T, "D": D, "sig": sig, "cap": cap, "phase": phase, "tm": tm, "left": left,
                    }
                    break
                else:
                    continue
                break
            break
    return found


def main():
    e_target = [("E", 15, -4)]
    width = SPATIAL_PERIOD * 100
    catalog = {}

    pairs = [(g1, g2) for g1 in ALL_VERIFIED for g2 in ALL_VERIFIED]
    offsets = range(20, 140, 4)

    for g1, g2 in pairs:
        for d in offsets:
            state = list(ether_window(0, width))
            state, a1 = place_glider(state, g1, width // 3)
            state, a2 = place_glider(state, g2, width // 3 + d)
            state = tuple(state)
            history = evolve_history(state, 300)
            found = track_in_history(history, e_target)
            if "E" in found:
                info = found["E"]
                existing = catalog.get("E")
                if existing is None or len(info["sig"]) < len(existing["sig"]):
                    catalog["E"] = info
                    print(f"  E found: {g1.name}+{g2.name} offset={d} span={len(info['sig'])}")

    if "E" in catalog:
        info = catalog["E"]
        cells = ",".join(f"{o:+d}={b}" for o, b in info["sig"])
        print(f"\nE: {len(info['sig'])} cells; phase={info['phase']}")
        print(f"  delta: {cells}")
        print(f"  window: {''.join(str(b) for b in info['cap'])}")
    else:
        print("\nE not found via any 2-glider collision sweep")


if __name__ == "__main__":
    main()
