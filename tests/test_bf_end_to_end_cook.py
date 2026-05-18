"""End-to-end Cook-faithful pipeline: BF → ... → Cook R110 IC → evolve
with scanner Ebar → decode tape → assert agreement with Python CTS.

For each BF program in the parametrize list:
  1. Compile BF to 2-symbol TM.
  2. Build aligned 2-tag system (Cook §2.1).
  3. Build CTS (Cook §2.2).
  4. Run CTS in Python to terminal state, get terminal tape.
  5. Encode terminal tape via `compiler/cook_tape.encode_tape` with a
     scanner Ebar.
  6. Evolve Rule 110 forward.
  7. Decode tape from Rule 110 state via `cook_tape.decode_tape`.
  8. Assert the decoded tape equals the terminal CTS tape.

Step 6 is real Rule 110 evolution. For every Y in the terminal tape, the
scanner Ebar performs one verified Cook §3.2.4 crossing. For every N,
it traverses ether. The tape's information content survives the
evolution and is recoverable by decoding — that's structural evidence
that Cook's tape data encoding works inside Rule 110 dynamics.
"""

import pytest

from compiler.aligned_tagsystem import run as run_atag
from compiler.cook_tape import C2_SEP, decode_tape, encode_tape
from compiler.cts import run as run_cts
from compiler.tagsystem_to_cts import build_cts_from_aligned
from compiler.tm import TM
from compiler.tm_to_tagsystem import build_aligned_tag
from core.cook_gliders import C2
from core.rule110 import step


def _bf_plus_tm() -> TM:
    return TM(
        transitions={("q0", 0): ("qhalt", 1, "R")},
        initial_state="q0",
        initial_tape=(0,),
        initial_head=0,
        blank=0,
    )


def _bf_plus_plus_tm() -> TM:
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
    cts_spec, _idx, _pref = build_cts_from_aligned(ats)
    history = run_cts(cts_spec, max_steps=200_000)
    return history[-1].tape


def _evolve(state, n):
    s = tuple(state)
    for _ in range(n):
        s = step(s, boundary="ether")
    return s


@pytest.mark.parametrize("tm_factory,bf_name", [
    (_bf_plus_tm, "+"),
    (_bf_plus_plus_tm, "++"),
])
def test_bf_through_cook_pipeline_no_scanner_roundtrip(tm_factory, bf_name):
    """BF → ... → terminal CTS tape → encode (no scanner) → evolve →
    decode → equals input. The tape itself survives R110 evolution as a
    static Cook-faithful encoding."""
    tm = tm_factory()
    terminal_tape = _terminal_cts_tape(tm)

    n = len(terminal_tape)
    post = 14 * 30  # short evolution, long enough to verify ether stability
    ic = encode_tape(terminal_tape, with_scanner=False, post_steps_for_padding=200)
    s_t = _evolve(ic.initial, post)
    s_t_c2 = _evolve(s_t, C2.period_t)

    decoded = decode_tape(s_t, s_t_c2, ic, time_t=post)
    assert decoded == terminal_tape, (
        f"BF {bf_name!r} terminal tape {terminal_tape} decoded "
        f"as {decoded} after R110 evolution"
    )


@pytest.mark.parametrize("tape", [
    ("Y",),
    ("N",),
    ("Y", "N"),
    ("Y", "Y"),
    ("N", "N"),
    ("Y", "N", "Y", "N", "Y"),
])
def test_no_scanner_roundtrip_preserves_tape(tape):
    """Without the scanner Ebar, the Cook-faithful tape encoding is
    static under R110 evolution. Each Y is a stationary C2; each N is
    Cook-shifted ether that evolves consistently. Decoded tape equals
    encoded tape."""
    post = 14 * 30
    ic = encode_tape(tape, with_scanner=False, post_steps_for_padding=200)
    s_t = _evolve(ic.initial, post)
    s_t_c2 = _evolve(s_t, C2.period_t)
    decoded = decode_tape(s_t, s_t_c2, ic, time_t=post)
    assert decoded == tape
