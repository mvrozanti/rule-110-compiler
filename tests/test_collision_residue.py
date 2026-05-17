"""Empirical collision residue behaviour for our catalogue.

Documents what C × Ē actually does in our Rule 110 with our verified
glider patterns: a destructive collision that produces an expanding
disturbance, NOT a clean Cook §3.2.4 crossing or a clean post-collision
glider set.

These tests pin the empirical reality so future regressions of
core/rule110.py or core/gliders.py are caught.
"""

import pytest

from core.ether import SPATIAL_PERIOD, ether_window
from core.gliders import C, Ebar
from core.rule110 import step
from scripts.probe_collisions import (
    place_glider, find_diff_clusters, signature_of_cluster, matches_known,
)


def _names_after_collision(c_seps_from_anchor, ebar_offset_from_last_c, post_steps, width_units=400):
    width = SPATIAL_PERIOD * width_units
    anchor = width // 2
    s = list(ether_window(0, width))
    cs_anchors = []
    for off in c_seps_from_anchor:
        a = place_glider(s, C, anchor + off)
        cs_anchors.append(a)
    place_glider(s, Ebar, cs_anchors[-1] + ebar_offset_from_last_c)
    state = tuple(s)
    for _ in range(post_steps):
        state = step(state, boundary="ether")
    safe_lo = post_steps + 50
    safe_hi = width - post_steps - 50
    clusters = [c for c in find_diff_clusters(state, post_steps) if safe_lo <= c[0] and c[-1] <= safe_hi]
    sigs = [signature_of_cluster(state, post_steps, c) for c in clusters]
    return sorted(matches_known(s) or "?" for s in sigs)


def test_c_x_ebar_head_on_destroys_both():
    """When Ē actually reaches C (instead of still being en route), the
    collision destroys both gliders. The post-collision state is a single
    'unknown' (non-catalogue) cluster — an expanding disturbance, not a
    glider in our catalogue."""
    names = _names_after_collision(c_seps_from_anchor=[0], ebar_offset_from_last_c=84, post_steps=420)
    assert "C" not in names, f"C survived an actual collision: {names}"
    assert "Ebar" not in names, f"Ē survived an actual collision: {names}"
    assert names == ["?"], f"expected single unknown residue: {names}"


def test_tight_tape_collapses_under_single_ebar():
    """A 28-cell-spaced tape of multiple Cs collapses entirely when one Ē
    is launched from the right: the collision disturbance expands fast
    enough to consume neighbouring Cs."""
    names = _names_after_collision(
        c_seps_from_anchor=[0, 28, 56],
        ebar_offset_from_last_c=200,
        post_steps=1260,
    )
    assert names.count("C") <= 1, f"tight tape preserved Cs: {names}"


def test_widely_spaced_tape_keeps_left_c_at_first_collision():
    """At C separation 168 cells, the leftward expansion of the C × Ē
    residue is slow enough that one Ē destroys only the rightmost C
    in the first interaction. (The disturbance does continue to expand
    and eventually consume left Cs — see test below.)"""
    names = _names_after_collision(
        c_seps_from_anchor=[0, 168],
        ebar_offset_from_last_c=200,
        post_steps=1260,
    )
    assert names.count("C") == 1, (
        f"expected 1 C surviving the first collision, got {names}"
    )


def test_collision_residue_expands_unboundedly():
    """The C × Ē collision residue grows over time at ~0.19 cells/step
    (extent at t=840 is ~30 cells; at t=2030 it's ~257). It is not a
    glider — it has no fixed extent."""
    width = SPATIAL_PERIOD * 600
    anchor = width // 2
    s = list(ether_window(0, width))
    place_glider(s, C, anchor)
    place_glider(s, Ebar, anchor + 200)
    state = tuple(s)
    extents = []
    for target_t in (840, 1400, 1960):
        steps_needed = target_t - sum(s for _, s in [(0, 0)])
        s2 = state
        for _ in range(target_t):
            s2 = step(s2, boundary="ether")
        safe_lo = target_t + 50
        safe_hi = width - target_t - 50
        clusters = [c for c in find_diff_clusters(s2, target_t) if safe_lo <= c[0] and c[-1] <= safe_hi]
        if clusters:
            extents.append(len(clusters[0]))
    assert len(extents) >= 2
    assert extents[-1] > extents[0] * 1.5, (
        f"residue should expand over time, got extents {extents}"
    )
