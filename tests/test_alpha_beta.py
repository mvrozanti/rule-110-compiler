"""Empirical alpha/beta calibration for our verified glider catalog.

Cook (2004) §3.2 defines alpha (diagonal-ether-row) and beta (vertical-
ether-column) distances between same-direction gliders. The proof works
in (alpha, beta) coordinates because the two are independently adjustable.

For our purposes we want a cell-count translation: given two same-glider
placements at cell offset Δ, classify the configuration. The tests below
nail down what we have empirically observed:

  * Our C glider has period (7, 0); placement is constrained to left_phase
    == 3 (mod 14). So two C placements separated by Δ cells with both
    correctly aligned require Δ ≡ 0 (mod 14).
  * Our Ē glider has period (30, -8); left_phase == 10 (mod 14). Two Ēs
    separated by Δ cells require Δ ≡ 0 (mod 14) for clean placement.

  * C × C stable separations: 28 cells is the minimum where both Cs
    survive 420 R110 steps without disturbance to either. Spacings
    14 collide; ≥ 28 are stable.
  * Ē × Ē stable separations: 42 cells is the minimum where both Ēs
    survive cleanly (small period-30 'shadow' artifacts persist alongside
    them, see notes in docs/gliders_status.md). Spacings 14 or 28
    chaotically destabilise; ≥ 42 leave 2 Ēs intact.

  * Our C glider's 'width' (Cook §3.1, the ether offset mod 14 across the
    glider) measures as 0: the ether on its right is in-phase with the
    ether on its left extrapolated. This does not match any of Cook's
    documented C1/C2/C3 widths (9, 3, 11). It is consistent with a
    'no-net-ether-shift' stationary glider — we treat it as our 'C' and
    accept the documented divergence from Cook's classification.
"""

from core.ether import SPATIAL_PERIOD, ether_cell, ether_window
from core.gliders import C, Ebar
from core.rule110 import step
from scripts.probe_collisions import (
    place_glider, find_diff_clusters, signature_of_cluster, matches_known,
)


WIDTH = SPATIAL_PERIOD * 100
POST_STEPS = 420
SAFE_LO = POST_STEPS + 50
SAFE_HI = WIDTH - POST_STEPS - 50


def _evolve_with(placements):
    s = list(ether_window(0, WIDTH))
    anchor = WIDTH // 2
    for gl, off in placements:
        place_glider(s, gl, anchor + off)
    state = tuple(s)
    for _ in range(POST_STEPS):
        state = step(state, boundary="ether")
    clusters = [
        c for c in find_diff_clusters(state, POST_STEPS)
        if SAFE_LO <= c[0] and c[-1] <= SAFE_HI
    ]
    sigs = [signature_of_cluster(state, POST_STEPS, c) for c in clusters]
    return [matches_known(s) for s in sigs]


def _c_glider_width_mod_14() -> int:
    """Empirically read C's 'width' = the ether offset mod 14 between the
    ether on its right and the extrapolated left ether.

    We place C, evolve a full C period (7 steps), and compare cells on the
    right of the glider against the time-shifted ether reference.
    """
    s = list(ether_window(0, WIDTH))
    anchor = place_glider(s, C, WIDTH // 2)
    state = tuple(s)
    for _ in range(7):
        state = step(state, boundary="ether")
    shift = 4 * 7
    right_start = anchor + 11
    for offset in range(SPATIAL_PERIOD):
        match = True
        for i in range(20):
            pos = right_start + i
            if state[pos] != ether_cell(pos + offset + shift):
                match = False
                break
        if match:
            return offset
    return -1


def test_c_glider_width_is_zero_mod_14():
    """Our empirical C has zero ether offset across the glider; this does
    not match any of Cook's C1/C2/C3 widths (9, 3, 11). We document the
    divergence rather than pretending the catalogue matches Cook."""
    w = _c_glider_width_mod_14()
    assert w == 0, f"C glider width should be 0 (no ether shift), got {w}"


def test_c_x_c_minimum_stable_spacing_is_28_cells():
    """Two Cs at separation 14 collide; at 28 both survive."""
    survivors_14 = _evolve_with([(C, 0), (C, 14)])
    assert survivors_14.count("C") < 2, (
        f"C x C at sep 14 unexpectedly stable: {survivors_14}"
    )
    survivors_28 = _evolve_with([(C, 0), (C, 28)])
    assert survivors_28.count("C") == 2, (
        f"C x C at sep 28 should keep both: {survivors_28}"
    )


def test_c_x_c_wider_spacings_remain_stable():
    """C x C at multiples of 14 above 28 remain clean."""
    for sep in (28, 42, 56, 70, 84):
        survivors = _evolve_with([(C, 0), (C, sep)])
        assert survivors.count("C") == 2, (
            f"C x C at sep {sep} should keep both: {survivors}"
        )


def test_ebar_x_ebar_minimum_stable_separation_is_42_cells():
    """Two Ēs at sep 14 or 28 destabilise; at 42 both survive (alongside
    Ē's natural 'shadow' artifacts in the post-collision window)."""
    survivors_14 = _evolve_with([(Ebar, 0), (Ebar, 14)])
    assert survivors_14.count("Ebar") < 2, (
        f"Ebar x Ebar at sep 14 unexpectedly stable: {survivors_14}"
    )
    survivors_42 = _evolve_with([(Ebar, 0), (Ebar, 42)])
    assert survivors_42.count("Ebar") == 2, (
        f"Ebar x Ebar at sep 42 should keep both: {survivors_42}"
    )


def test_ether_period_is_placement_quantum_for_stationary_gliders():
    """For stationary gliders (C), placement is quantised to multiples of
    14 cells because their left_phase must agree with the ether phase."""
    s_a = list(ether_window(0, WIDTH))
    a1 = place_glider(s_a, C, WIDTH // 2)
    a2 = place_glider(s_a, C, WIDTH // 2 + 1)
    assert (a2 - a1) % SPATIAL_PERIOD == 0
    assert a2 - a1 == 0 or a2 - a1 >= SPATIAL_PERIOD
