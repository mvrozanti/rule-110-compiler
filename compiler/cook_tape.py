"""Cook-faithful CTS tape encoding inside Rule 110.

Encodes a CTS tape as a sequence of Cook-faithful C2 gliders separated by
the empirically-calibrated `C2_SEP` cells (28 by default, the minimum
stable spacing). Each Y symbol places a C2; each N symbol leaves the
slot as Cook-shifted ether.

An optional 'scanner Ebar' can be placed to the right of the tape with
the verified crossing-phase gap (`EBAR_GAP`). When Rule 110 evolution
runs forward, the Ebar performs one verified C2 × Ebar crossing per Y
symbol it encounters, traversing the entire tape and emerging on the
left.

Each crossing is one elementary Rule 110 reaction inside the spacetime —
direct evidence of structured computation happening inside the
automaton, not in surrounding Python code.
"""

from dataclasses import dataclass

from core.cook_gliders import C2, Ebar, place_cook_glider, fresh_ether_state
from core.ether import SPATIAL_PERIOD


# Empirically calibrated by tests/test_alpha_beta.py and
# tests/test_multi_c2_traversal.py:
C2_SEP = 28              # min stable C2 × C2 cell spacing
EBAR_GAP = 22            # verified crossing-phase gap (Cook α3-ish)
TAPE_PAD_LEFT = 200      # ether room left of the tape for Ebar to emerge
TAPE_PAD_RIGHT = 200     # ether room right of the tape


@dataclass(frozen=True)
class CookTapeIC:
    initial: tuple[int, ...]
    c2_anchors: tuple[int, ...]    # cell positions of placed C2 gliders (Y slots only)
    slot_positions: tuple[int, ...]  # cell positions of every slot (Y or N)
    slot_kinds: tuple[str, ...]      # 'Y' or 'N' per slot, in the original tape order
    ebar_anchor: int | None         # Ebar position if scanner placed, else None


def encode_tape(tape: tuple[str, ...], with_scanner: bool = True,
                width: int | None = None, post_steps_for_padding: int = 2400) -> CookTapeIC:
    """Encode CTS tape as a Cook-faithful Rule 110 IC.

    Tape symbols Y place a C2 glider at the slot. N leave Cook-shifted
    ether at the slot. Slots are spaced C2_SEP cells apart. Optionally
    place an Ebar scanner to the right of the rightmost tape slot with
    EBAR_GAP separation (a verified crossing-phase gap).

    `width` defaults to enough cells to hold the tape, the scanner, and
    enough boundary-safe padding (`2 * post_steps_for_padding + 200`) so
    Rule 110 evolution to `post_steps_for_padding` steps does not let
    ether-boundary corruption reach the tape's safe central region.
    """
    n = len(tape)
    tape_extent = n * C2_SEP + TAPE_PAD_LEFT + TAPE_PAD_RIGHT
    if width is None:
        width = max(
            tape_extent + 2 * post_steps_for_padding + 200,
            SPATIAL_PERIOD * 100,
        )
        # round up to ether period
        if width % SPATIAL_PERIOD:
            width += SPATIAL_PERIOD - (width % SPATIAL_PERIOD)
    state = fresh_ether_state(width, phase=0)

    cw = 0
    tape_start = post_steps_for_padding + 200
    slot_positions: list[int] = []
    slot_kinds: list[str] = []
    c2_anchors: list[int] = []
    target = tape_start
    for sym in tape:
        if sym == "Y":
            a, cw = place_cook_glider(state, target, C2, cumulative_width=cw)
            slot_positions.append(a)
            c2_anchors.append(a)
            slot_kinds.append("Y")
            target = a + C2_SEP
        elif sym == "N":
            slot_positions.append(target)
            slot_kinds.append("N")
            target = target + C2_SEP
        else:
            raise ValueError(f"unsupported CTS symbol {sym!r}; expected Y or N")

    ebar_anchor = None
    if with_scanner:
        if c2_anchors:
            scanner_target = c2_anchors[-1] + C2.extent + EBAR_GAP
        else:
            scanner_target = tape_start + n * C2_SEP + EBAR_GAP
        ebar_anchor, cw = place_cook_glider(state, scanner_target, Ebar, cumulative_width=cw)

    return CookTapeIC(
        initial=tuple(state),
        c2_anchors=tuple(c2_anchors),
        slot_positions=tuple(slot_positions),
        slot_kinds=tuple(slot_kinds),
        ebar_anchor=ebar_anchor,
    )


def decode_tape(state_t, state_t_plus_c2_period, ic: CookTapeIC, time_t: int) -> tuple[str, ...]:
    """Read the CTS tape back from a Rule 110 state.

    For each slot, decode 'Y' if the cells at the slot host a C2-class
    glider (non-ether against the appropriate ether phase AND stable
    over one C2 period); else 'N'.

    The "appropriate ether phase" at slot i is determined by the
    cumulative Cook-width to the left of slot i. This depends on:

      1. How many earlier slots were Y (each adds C2.width = 3 to all
         slots after it).
      2. If a scanner Ebar was placed and has passed the slot by
         time_t (moved to its left), the Ebar adds Ebar.width = 7.

    We compute (2) from `ic.ebar_anchor` and `time_t`.
    """
    from core.ether import ether_cell
    from core.rule110 import step

    # Scanner contribution: if it has reached a position to the left of the
    # rightmost slot we're decoding, it's added its width to all slots to
    # the right of its current position. For simplicity, we assume it has
    # passed *all* slots if it's currently left of slot_positions[0].
    ebar_contrib = 0
    if ic.ebar_anchor is not None:
        ebar_pos_now = ic.ebar_anchor + time_t * Ebar.displacement // Ebar.period_t
        if ic.slot_positions and ebar_pos_now < ic.slot_positions[0]:
            ebar_contrib = Ebar.width

    # Sample C2 cells at all C2.period_t internal phases — at some phase the
    # cells of a real C2 must differ from ether (otherwise C2 would be
    # indistinguishable from ether everywhere in its cycle, contradiction).
    period_snapshots = [state_t]
    s = state_t
    for _ in range(C2.period_t):
        s = step(s, boundary="ether")
        period_snapshots.append(s)

    out: list[str] = []
    cum_w_before_slot = ebar_contrib
    for slot_pos in ic.slot_positions:
        # Stable over one C2 period:
        stable = period_snapshots[0] == period_snapshots[C2.period_t] or all(
            state_t[slot_pos + j] == state_t_plus_c2_period[slot_pos + j]
            for j in range(C2.extent)
        )
        # Check whether ANY snapshot in the cycle differs from ether at the
        # same internal time-shifted phase (a C2 differs from local ether at
        # at least one of its 7 internal phases; pure ether matches at all).
        differs_at_some_phase = False
        for k in range(C2.period_t):
            t_k = time_t + k
            snap = period_snapshots[k]
            for j in range(C2.extent):
                pos = slot_pos + j
                expected = ether_cell(pos + cum_w_before_slot + 4 * t_k)
                if snap[pos] != expected:
                    differs_at_some_phase = True
                    break
            if differs_at_some_phase:
                break
        if differs_at_some_phase and stable:
            out.append("Y")
            cum_w_before_slot = (cum_w_before_slot + C2.width) % 14
        else:
            out.append("N")
    return tuple(out)
