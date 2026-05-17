"""End-to-end pipeline test: a small BF program lowered all the way to CTS.

The compile chain runs:
    BF source
      |  (manually mapped to 2-symbol TM; the auto-generated 8-symbol TM
      |   from compiler/bf_to_tm.py is correct but not directly amenable
      |   to Cook §2.1, which requires a 2-symbol TM)
      v
    2-symbol Turing machine
      |  (compiler/tm_to_tagsystem.py, Cook §2.1)
      v
    aligned 2-tag system
      |  (compiler/tagsystem_to_cts.py.build_cts_from_aligned, Cook §2.2)
      v
    cyclic tag system
      |  (compiler/cts.py.run)
      v
    final CTS tape

For the program `+` (BF: single increment), the corresponding TM writes 1
and halts. After running the full chain, the CTS should consume its tape
and either halt or produce a tape we can decode back to the TM final state.
"""

import pytest

from compiler.aligned_tagsystem import run as run_atag
from compiler.cts import run as run_cts
from compiler.tagsystem_to_cts import build_cts_from_aligned
from compiler.tm import TM
from compiler.tm_to_tagsystem import build_aligned_tag, decode_tape as decode_atag


def bf_plus_as_two_symbol_tm() -> TM:
    return TM(
        transitions={("q0", 0): ("qhalt", 1, "R")},
        initial_state="q0",
        initial_tape=(0,),
        initial_head=0,
        blank=0,
    )


def test_bf_plus_lowers_to_tm_to_aligned_tag_to_cts():
    tm = bf_plus_as_two_symbol_tm()
    ats = build_aligned_tag(tm)

    atag_history = run_atag(ats, max_steps=400)
    final_atag = atag_history[-1]
    decoded = decode_atag(final_atag.tape, final_atag.use_offset)
    assert decoded is not None
    assert decoded.state == "qhalt"
    assert decoded.head_bit == 0
    assert decoded.tl == 1
    assert decoded.tr == 0

    cts_spec, sym_idx, prefix = build_cts_from_aligned(ats)
    assert len(cts_spec.appendants) == 2 * len(sym_idx)
    cts_history = run_cts(cts_spec, max_steps=20000)
    final_cts = cts_history[-1]
    assert final_cts.halted, (
        f"CTS did not terminate after 20000 steps; tape size at end = {len(final_cts.tape)}"
    )


def test_chain_pipeline_uses_2k_appendant_structure():
    tm = bf_plus_as_two_symbol_tm()
    ats = build_aligned_tag(tm)
    cts_spec, sym_idx, prefix = build_cts_from_aligned(ats)
    k = len(sym_idx)
    real_half = cts_spec.appendants[:k]
    empty_half = cts_spec.appendants[k:]
    assert all(app == () for app in empty_half), (
        "Cook §2.2 requires the second k appendants to be empty"
    )
    assert any(len(app) > 0 for app in real_half), (
        "at least one real appendant should be non-empty"
    )


def bf_plus_plus_as_two_symbol_tm() -> TM:
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


def test_bf_plus_plus_chains_through_full_pipeline():
    tm = bf_plus_plus_as_two_symbol_tm()
    ats = build_aligned_tag(tm)
    atag_history = run_atag(ats, max_steps=2000)
    final_atag = atag_history[-1]
    decoded = decode_atag(final_atag.tape, final_atag.use_offset)
    assert decoded is not None
    assert decoded.state == "qhalt"
    assert decoded.tl == 3
    assert decoded.tr == 0

    cts_spec, sym_idx, prefix = build_cts_from_aligned(ats)
    cts_history = run_cts(cts_spec, max_steps=200000)
    assert cts_history[-1].halted, (
        f"CTS did not halt; tape size {len(cts_history[-1].tape)}"
    )
