"""Round-trip: CTS tape -> Rule 110 IC -> evolve -> decode -> CTS tape.

The encoder is state-encoding-only (see compiler/cts_to_r110.py scope note);
these tests verify the encoding round-trips through Rule 110 evolution.
They do **not** verify that Rule 110 evolution emulates CTS step
dynamics — that requires the unfinished collision atlas.
"""

import pytest

from compiler.cts_to_r110 import encode_cts_state
from runtime.decode import decode_to_cts_tape
from runtime.evolve import evolve


@pytest.mark.parametrize("tape,steps", [
    ((), 0),
    ((), 100),
    (("Y",), 0),
    (("Y",), 7),
    (("Y",), 70),
    (("N",), 0),
    (("N",), 70),
    (("Y", "N"), 7),
    (("Y", "Y", "N", "Y"), 21),
    (("N", "Y", "N", "Y", "N"), 49),
])
def test_round_trip_preserves_cts_tape(tape, steps):
    enc = encode_cts_state(tape)
    history = evolve(enc, steps)
    decoded = decode_to_cts_tape(history[-1], enc.region_map, steps)
    assert decoded == tape, f"tape {tape} after {steps} steps decoded as {decoded}"


def test_empty_tape_yields_ether_only():
    enc = encode_cts_state(())
    from core.ether import ether_cell
    for i, b in enumerate(enc.initial):
        assert b == ether_cell(i), (
            f"empty tape encoding should be pure ether at position {i}: got {b}"
        )


def test_each_y_places_a_c_glider_delta():
    enc = encode_cts_state(("Y", "Y"))
    from core.gliders import C
    from core.ether import ether_cell
    starts = enc.region_map.slot_starts
    for s in starts:
        anchor = s
        while anchor % 14 != C.left_phase:
            anchor += 1
        for off, expected in C.delta:
            assert enc.initial[anchor + off] == expected, (
                f"at slot starting {s}, anchor {anchor}, offset {off}: "
                f"expected {expected}, got {enc.initial[anchor + off]}"
            )
