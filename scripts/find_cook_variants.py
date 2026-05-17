"""Search for Cook-style width-W gliders, not just width-0 ones.

ADR 0002 records the discovery that our verified gliders all measure
width 0 mod 14, while Cook's table assigns each glider a specific
non-zero width (A=6, B=8, C1=9, C2=3, C3=11, etc.). Hypothesis: my
strict-halo verifier in `scripts/exhaustive_e_search.py` and the
minimal-delta extractor in `scripts/track_gliders.py` both assume the
ether around the glider is standard ether on both sides. A Cook width-W
glider has ether at phase L on its left and phase L+W on its right;
checking either side against standard ether would reject it.

This script searches for period-(T, D) patterns at each ether-phase
combination (L_left, L_left + W) for W in 0..13. A hit is a delta whose
left halo matches phase-L_left ether and whose right halo matches
phase-(L_left + W) ether, with the delta itself reappearing at offset D
after T steps.

Run as:
    python -m scripts.find_cook_variants <target-name> <T> <D> <max-extent>
e.g.
    python -m scripts.find_cook_variants A 3 2 8
"""

import itertools
import sys
import time

from core.ether import SPATIAL_PERIOD, ether_cell, ether_window
from core.rule110 import step


def evolve_steps(state, n):
    for _ in range(n):
        state = step(state, boundary="ether")
    return state


def check_width_w_glider(delta, left_phase, extent, width_w, T, D,
                         ambient_width=600, halo=20):
    """Check whether `delta` placed at left_phase with right ether at
    phase (left_phase + width_w + extent) propagates with (T, D).

    The right halo must match ether shifted by width_w; left halo must
    match standard ether at left phase. Surrounding the placement with
    proper ether is the trick: cells beyond the glider's extent on the
    right are set to (phase + width_w) ether bits.
    """
    anchor = SPATIAL_PERIOD * (ambient_width // (2 * SPATIAL_PERIOD)) + left_phase
    s = [ether_cell(i) for i in range(ambient_width)]
    for j in range(extent):
        pos = anchor + j
        s[pos] = delta[j]
    for j in range(extent, halo + extent):
        pos = anchor + j
        if 0 <= pos < ambient_width:
            s[pos] = ether_cell(pos + width_w)

    s = tuple(s)
    for k in range(1, 4):
        s = evolve_steps(s, T)
        moved = anchor + k * D
        shift = 4 * k * T
        for j in range(extent):
            pos = moved + j
            if not (0 <= pos < ambient_width):
                return False
            if s[pos] != delta[j]:
                return False
        for j in range(-halo, 0):
            pos = moved + j
            if not (0 <= pos < ambient_width):
                continue
            if s[pos] != ether_cell(pos + shift):
                return False
        for j in range(extent, extent + halo):
            pos = moved + j
            if not (0 <= pos < ambient_width):
                continue
            expected = ether_cell(pos + width_w + shift)
            if s[pos] != expected:
                return False
    return True


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "A"
    T = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    D = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    max_extent = int(sys.argv[4]) if len(sys.argv) > 4 else 8

    start = time.time()
    total = 0
    hits = []

    for extent in range(2, max_extent + 1):
        for left_phase in range(SPATIAL_PERIOD):
            for width_w in range(SPATIAL_PERIOD):
                for bits in itertools.product((0, 1), repeat=extent):
                    delta = list(bits)
                    total += 1
                    if total % 200_000 == 0:
                        el = time.time() - start
                        print(f"  scanned {total:,}  extent={extent} phase={left_phase} W={width_w}  elapsed {el:.1f}s",
                              flush=True)
                    if check_width_w_glider(delta, left_phase, extent, width_w, T, D):
                        hits.append((extent, left_phase, width_w, tuple(delta)))
                        print(f"  HIT extent={extent} L={left_phase} W={width_w} delta={delta}",
                              flush=True)
                        if len(hits) >= 200:
                            break
                if len(hits) >= 200:
                    break
            if len(hits) >= 200:
                break
        if len(hits) >= 200:
            break

    el = time.time() - start
    print(f"\n[{name}] candidates checked = {total:,}; hits = {len(hits)} in {el:.1f}s")
    seen_w = {}
    for ext, lp, w, d in hits:
        if w not in seen_w:
            seen_w[w] = (ext, lp, d)
    print(f"\nDistinct widths found: {sorted(seen_w.keys())}")
    for w in sorted(seen_w.keys()):
        ext, lp, d = seen_w[w]
        print(f"  W={w} L={lp} extent={ext} delta={d}")


if __name__ == "__main__":
    main()
