"""Detailed offset sweep of the C x Ebar collision.

Cook §3.2.4 documents four possible C2 x Ē collisions: pass-through
('crossing'), absorption, annihilation, and 'big' reaction yielding C3.
This script sweeps the relative offset and labels each outcome.

We only have one C variant in core/gliders.py (period 7, width 11). It may
correspond to C2 (width 3 by Cook's table), C1 (width 9), or C3 (width 11).
Empirically we treat it as a single representative and record collision
outcomes for it.
"""

from core.ether import SPATIAL_PERIOD, ether_window, ether_cell
from core.gliders import C, Ebar
from core.rule110 import step
from scripts.probe_collisions import (
    place_glider, find_diff_clusters, signature_of_cluster, matches_known,
)


def classify_outcome(sigs):
    names = sorted(matches_known(s) or "?" for s in sigs)
    if names == []:
        return "empty"
    return "+".join(names)


def main():
    offsets = list(range(0, 200, 1))
    width = SPATIAL_PERIOD * 200
    g1_anchor = width // 2
    gap = 100
    post_steps = 420

    rows = []
    for off in offsets:
        g2_anchor = g1_anchor + gap + off
        s = list(ether_window(0, width))
        place_glider(s, C, g1_anchor)
        place_glider(s, Ebar, g2_anchor)
        state = tuple(s)
        for _ in range(post_steps):
            state = step(state, boundary="ether")

        safe_lo = post_steps + 50
        safe_hi = width - post_steps - 50
        clusters = [c for c in find_diff_clusters(state, post_steps) if safe_lo <= c[0] and c[-1] <= safe_hi]
        sigs = [signature_of_cluster(state, post_steps, c) for c in clusters]
        outcome = classify_outcome(sigs)
        rows.append((off, outcome, len(sigs)))

    by_outcome: dict[str, list[int]] = {}
    for off, outcome, _ in rows:
        by_outcome.setdefault(outcome, []).append(off)
    for outcome, offs in sorted(by_outcome.items(), key=lambda kv: -len(kv[1])):
        print(f"{outcome:40s}  count={len(offs):>3d}  example_offsets={offs[:8]}")


if __name__ == "__main__":
    main()
