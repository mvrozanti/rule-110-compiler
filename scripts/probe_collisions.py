"""Sweep collisions between verified gliders and classify outcomes.

For each ordered pair (G1, G2) and a sweep of relative ether-anchored
positions, place G1 and G2 on a wide ether strip, evolve long enough that
collision products separate, and classify the post-collision content as:
  - 'identical': same two gliders present (crossing/pass-through)
  - 'annihilate': both gliders gone
  - 'mutate': different glider set survives
  - 'chaotic': region didn't settle to identifiable ether-bedded gliders

This is the empirical seed for the collision atlas. We do not claim parity
with Cook's atlas; we record what Rule 110 actually does for our verified
glider patterns.
"""

import sys

from core.ether import SPATIAL_PERIOD, ether_cell, ether_window
from core.gliders import A, B, C, D, Ebar, Glider
from core.rule110 import step


def place_glider(state, gl: Glider, anchor: int):
    here = anchor % SPATIAL_PERIOD
    delta_phase = (gl.left_phase - here + SPATIAL_PERIOD) % SPATIAL_PERIOD
    anchor += delta_phase
    for off, b in gl.delta:
        if 0 <= anchor + off < len(state):
            state[anchor + off] = b
    return anchor


def is_ether(s, time, lo, hi):
    for pos in range(max(0, lo), min(len(s), hi)):
        if s[pos] != ether_cell(pos + 4 * time):
            return False
    return True


def find_diff_clusters(s, time, gap=6):
    diffs = [i for i in range(len(s)) if s[i] != ether_cell(i + 4 * time)]
    if not diffs:
        return []
    groups = [[diffs[0]]]
    for q in diffs[1:]:
        if q - groups[-1][-1] <= gap:
            groups[-1].append(q)
        else:
            groups.append([q])
    return groups


def signature_of_cluster(s, time, cluster):
    lo, hi = cluster[0], cluster[-1]
    bits = tuple(s[lo:hi + 1])
    ref = tuple(ether_cell(p + 4 * time) for p in range(lo, hi + 1))
    delta = tuple((p - lo, bits[p - lo]) for p in range(lo, hi + 1) if bits[p - lo] != ref[p - lo])
    return delta


def classify(g1: Glider, g2: Glider, offset: int, post_steps: int = 420, gap_between_g: int = 80):
    width = SPATIAL_PERIOD * 200
    g1_anchor = width // 2
    g2_anchor = g1_anchor + gap_between_g + offset
    s = list(ether_window(0, width))
    a1 = place_glider(s, g1, g1_anchor)
    a2 = place_glider(s, g2, g2_anchor)
    state = tuple(s)
    for t in range(1, post_steps + 1):
        state = step(state, boundary="ether")

    safe_lo = post_steps + 50
    safe_hi = width - post_steps - 50
    clusters = [c for c in find_diff_clusters(state, post_steps) if safe_lo <= c[0] and c[-1] <= safe_hi]
    if not clusters:
        return "annihilate", []
    sigs = [signature_of_cluster(state, post_steps, c) for c in clusters]
    return "survives", sigs


def matches_known(sig):
    for gl in (A, B, C, D, Ebar):
        if sig == gl.delta:
            return gl.name
    return None


def main():
    pairs = [(A, A), (A, B), (A, C), (A, D), (A, Ebar),
             (B, C), (B, D), (B, Ebar),
             (C, C), (C, D), (C, Ebar),
             (D, D), (D, Ebar),
             (Ebar, Ebar)]

    offsets = list(range(0, 60, 1))
    for g1, g2 in pairs:
        annihilate_count = 0
        survives_set = set()
        examples = []
        for off in offsets:
            outcome, sigs = classify(g1, g2, off)
            if outcome == "annihilate":
                annihilate_count += 1
            else:
                tags = tuple(matches_known(s) for s in sigs)
                survives_set.add(tags)
                if len(examples) < 3 and tags != (None,) * len(tags):
                    examples.append((off, tags))
        print(f"{g1.name:>4s} x {g2.name:<4s}: "
              f"annihilate@{annihilate_count}/{len(offsets)}  "
              f"survivors={sorted({t for ts in survives_set for t in ts if t})}")
        for off, tags in examples[:3]:
            print(f"      off={off}: {tags}")


if __name__ == "__main__":
    main()
