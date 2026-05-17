"""Empirical collision fixtures.

Each test places verified gliders on clean ether at recorded offsets,
evolves Rule 110 for a fixed-step interval, and asserts the surviving
glider catalog in a boundary-effect-safe central window matches what we
have empirically observed. These fixtures are the seed of Cook's collision
atlas; they verify what Rule 110 *actually* does for our concrete glider
patterns, not what Cook's paper claims abstractly. Mismatches between
these and Cook's claims are documented in docs/gliders_status.md.
"""

from core.ether import SPATIAL_PERIOD, ether_window
from core.gliders import A, B, C, D, Ebar
from core.rule110 import step
from scripts.probe_collisions import (
    place_glider, find_diff_clusters, signature_of_cluster, matches_known,
)


POST_STEPS = 420
WIDTH = SPATIAL_PERIOD * 200
GAP = 100


def survivors(g1, g2, offset, post_steps=POST_STEPS):
    s = list(ether_window(0, WIDTH))
    anchor = WIDTH // 2
    place_glider(s, g1, anchor)
    place_glider(s, g2, anchor + GAP + offset)
    state = tuple(s)
    for _ in range(post_steps):
        state = step(state, boundary="ether")
    safe_lo = post_steps + 50
    safe_hi = WIDTH - post_steps - 50
    clusters = [c for c in find_diff_clusters(state, post_steps) if safe_lo <= c[0] and c[-1] <= safe_hi]
    sigs = [signature_of_cluster(state, post_steps, c) for c in clusters]
    names = sorted([n for n in (matches_known(s) for s in sigs) if n])
    return names, len(sigs)


def test_c_x_ebar_crosses_at_wide_offsets():
    """C and Ē both survive at separation >= 23 cells (Cook §3.2.4 crossing
    collision). This is the central reaction Cook's construction uses for
    moving data crossing tape data."""
    for off in (23, 30, 44, 80, 150):
        names, _total = survivors(C, Ebar, off)
        assert "C" in names and "Ebar" in names, (
            f"C x Ebar at offset {off}: expected both to survive, got {names}"
        )


def test_a_x_a_parallel():
    """Two A gliders moving rightward at offsets where they cannot collide
    propagate independently (both survive)."""
    for off in (0, 10, 25):
        names, _ = survivors(A, A, off)
        assert names.count("A") == 2, f"A x A off={off}: {names}"


def test_c_x_c_parallel():
    """Stationary C-gliders at any non-trivial offset coexist."""
    for off in (10, 25, 50, 100):
        names, _ = survivors(C, C, off)
        assert names.count("C") == 2, f"C x C off={off}: {names}"


def test_ebar_x_ebar_parallel():
    """Two Ē gliders both moving left at constant velocity coexist when not
    placed in collision range."""
    for off in (0, 10, 25):
        names, _ = survivors(Ebar, Ebar, off)
        assert names.count("Ebar") == 2, f"Ebar x Ebar off={off}: {names}"
