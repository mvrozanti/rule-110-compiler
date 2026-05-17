"""CTS state -> Rule 110 initial bitstring.

Scope and honest accounting:

  Cook (2004) §4 specifies a Rule 110 encoding where each CTS character is
  4 C2 gliders at α-aligned spacings (Y: `C2 18 C2 18 C2 14 C2`,
  N: `C2 18 C2 10 C2 14 C2`), with leaders (8 Ē gliders) for appendants and
  ossifiers (4 A4 gliders) for accepting characters. Executing the CTS
  inside Rule 110 then depends on a 30-plus-collision atlas that Cook
  validates abstractly via diagonal/vertical ether-distance arithmetic
  (Cook §3.3-§3.5).

  This module implements only the **state-encoding** part of Cook's
  construction: given a CTS tape, place a C-glider at each Y position and
  ether at each N position, in a region_map-indexed slot layout. The
  decoder in runtime/decode.py reads slots and recovers Y/N. This round-
  trips state through Rule 110 but does **not** execute CTS appendants in
  Rule 110; the appendant dynamics are still in Python (compiler/cts.py).

  Faithful Cook §4 spacings (18α, 14α, 10α) translate ambiguously to raw
  cell counts under our single-C-variant catalog. Documenting the gap is
  in docs/decisions/0001-... and the README; closing it is the unfinished
  collision-atlas work, blocked on phase 2 (E) and phase 3 (collisions).

The encoder is deterministic and produces a structure the viz can colour:
each slot's cell range is returned in region_map.
"""

from dataclasses import dataclass

from compiler.cts import CTSSpec, CTSState
from core.ether import SPATIAL_PERIOD, ether_cell, ether_window
from core.gliders import C


SLOT_SPACING = 56
LEFT_PAD = 4 * SPATIAL_PERIOD
RIGHT_PAD = 4 * SPATIAL_PERIOD


@dataclass(frozen=True)
class RegionMap:
    slot_starts: tuple[int, ...]
    slot_width: int
    glider: str

    def slot_range(self, idx: int) -> tuple[int, int]:
        start = self.slot_starts[idx]
        return start, start + self.slot_width


@dataclass(frozen=True)
class R110Encoding:
    initial: tuple[int, ...]
    region_map: RegionMap


def _align_phase(pos: int, target_phase: int) -> int:
    here = pos % SPATIAL_PERIOD
    shift = (target_phase - here + SPATIAL_PERIOD) % SPATIAL_PERIOD
    return pos + shift


def encode_cts_state(tape: tuple[str, ...]) -> R110Encoding:
    """Encode a CTS tape as a Rule 110 initial bitstring.

    Each tape symbol occupies one slot of SLOT_SPACING cells. 'Y' places a
    C glider in that slot; 'N' leaves it as pure ether. The width is
    LEFT_PAD + len(tape) * SLOT_SPACING + RIGHT_PAD, rounded up to a
    full ether period.
    """
    n_slots = len(tape)
    width = LEFT_PAD + n_slots * SLOT_SPACING + RIGHT_PAD
    width += (SPATIAL_PERIOD - width % SPATIAL_PERIOD) % SPATIAL_PERIOD

    state = list(ether_window(0, width))
    slot_starts: list[int] = []
    base = LEFT_PAD
    for i, sym in enumerate(tape):
        slot_start = base + i * SLOT_SPACING
        slot_anchor = _align_phase(slot_start, C.left_phase)
        slot_starts.append(slot_start)
        if sym == "Y":
            for off, b in C.delta:
                if 0 <= slot_anchor + off < width:
                    state[slot_anchor + off] = b
        elif sym == "N":
            pass
        else:
            raise ValueError(f"unsupported CTS symbol {sym!r}; expected Y or N")

    region_map = RegionMap(
        slot_starts=tuple(slot_starts),
        slot_width=SLOT_SPACING,
        glider=C.name,
    )
    return R110Encoding(initial=tuple(state), region_map=region_map)


def encode_cts_spec(spec: CTSSpec) -> R110Encoding:
    """Encode the *initial* CTS tape of a spec. Appendants are not encoded
    into the IC at all in this minimal implementation; they live in the
    Python-side CTS simulator (see scope note at the top of this module).
    """
    return encode_cts_state(spec.initial_tape)


def encode_cts_runstate(state: CTSState) -> R110Encoding:
    return encode_cts_state(state.tape)
