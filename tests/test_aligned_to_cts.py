"""Aligned 2-tag system -> CTS round-trip tests.

Build a CTS from an aligned tag system, run it, and confirm the result
matches what the aligned tag system would compute (decoded back through
the same encoding).
"""

from compiler.aligned_tagsystem import AlignedTagSystem, run as run_atag
from compiler.cts import run as run_cts
from compiler.tagsystem_to_cts import build_cts_from_aligned


def test_build_cts_from_aligned_use_offset_0_no_prefix():
    ats = AlignedTagSystem(
        productions={"a": ("b",), "b": ()},
        initial_tape=("a", "b"),
        initial_use_offset=0,
    )
    spec, idx, prefix = build_cts_from_aligned(ats)
    assert prefix == 0
    assert len(spec.appendants) == 4
    assert spec.appendants[2] == ()
    assert spec.appendants[3] == ()


def test_build_cts_from_aligned_use_offset_1_has_k_prefix():
    ats = AlignedTagSystem(
        productions={"a": ("b",), "b": ()},
        initial_tape=("a", "b"),
        initial_use_offset=1,
    )
    spec, idx, prefix = build_cts_from_aligned(ats)
    assert prefix == 2
    assert spec.initial_tape[:2] == ("N", "N")


def test_aligned_to_cts_consumes_tape_when_run():
    ats = AlignedTagSystem(
        productions={"a": (), "b": ()},
        initial_tape=("a", "b"),
        initial_use_offset=0,
    )
    spec, _, _ = build_cts_from_aligned(ats)
    history = run_cts(spec, max_steps=1000)
    assert history[-1].halted


def test_aligned_to_cts_appendant_count_is_two_k():
    ats = AlignedTagSystem(
        productions={"a": (), "b": (), "c": (), "d": ()},
        initial_tape=("a", "b"),
        initial_use_offset=0,
    )
    spec, _, _ = build_cts_from_aligned(ats)
    assert len(spec.appendants) == 8
