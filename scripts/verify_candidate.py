"""Take a candidate (left_phase, delta_cells, T, D) and verify whether it
behaves as a glider when placed in clean ether (no other activity nearby)."""

import sys

from core.ether import SPATIAL_PERIOD, ether_window
from core.rule110 import step


def verify(left_phase, delta, T, D, n_periods=4, state_periods=20):
    width = SPATIAL_PERIOD * state_periods
    anchor = SPATIAL_PERIOD * (state_periods // 2) + left_phase
    state = list(ether_window(0, width))
    for offset, b in delta:
        state[anchor + offset] = b
    state = tuple(state)

    print(f"  left_phase={left_phase}, anchor={anchor}, anchor%14={anchor % 14}")
    print(f"  delta: {delta}")

    s = state
    for k in range(1, n_periods + 1):
        for _ in range(T):
            s = step(s, boundary="ether")
        margin = k * T
        safe = slice(margin, width - margin)
        expected_at_anchor_offset = k * D
        try:
            for offset, b in delta:
                pos = anchor + offset + k * D
                if not (safe.start <= pos < safe.stop):
                    print(f"  k={k}: position {pos} out of safe interior")
                    return False
                if s[pos] != b:
                    print(f"  k={k}: shifted cell at {pos} = {s[pos]}, expected {b}  (NOT a glider)")
                    return False
            ether_ok = True
            for q in range(safe.start, safe.stop):
                in_glider = any(q == anchor + offset + k * D for offset, _ in delta)
                if in_glider:
                    continue
                expected = ether_window(4 * k * T + q, 1)[0]
                if s[q] != expected:
                    ether_ok = False
                    break
            print(f"  k={k}: shifted-cell check OK, ether-elsewhere OK={ether_ok}")
        except IndexError:
            return False
    return True


def main():
    candidates = [
        ("A",   3,  3, +2, ((0, 0), (2, 1), (3, 1))),
        ("B",   9,  4, -2, ((0, 1), (1, 1), (5, 0))),
        ("C",   9,  7,  0, ((0, 1), (1, 1), (5, 0))),
        ("D",   9, 10, +2, ((0, 1), (4, 1), (5, 0))),
        ("E",  10, 15, -4, ((0, 1), (4, 0), (5, 0))),
        ("Eb",  2, 30, -8, ((0, 0), (4, 1), (6, 0))),
    ]
    for label, phase, T, D, delta in candidates:
        print(f"\n=== {label} candidate: T={T}, D={D} ===")
        ok = verify(phase, delta, T, D)
        print(f"  verdict: {'GLIDER' if ok else 'not a glider in isolation'}")


if __name__ == "__main__":
    main()
