"""Empirically locate the Cook §3.2.4 C2 × Ebar crossing collision.

For each pair (C2-variant, Ebar-variant) × placement-gap, simulate
the collision and detect 'crossing' liberally: C2 survives at its
original anchor AND there is non-ether activity at the expected Ebar
position after the crossing.

Cook §4.2: "Each Ebar must be α3 from the first C2 it crosses." α3 is
discrete — likely a specific cell separation we identify empirically.

We sweep all combinations and record gaps where C2 survives.
"""

import sys
import time

from core.cook_gliders import CookGlider, place_cook_glider, fresh_ether_state
from core.ether import SPATIAL_PERIOD, ether_cell
from core.rule110 import step


# Discovered variants from scripts.find_cook_variants (period, displacement, width)
C2_VARIANTS = [
    CookGlider("C2_L2_v1", 7, 0, 2, 3, (1, 0, 0, 0, 0, 0), "L=2"),
    CookGlider("C2_L3_v1", 7, 0, 3, 3, (0, 0, 0, 0, 0, 1), "L=3 v1"),
    CookGlider("C2_L3_v2", 7, 0, 3, 3, (1, 1, 0, 1, 1, 0), "L=3 v2"),
    CookGlider("C2_L4_v1", 7, 0, 4, 3, (1, 0, 1, 0, 0, 0), "L=4 v1"),
    CookGlider("C2_L4_v2", 7, 0, 4, 3, (1, 0, 1, 1, 0, 1), "L=4 v2"),
    CookGlider("C2_L5_v1", 7, 0, 5, 3, (0, 0, 0, 1, 1, 1), "L=5 v1"),
    CookGlider("C2_L5_v2", 7, 0, 5, 3, (0, 1, 0, 0, 0, 0), "L=5 v2"),
    CookGlider("C2_L5_v3", 7, 0, 5, 3, (0, 1, 1, 0, 1, 0), "L=5 v3"),
    CookGlider("C2_L7_v1", 7, 0, 7, 3, (0, 1, 1, 1, 1, 1), "L=7 v1"),
]

EBAR_VARIANTS = [
    CookGlider("Eb_L4_v1", 30, -8, 4, 7, (1, 1, 0, 0, 1, 1, 1), "L=4"),
]


def survives_collision(c2v, ebv, gap, post_steps, width_units=200):
    width = SPATIAL_PERIOD * width_units
    state = fresh_ether_state(width, phase=0)
    anchor = width // 3
    c2_anchor, cw = place_cook_glider(state, anchor, c2v, cumulative_width=0)
    eb_anchor, cw = place_cook_glider(state, c2_anchor + c2v.extent + gap, ebv, cumulative_width=cw)
    s = tuple(state)
    for _ in range(post_steps):
        s = step(s, boundary="ether")

    c2_present = all(s[c2_anchor + j] == c2v.delta[j] for j in range(c2v.extent))
    if not c2_present:
        return None

    activity_left = 0
    for p in range(max(0, c2_anchor - 200), c2_anchor - 20):
        if s[p] != ether_cell(p + 4 * post_steps):
            activity_left += 1
    return activity_left


def main():
    post = int(sys.argv[1]) if len(sys.argv) > 1 else 1400  # 200 C2 periods, ~47 Ebar periods
    max_gap = int(sys.argv[2]) if len(sys.argv) > 2 else 200

    start = time.time()
    hits = []
    total = 0

    for c2v in C2_VARIANTS:
        for ebv in EBAR_VARIANTS:
            for gap in range(0, max_gap):
                total += 1
                activity = survives_collision(c2v, ebv, gap, post)
                if activity is not None and activity > 0:
                    sep_approx = c2v.extent + gap
                    hits.append((c2v.name, ebv.name, gap, sep_approx, activity))
                    print(f"  CANDIDATE: {c2v.name} × {ebv.name}  gap={gap}  left_activity={activity}",
                          flush=True)
                if total % 100 == 0:
                    el = time.time() - start
                    print(f"  scanned {total} configurations, elapsed {el:.1f}s", flush=True)

    el = time.time() - start
    print(f"\nDone in {el:.1f}s; total configurations checked = {total:,}; candidate crossings = {len(hits)}")
    if hits:
        print("\nCandidate (variant, gap, left_activity):")
        for c2n, ebn, gap, sep, act in hits[:40]:
            print(f"  {c2n} × {ebn}  gap={gap} sep~{sep}  activity_count={act}")


if __name__ == "__main__":
    main()
