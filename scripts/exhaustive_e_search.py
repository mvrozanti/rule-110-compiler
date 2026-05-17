"""Exhaustive search for E glider over fixed-width delta patterns.

E has period (15, -4) per Cook Figure 5, with natural extent ~19 cells
(width = 11 + 8n; E1 has n=1 giving width 19).

Strategy: for each ether left-phase 0..13 and each non-empty delta pattern
of width W cells over phase, place the delta on clean ether, evolve T=15
steps, and check the same delta reappears at offset -4. Verify two more
periods (45 steps total) to weed out false positives.

W is parameterised; larger W explores more patterns but blows up search.
W up to ~22 is tractable as a bitmask sweep when paired with a 'must be
nonzero in the leftmost AND rightmost cells' pruning rule (eliminates
shorter patterns that fit inside a wider window).
"""

import sys
import time

from core.ether import SPATIAL_PERIOD, ether_window, ether_cell
from core.rule110 import step


T = 15
D = -4
WIDTH_DEFAULT = 20


def evolve_steps(state, n):
    for _ in range(n):
        state = step(state, boundary="ether")
    return state


def check_pattern(delta, left_phase, width, ambient_width=600, halo=20):
    """Return True if delta at left_phase reappears at offset D after T steps,
    AND ether around the moved delta is intact, for 3 successive periods.

    Halo cells on each side of the delta must match ether after each period;
    this rejects 'patterns whose middle bits happen to repeat' that leak chaos
    into the surrounding ether (not a true glider)."""
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


def pattern_from_mask(mask, width, left_phase):
    bits = [(mask >> i) & 1 for i in range(width)]
    ref = [ether_cell(left_phase + i) for i in range(width)]
    delta = []
    for i in range(width):
        delta.append(bits[i])
    return delta, any(delta[i] != ref[i] for i in range(width))


def main():
    width = int(sys.argv[1]) if len(sys.argv) > 1 else WIDTH_DEFAULT
    max_phases = int(sys.argv[2]) if len(sys.argv) > 2 else SPATIAL_PERIOD

    start = time.time()
    total = 0
    hits = []

    for phase in range(max_phases):
        ref = [ether_cell(phase + i) for i in range(width)]
        ref_mask = sum(b << i for i, b in enumerate(ref))
        for mask in range(0, 1 << width):
            if mask == ref_mask:
                continue
            delta = [(mask >> i) & 1 for i in range(width)]
            if delta[0] == ref[0] and delta[-1] == ref[-1]:
                continue
            total += 1
            if total % 1_000_000 == 0:
                el = time.time() - start
                print(f"  scanned {total:,} / phase {phase}, elapsed {el:.1f}s", flush=True)
            if check_pattern(delta, phase, width):
                hits.append((phase, delta, mask))
                print(f"  HIT phase={phase} width={width} mask={mask:0{width}b} delta={delta}", flush=True)
                if len(hits) >= 20:
                    break
        if len(hits) >= 20:
            break

    el = time.time() - start
    print(f"\nDone in {el:.1f}s; total candidates checked = {total:,}; hits = {len(hits)}")
    for phase, delta, mask in hits:
        print(f"  phase={phase} mask={mask:0{width}b}")
        print(f"  delta={delta}")


if __name__ == "__main__":
    main()
