"""Empirically locate the Cook §3.2.4 C2 × Ebar crossing collision.

For each pair (C2-variant, Ebar-variant) × placement-gap, simulate
the collision and detect 'crossing' using structural detectors from
`compiler.glider_detect`:

  - C2 still stationary at its original anchor (period-7 self-equality
    AND non-ether), accounting for C2's local left_phase shift after
    Ebar crosses to its left.
  - A leftward-moving period-30 displacement-(-8) glider somewhere in
    the safe central region to the left of the C2.

Both conditions must hold simultaneously for a configuration to count
as a crossing. Bit-pattern matching against C2.delta or Ebar.delta is
not used — see ADR 0005 for why.
"""

import sys
import time

from compiler.glider_detect import is_stationary_glider, find_displaced_glider
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


def crossing_signature(c2v, ebv, gap, post_steps, width_units=400):
    """Run the C2-then-Ebar simulation for `post_steps` and return
    (c2_stationary, ebar_displaced_anchor) or None if either detector
    fails.

    c2_stationary: True iff cells at c2_anchor are non-ether and stable
      over one C2 period.
    ebar_displaced_anchor: position where the structural displacement
      detector found an Ebar-class glider in the safe left region, or
      None.
    """
    width = SPATIAL_PERIOD * width_units
    state = fresh_ether_state(width, phase=0)
    anchor = width // 3
    c2_anchor, cw = place_cook_glider(state, anchor, c2v, cumulative_width=0)
    eb_anchor, cw = place_cook_glider(state, c2_anchor + c2v.extent + gap, ebv, cumulative_width=cw)
    s_t = tuple(state)
    for _ in range(post_steps):
        s_t = step(s_t, boundary="ether")
    s_t_plus_c2 = s_t
    for _ in range(c2v.period_t):
        s_t_plus_c2 = step(s_t_plus_c2, boundary="ether")
    s_t_plus_eb = s_t
    for _ in range(ebv.period_t):
        s_t_plus_eb = step(s_t_plus_eb, boundary="ether")

    c2_ok = is_stationary_glider(s_t, s_t_plus_c2, c2_anchor, c2v.extent, post_steps)
    if not c2_ok:
        return None

    safe_lo = post_steps + 50
    safe_hi = c2_anchor - 20
    eb_found = find_displaced_glider(
        s_t, s_t_plus_eb, displacement=ebv.displacement,
        time_t=post_steps, extent=ebv.extent,
        search_left=safe_lo, search_right=safe_hi,
    )
    return (c2_ok, eb_found)


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
                sig = crossing_signature(c2v, ebv, gap, post)
                if sig is not None:
                    c2_ok, eb_found = sig
                    if c2_ok and eb_found is not None:
                        hits.append((c2v.name, ebv.name, gap, c2v.extent + gap, eb_found))
                        print(f"  CROSSING: {c2v.name} × {ebv.name}  gap={gap}  ebar_at={eb_found}",
                              flush=True)
                if total % 100 == 0:
                    el = time.time() - start
                    print(f"  scanned {total} configurations, elapsed {el:.1f}s", flush=True)

    el = time.time() - start
    print(f"\nDone in {el:.1f}s; total configurations checked = {total:,}; verified crossings = {len(hits)}")
    if hits:
        print("\nCrossings (variant pair, gap, post-collision Ebar anchor):")
        for c2n, ebn, gap, sep, eb_at in hits[:40]:
            print(f"  {c2n} × {ebn}  gap={gap} sep~{sep}  ebar_at={eb_at}")


if __name__ == "__main__":
    main()
