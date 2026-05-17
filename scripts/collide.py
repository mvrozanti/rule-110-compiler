"""Collision sandbox: place two verified gliders at chosen positions in an
ether-bedded state, evolve, and print the spacetime as ASCII.

Cook's universality construction depends on a small set of designed glider
collisions. Their inputs and outputs are documented in Cook 2004 §3.3-§3.5
but exact relative positions matter and have to be empirically tuned. This
script is the iteration loop for that tuning.

Usage:
  python -m scripts.collide A 0 Ebar 30 --steps 60
  python -m scripts.collide C 0 Ebar 20 --steps 80 --scan
  python -m scripts.collide A 0 A 14 --steps 50

Output: spacetime diagram, 1 cell per character.  '.' = ether-background bit
that matches ether at that time; '0' = bit 0 deviating from ether (should
be 1 there); '1' = bit 1 deviating; '#' = exact background bit value (legacy).
"""

import argparse
import sys

from core.ether import SPATIAL_PERIOD, ether_window
from core.gliders import ALL_VERIFIED, Glider
from core.rule110 import step


BY_NAME = {g.name: g for g in ALL_VERIFIED}


def place(glider: Glider, anchor: int, state: list[int]) -> list[int]:
    if anchor % SPATIAL_PERIOD != glider.left_phase:
        anchor += (glider.left_phase - anchor) % SPATIAL_PERIOD
    for offset, b in glider.delta:
        if 0 <= anchor + offset < len(state):
            state[anchor + offset] = b
    return state


def render(state: tuple[int, ...], t: int, view_left: int, view_right: int) -> str:
    chars = []
    ref = ether_window(t * 4, len(state))
    for q in range(view_left, view_right):
        if q < 0 or q >= len(state):
            chars.append(" ")
            continue
        if state[q] == ref[q]:
            chars.append("." if state[q] == 0 else ":")
        else:
            chars.append("0" if state[q] == 0 else "1")
    return "".join(chars)


def simulate(name_a: str, off_a: int, name_b: str, off_b: int, steps: int, scan: bool):
    if name_a not in BY_NAME:
        sys.exit(f"unknown glider {name_a!r}; available: {sorted(BY_NAME)}")
    if name_b not in BY_NAME:
        sys.exit(f"unknown glider {name_b!r}; available: {sorted(BY_NAME)}")

    ga, gb = BY_NAME[name_a], BY_NAME[name_b]
    width = SPATIAL_PERIOD * 20
    base = SPATIAL_PERIOD * 6
    state = list(ether_window(0, width))
    state = place(ga, base + off_a, state)
    state = place(gb, base + off_b, state)
    state = tuple(state)

    view_left = base - 10
    view_right = base + max(off_a, off_b) + 60

    s = state
    for t in range(steps + 1):
        line = render(s, t, view_left, view_right)
        prefix = f"t={t:>3d} "
        print(prefix + line)
        if t < steps:
            s = step(s, boundary="ether")

    if scan:
        for shift in range(-10, 11):
            s = list(ether_window(0, width))
            s = place(ga, base + off_a, s)
            s = place(gb, base + off_b + shift, s)
            s = tuple(s)
            initial_diff = sum(1 for q in range(width) if s[q] != ether_window(0, width)[q])
            for _ in range(steps):
                s = step(s, boundary="ether")
            final_diff = sum(1 for q in range(width) if s[q] != ether_window(steps * 4, width)[q])
            print(f"  shift={shift:+3d}: initial_diffs={initial_diff:>3d}  final_diffs={final_diff:>3d}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("glider_a")
    p.add_argument("offset_a", type=int)
    p.add_argument("glider_b")
    p.add_argument("offset_b", type=int)
    p.add_argument("--steps", type=int, default=60)
    p.add_argument("--scan", action="store_true",
                   help="sweep relative offset to see how the collision changes")
    args = p.parse_args()
    simulate(args.glider_a, args.offset_a, args.glider_b, args.offset_b,
             args.steps, args.scan)


if __name__ == "__main__":
    main()
