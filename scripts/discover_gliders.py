"""Search Rule 110 for Cook's gliders by their period and displacement.

Cook (2004) Figure 5 documents each glider's (period_t, displacement) pair:
    C-class: (7, 0)    stationary  (3 variants C1, C2, C3 at different phases)
    A:       (3, +2)   fast right-mover
    B:       (4, -2)   fast left-mover
    D-class: (10, +2)  medium right-mover
    Ebar:    (30, -8)  long-period heavy left-mover

This script searches binary deltas from the ether background for patterns that
reproduce their starting shape, shifted by `displacement`, after `period_t`
Rule 110 steps. Output: each unique glider as the list of cell positions where
its representation differs from the background ether, mod 14.
"""

from itertools import product

from core.ether import SPATIAL_PERIOD, ether_window
from core.rule110 import step


def safe_interior(width: int, period_t: int, displacement: int) -> slice:
    left = period_t + max(0, displacement)
    right = width - period_t + min(0, displacement)
    return slice(left, right)


def is_glider(
    state: tuple[int, ...], period_t: int, displacement: int
) -> bool:
    evolved = state
    for _ in range(period_t):
        evolved = step(evolved, boundary="ether")
    safe = safe_interior(len(state), period_t, displacement)
    for q in range(safe.start, safe.stop):
        if evolved[q] != state[q - displacement]:
            return False
    return True


def delta_signature(
    state: tuple[int, ...], anchor: int
) -> tuple[tuple[int, int], ...]:
    n = len(state)
    diffs = []
    for i in range(n):
        ether_bit = ether_window(0, n)[i]
        if state[i] != ether_bit:
            diffs.append((i - anchor, state[i]))
    if not diffs:
        return ()
    first_offset = diffs[0][0]
    return tuple((o - first_offset, b) for o, b in diffs)


def search(
    period_t: int,
    displacement: int,
    max_width: int = 12,
    state_width_periods: int = 14,
    phases: tuple[int, ...] = (0,),
) -> list[tuple[tuple[tuple[int, int], ...], int]]:
    state_width = SPATIAL_PERIOD * state_width_periods
    anchor_base = SPATIAL_PERIOD * (state_width_periods // 2)
    base = list(ether_window(0, state_width))

    found: dict[tuple[tuple[int, int], ...], int] = {}
    for phase in phases:
        anchor = anchor_base + phase
        for w in range(1, max_width + 1):
            for bits in product((0, 1), repeat=w):
                state = list(base)
                for k, b in enumerate(bits):
                    state[anchor + k] = b
                state = tuple(state)
                if state == tuple(base):
                    continue
                if not is_glider(state, period_t, displacement):
                    continue
                sig = delta_signature(state, anchor)
                if sig in found:
                    found[sig] = min(found[sig], w)
                else:
                    found[sig] = w

    return sorted(found.items(), key=lambda kv: (len(kv[0]), kv[1]))


def visualize_delta(sig: tuple[tuple[int, int], ...]) -> str:
    if not sig:
        return "(empty)"
    span = max(o for o, _ in sig) + 1
    glyphs = ["."] * span
    for o, b in sig:
        glyphs[o] = "1" if b else "0"
    return "".join(glyphs)


def main() -> None:
    all_phases = tuple(range(SPATIAL_PERIOD))
    targets = [
        ("C-class stationary", 7, 0, 10, all_phases),
        ("A right-mover",      3, 2, 8, all_phases),
        ("B (4,-2)",           4, -2, 14, all_phases),
        ("D (10,+2)",          10, 2, 12, all_phases),
        ("E (15,-4)",          15, -4, 18, all_phases),
        ("Ebar (30,-8)",       30, -8, 14, all_phases),
    ]
    for label, t, d, max_w, phases in targets:
        print(f"\n=== {label}: period {t}, displacement {d} ===")
        results = search(t, d, max_width=max_w, phases=phases)
        if not results:
            print(f"  none found at max_width={max_w}")
            continue
        for sig, _ in results[:10]:
            cells = ",".join(f"{o:+d}={b}" for o, b in sig)
            print(f"  delta_vs_ether: {visualize_delta(sig):<18s} cells: {cells}")


if __name__ == "__main__":
    main()
