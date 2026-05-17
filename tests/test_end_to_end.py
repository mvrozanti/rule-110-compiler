"""End-to-end: BF source -> ... -> Rule 110 IC -> evolve -> decode -> assert.

Honest scope:

  This chains all the verified pieces: BF parses -> 2-symbol TM (where the
  current chain handles it, i.e. R-only TMs hand-mapped for `+` and `++`)
  -> aligned 2-tag system -> CTS -> Python-side CTS run to terminal state
  -> encode terminal CTS tape as a Rule 110 IC -> evolve -> decode.

  The CTS *step* dynamics are executed in Python (compiler/cts.py), not in
  Rule 110. The Rule 110 layer only carries the *state* of the CTS tape
  through a faithful round-trip. Closing the universality demo to "CTS
  steps happen in R110" requires the unfinished collision atlas (see
  README, docs/gliders_status.md).

  These tests still exercise every other layer end-to-end and prove the
  encoder/decoder agree with the upstream simulators.
"""

from compiler.aligned_tagsystem import run as run_atag
from compiler.cts import run as run_cts
from compiler.cts_to_r110 import encode_cts_state, encode_cts_runstate
from compiler.tagsystem_to_cts import build_cts_from_aligned
from compiler.tm import TM
from compiler.tm_to_tagsystem import build_aligned_tag
from runtime.decode import decode_to_cts_tape
from runtime.evolve import evolve


def _bf_plus_as_tm() -> TM:
    return TM(
        transitions={("q0", 0): ("qhalt", 1, "R")},
        initial_state="q0",
        initial_tape=(0,),
        initial_head=0,
        blank=0,
    )


def _bf_plus_plus_as_tm() -> TM:
    return TM(
        transitions={
            ("q0", 0): ("q1", 1, "R"),
            ("q1", 0): ("qhalt", 1, "R"),
        },
        initial_state="q0",
        initial_tape=(0, 0, 0),
        initial_head=0,
        blank=0,
    )


def _terminal_cts_tape(tm: TM) -> tuple[str, ...]:
    ats = build_aligned_tag(tm)
    cts_spec, _sym_idx, _prefix = build_cts_from_aligned(ats)
    history = run_cts(cts_spec, max_steps=200_000)
    final = history[-1]
    return final.tape


def test_bf_plus_through_r110_round_trip():
    tm = _bf_plus_as_tm()
    terminal = _terminal_cts_tape(tm)
    enc = encode_cts_state(terminal)
    spacetime = evolve(enc, 49)
    decoded = decode_to_cts_tape(spacetime[-1], enc.region_map, 49)
    assert decoded == terminal, (
        f"BF '+' terminal CTS {terminal} round-tripped through R110 as {decoded}"
    )


def test_bf_plus_plus_through_r110_round_trip():
    tm = _bf_plus_plus_as_tm()
    terminal = _terminal_cts_tape(tm)
    enc = encode_cts_state(terminal)
    spacetime = evolve(enc, 49)
    decoded = decode_to_cts_tape(spacetime[-1], enc.region_map, 49)
    assert decoded == terminal


def test_bf_plus_chain_uses_every_layer():
    """Smoke check: the chain touches BF -> TM -> aligned tag -> CTS ->
    R110 IC -> evolve -> decode. Just confirms each call returns
    non-empty / typed results."""
    tm = _bf_plus_as_tm()
    ats = build_aligned_tag(tm)
    assert len(ats.productions) > 0
    cts_spec, sym_idx, _prefix = build_cts_from_aligned(ats)
    assert len(cts_spec.appendants) == 2 * len(sym_idx)
    atag_h = run_atag(ats, max_steps=400)
    assert len(atag_h) > 1
    cts_h = run_cts(cts_spec, max_steps=20_000)
    assert cts_h[-1].halted
    enc = encode_cts_state(cts_h[-1].tape)
    history = evolve(enc, 14)
    decoded = decode_to_cts_tape(history[-1], enc.region_map, 14)
    assert decoded == cts_h[-1].tape


def test_explicit_runstate_round_trip():
    from compiler.cts import CTSSpec, CTSState
    spec = CTSSpec(appendants=(("Y",), ()), initial_tape=("Y", "N", "Y"))
    state = CTSState(tape=spec.initial_tape, cursor=0)
    enc = encode_cts_runstate(state)
    history = evolve(enc, 21)
    decoded = decode_to_cts_tape(history[-1], enc.region_map, 21)
    assert decoded == ("Y", "N", "Y")
