"""Constrained exhaustive search for E glider at width 19.

E1 has natural width 19 (Cook §3.1). At width 19 the unconstrained bitmask
sweep is 14*2^19 ≈ 7M patterns, too slow. Other gliders' minimal delta
cardinality is 25-70% of extent (3/4, 10/16, 4/11, 8/11, 7/14). At width 19
that suggests 5-13 cells of delta. We sweep delta-from-ether patterns with
constrained popcount and use the same strict ether-halo verification used
for shorter widths.

Run as:
    python -m scripts.exhaustive_e_search_constrained <width> <min_pop> <max_pop>
"""

import itertools
import sys
import time

from core.ether import SPATIAL_PERIOD, ether_cell, ether_window
from core.rule110 import step


T = 15
D = -4


def evolve_steps(state, n):
    for _ in range(n):
        state = step(state, boundary="ether")
    return state


def check_pattern(delta, left_phase, width, ambient_width=600, halo=20):
    anchor = SPATIAL_PERIOD * (ambient_width // (2 * SPATIAL_PERIOD)) + left_phase
    s = list(ether_window(0, ambient_width))
    for j, b in enumerate(delta):
        s[anchor + j] = b
    s = tuple(s)
    for k in range(1, 4):
        s = evolve_steps(s, T)
        moved = anchor + k * D
        shift = 4 * k * T
        for j in range(width):
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
        for j in range(width, width + halo):
            pos = moved + j
            if not (0 <= pos < ambient_width):
                continue
            if s[pos] != ether_cell(pos + shift):
                return False
    return True


def main():
    width = int(sys.argv[1]) if len(sys.argv) > 1 else 19
    min_pop = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    max_pop = int(sys.argv[3]) if len(sys.argv) > 3 else 13

    start = time.time()
    total = 0
    hits = []

    for phase in range(SPATIAL_PERIOD):
        ref = [ether_cell(phase + i) for i in range(width)]
        for pop in range(min_pop, max_pop + 1):
            for diff_positions in itertools.combinations(range(width), pop):
                delta = list(ref)
                for p in diff_positions:
                    delta[p] = 1 - delta[p]
                if delta[0] == ref[0] and delta[-1] == ref[-1]:
                    continue
                total += 1
                if total % 200_000 == 0:
                    el = time.time() - start
                    print(f"  scanned {total:,}  phase={phase} pop={pop}  elapsed {el:.1f}s", flush=True)
                if check_pattern(delta, phase, width):
                    hits.append((phase, list(delta), tuple(diff_positions)))
                    print(f"  HIT phase={phase} pop={pop} diffs={diff_positions}", flush=True)
                    print(f"    delta={delta}", flush=True)
                    if len(hits) >= 30:
                        break
            if len(hits) >= 30:
                break
        if len(hits) >= 30:
            break

    el = time.time() - start
    print(f"\nDone in {el:.1f}s; candidates checked = {total:,}; hits = {len(hits)}")
    for phase, delta, diffs in hits:
        print(f"  phase={phase} diffs={diffs} delta={delta}")


if __name__ == "__main__":
    main()
