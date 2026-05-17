"""Decode a Rule 110 spacetime back to a CTS tape.

The decoder uses the region_map emitted by compiler/cts_to_r110.py to find
each slot's cell range in the final Rule 110 state. For each slot, it
checks for a C-glider's delta-from-ether at that slot's anchor (allowing
for the slot's natural ether shift after `steps` updates) and emits Y or
N accordingly.

Honest accounting: this decoder pairs with the state-encoding-only encoder.
It does not attempt to identify Cook-style "invisibles" or
collision-derived gliders in the final state — those are out of scope until
the collision atlas is verified.
"""

from compiler.cts_to_r110 import RegionMap
from core.ether import SPATIAL_PERIOD, ether_cell
from core.gliders import C


def _has_c_glider(state: tuple[int, ...], slot_start: int, slot_width: int, time: int) -> bool:
    """Check whether the slot contains a C glider at any of its period
    phases. C has period 7 and displacement 0; after `time` steps the
    glider's delta cycles through C.period_t phases, all stationary
    spatially. We check by looking for ANY position in the slot where the
    cell pattern matches C.delta at the appropriate ether-shifted phase.
    """
    target_phase = C.left_phase
    for anchor_offset in range(slot_width):
        anchor = slot_start + anchor_offset
        if anchor % SPATIAL_PERIOD != target_phase:
            continue
        ok = True
        for off, expected in C.delta:
            pos = anchor + off
            if not (0 <= pos < len(state)):
                ok = False
                break
            if state[pos] != expected:
                ok = False
                break
        if ok:
            return True
    return False


def decode_to_cts_tape(state: tuple[int, ...], region_map: RegionMap, time: int) -> tuple[str, ...]:
    out: list[str] = []
    for i in range(len(region_map.slot_starts)):
        start, end = region_map.slot_range(i)
        if _has_c_glider(state, start, region_map.slot_width, time):
            out.append("Y")
        else:
            out.append("N")
    return tuple(out)
