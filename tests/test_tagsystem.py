"""Tests for the tag-system simulator and the tag-system -> CTS reduction."""

from compiler.cts import run as run_cts
from compiler.tagsystem import TagState, TagSystem, run as run_tag, step as step_tag
from compiler.tagsystem_to_cts import build_cts, decode_tape


def test_2tag_halts_when_no_production():
    ts = TagSystem(productions={"A": ("B", "B")}, initial_tape=("X", "Y"))
    st = TagState(("X", "Y"))
    out = step_tag(ts, st)
    assert out.halted


def test_2tag_simple_run():
    ts = TagSystem(
        productions={"A": ("C", "C", "D", "D"), "B": ("E",), "C": ("A",), "D": (), "E": ()},
        initial_tape=("A", "C", "D", "A", "B", "B", "E"),
    )
    history = run_tag(ts, max_steps=10)
    assert history[1].tape == ("D", "A", "B", "B", "E", "C", "C", "D", "D")


def test_tag_to_cts_round_trip_simple():
    ts = TagSystem(
        productions={"A": ("B",), "B": ()},
        initial_tape=("A", "B"),
    )
    spec, idx = build_cts(ts)
    assert len(idx) == 2
    cts_history = run_cts(spec, max_steps=200)
    final = cts_history[-1]
    assert final.tape == ()


def test_tag_to_cts_encoding_uses_unary_blocks():
    ts = TagSystem(
        productions={"A": ("B",), "B": ("A",), "C": ()},
        initial_tape=("A",),
    )
    spec, idx = build_cts(ts)
    assert len(idx) == 3
    decoded_initial = decode_tape(spec.initial_tape, idx)
    assert decoded_initial == ("A",)


def test_tag_to_cts_appendant_count_matches_alphabet():
    ts = TagSystem(
        productions={"A": (), "B": (), "C": (), "D": ()},
        initial_tape=("A", "B"),
    )
    spec, idx = build_cts(ts)
    assert len(spec.appendants) == 4
