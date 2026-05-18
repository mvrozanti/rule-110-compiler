"""Cook-faithful CTS tape encoding + scanner-Ebar end-to-end inside Rule 110.

Encodes a CTS tape as Cook-faithful C2 gliders + an Ebar scanner. Runs
Rule 110 forward. Asserts:

  1. Every Y symbol's C2 survives as a stationary period-7 glider.
  2. The scanner Ebar emerges on the far left, having crossed every Y
     symbol on the tape via the verified Cook §3.2.4 crossing collision.

Each crossing is one elementary Rule 110 collision; for a Y-rich tape of
length N, this is N verified Cook-collision steps occurring inside the
automaton's spacetime.
"""

import pytest

from compiler.cook_tape import C2_SEP, encode_tape
from compiler.glider_detect import find_displaced_glider, is_stationary_glider
from core.cook_gliders import C2, Ebar
from core.rule110 import step


def _evolve(state, n):
    s = tuple(state)
    for _ in range(n):
        s = step(s, boundary="ether")
    return s


def _post_steps_for_tape(n_symbols: int) -> int:
    """Generous post-evolution step count: enough for Ebar to cross every
    symbol and reach the safe central region for detection. C2_SEP per
    symbol traversal × travel time + padding."""
    base = 1400
    return base + n_symbols * 200


def _run(tape):
    post = _post_steps_for_tape(len(tape))
    ic = encode_tape(tape, with_scanner=True, post_steps_for_padding=post)
    s_t = _evolve(ic.initial, post)
    s_t_c2 = _evolve(s_t, C2.period_t)
    s_t_eb = _evolve(s_t, Ebar.period_t)
    return ic, post, s_t, s_t_c2, s_t_eb


@pytest.mark.parametrize("tape", [
    ("Y",),
    ("Y", "Y"),
    ("Y", "Y", "Y"),
    ("Y", "Y", "Y", "Y", "Y"),
])
def test_all_y_tape_survives_scanner_pass(tape):
    """Every Y on an all-Y tape persists after the scanner Ebar traverses
    the full tape inside Rule 110."""
    ic, post, s_t, s_t_c2, _ = _run(tape)
    for i, anchor in enumerate(ic.c2_anchors):
        assert is_stationary_glider(s_t, s_t_c2, anchor, C2.extent, post), (
            f"C2 at slot {i} (anchor {anchor}) did not survive scanner traversal"
        )


@pytest.mark.parametrize("tape", [
    ("Y", "Y", "Y"),
    ("Y", "Y", "Y", "Y", "Y"),
])
def test_scanner_ebar_emerges_on_far_left(tape):
    """The scanner Ebar reaches the safe central region to the left of
    the tape after crossing every Y, demonstrating completed traversal."""
    ic, post, s_t, _, s_t_eb = _run(tape)
    safe_lo = post + 50
    safe_hi = ic.c2_anchors[0] - 20
    eb_at = find_displaced_glider(
        s_t, s_t_eb, displacement=Ebar.displacement, time_t=post,
        extent=Ebar.extent, search_left=safe_lo, search_right=safe_hi,
    )
    assert eb_at is not None, (
        f"scanner Ebar did not emerge on the left for tape {tape}"
    )


def test_five_step_computation_inside_rule_110():
    """End-to-end claim: a 5-symbol Y tape encoded inside Rule 110, with
    a scanner Ebar, executes 5 verified Cook §3.2.4 crossings as the
    evolution runs forward. Five elementary Cook-collision steps of
    computation inside the automaton."""
    tape = ("Y",) * 5
    ic, post, s_t, s_t_c2, s_t_eb = _run(tape)

    all_y_survived = all(
        is_stationary_glider(s_t, s_t_c2, a, C2.extent, post)
        for a in ic.c2_anchors
    )
    assert all_y_survived, "not every Y tape symbol survived"

    safe_lo = post + 50
    safe_hi = ic.c2_anchors[0] - 20
    eb_at = find_displaced_glider(
        s_t, s_t_eb, displacement=Ebar.displacement, time_t=post,
        extent=Ebar.extent, search_left=safe_lo, search_right=safe_hi,
    )
    assert eb_at is not None, "scanner Ebar did not complete the 5-symbol traversal"


def test_tape_with_n_and_y_mixed():
    """N slots contain no C2; the scanner passes through them without
    interaction. Y slots host a C2 that survives the scanner. Tape:
    Y N Y N Y — three crossings."""
    tape = ("Y", "N", "Y", "N", "Y")
    ic, post, s_t, s_t_c2, s_t_eb = _run(tape)

    for i, anchor in enumerate(ic.c2_anchors):
        assert is_stationary_glider(s_t, s_t_c2, anchor, C2.extent, post), (
            f"Y at slot {i} did not survive scanner pass"
        )

    safe_lo = post + 50
    safe_hi = ic.c2_anchors[0] - 20
    eb_at = find_displaced_glider(
        s_t, s_t_eb, displacement=Ebar.displacement, time_t=post,
        extent=Ebar.extent, search_left=safe_lo, search_right=safe_hi,
    )
    assert eb_at is not None
