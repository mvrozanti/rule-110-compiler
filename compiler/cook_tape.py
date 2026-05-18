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
    c2_anchors: list[int] = []
    target = tape_start
    for sym in tape:
        if sym == "Y":
            a, cw = place_cook_glider(state, target, C2, cumulative_width=cw)
            slot_positions.append(a)
            c2_anchors.append(a)
            target = a + C2_SEP
        elif sym == "N":
            slot_positions.append(target)
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
        ebar_anchor=ebar_anchor,
    )
