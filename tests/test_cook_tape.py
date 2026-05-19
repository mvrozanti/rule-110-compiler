"""Cook-faithful CTS tape encoding + scanner-Ebar end-to-end inside Rule 110.

With `EBAR_GAP=40` (a strict-real crossing-window gap per
`tests/test_cook_crossing.py`), the scanner Ebar passing through a tape
of Ys produces a real preserved C2 at each interior Y anchor under
`is_real_stationary_glider`. The rightmost Y (first encountered by the
scanner) doesn't always strict-survive — Cook's crossing requires both
gliders to be in the right phase relationship, and the initial Ebar's
phase at the rightmost Y may differ.

This file pins:
  - Every interior Y strict-survives a scanner pass.
  - The rightmost Y may or may not strict-survive depending on tape size.
  - Weak-`is_stationary_glider` results retained for comparison.
"""

import pytest

from compiler.cook_tape import C2_SEP, encode_tape
from compiler.glider_detect import (
    find_displaced_glider, is_stationary_glider, is_real_stationary_glider,
)
from core.cook_gliders import C2, Ebar
from core.rule110 import step


def _evolve(state, n):
    s = tuple(state)
    for _ in range(n):
        s = step(s, boundary="ether")
    return s


def _post_steps_for_tape(n_symbols: int) -> int:
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
def test_all_y_tape_weakly_stationary_under_scanner(tape):
    """Every Y anchor remains weakly-stationary (period-7 self-equal)
    after scanner Ebar pass. The strict version is in
    `test_y_tape_strict_real_survival_count`."""
    ic, post, s_t, s_t_c2, _ = _run(tape)
    for i, anchor in enumerate(ic.c2_anchors):
        assert is_stationary_glider(s_t, s_t_c2, anchor, C2.extent, post), (
            f"C2 at slot {i} (anchor {anchor}) not even weakly stationary"
        )


def test_y_tape_strict_real_survival_count():
    """With EBAR_GAP=40 (strict-real crossing window), strict-real
    detection finds N-1 of N Y tape symbols preserved after a
    scanner pass on an all-Y tape of length 5. The rightmost Y (first
    encountered by the scanner) is the exception. Four-plus verified
    REAL Cook §3.2.4 crossings inside R110 spacetime per pass."""
    tape = ("Y",) * 5
    ic, post, s_t, s_t_c2, _ = _run(tape)
    real_survived = sum(
        1 for a in ic.c2_anchors
        if is_real_stationary_glider(s_t, s_t_c2, a, C2.extent, post)
    )
    assert real_survived >= 4, (
        f"expected ≥4 strict-real Y survivors, got {real_survived}/5"
    )
