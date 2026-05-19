"""Structural glider detection by period/displacement, not bit pattern.

Rationale: Cook's collisions can change a glider's local left_phase
(see ADR 0005). A glider that was at left_phase L before a crossing
may emerge at left_phase L' ≠ L afterwards, with different specific
bits at the same absolute position. Bit-pattern matching against a
single canonical delta misses these. Detecting gliders by their
*dynamical* invariants — period T and spatial displacement D — is
robust to the phase shift.

Two helpers:

  - `is_stationary_glider`: a region is a stationary (D=0) glider of
    period T iff cells in it at time t equal cells in it at time t+T,
    and the cells differ from time-shifted ether in at least one
    position (excluding pure ether, which is trivially period-T for
    T dividing the ether temporal period of 7).

  - `find_displaced_glider`: scan a state at time t for any contiguous
    non-ether region whose pattern reappears in state_t_plus_T shifted
    by `displacement` cells. Returns the leftmost anchor, or None.

Both helpers operate on two pre-computed snapshots of the Rule 110
state, so callers control the evolution and can verify multiple periods
by repeating the check.
"""

from core.ether import SPATIAL_PERIOD, ether_cell


def _differs_from_ether(state, anchor, extent, time_t):
    """Return True if any cell in [anchor, anchor+extent) differs from
    time-shifted ether."""
    for j in range(extent):
        pos = anchor + j
        if not (0 <= pos < len(state)):
            return False
        if state[pos] != ether_cell(pos + 4 * time_t):
            return True
    return False


def is_stationary_glider(state_t, state_t_plus_T, anchor, extent, time_t):
    """True iff the window [anchor, anchor+extent) is non-ether at time t
    AND identical at time t+T (i.e. stationary period T).

    The caller is responsible for ensuring state_t_plus_T was reached by
    exactly T evolutions from state_t.
    """
    if not _differs_from_ether(state_t, anchor, extent, time_t):
        return False
    for j in range(extent):
        pos = anchor + j
        if not (0 <= pos < len(state_t_plus_T)):
            return False
        if state_t[pos] != state_t_plus_T[pos]:
            return False
    return True


def is_real_stationary_glider(state_t, state_t_plus_T, anchor, extent, time_t,
                              n_periods=3):
    """Stronger stationary check: cells at anchor are stable AND differ from
    *every* possible Cook-shifted ether phase (0..13). Excludes pure ether at
    any shifted phase, leaving only genuine glider structures.

    Verifies stability across `n_periods` evolutions of T = period implicit in
    the snapshots — the caller must supply state_t_plus_T such that the period
    matches their interest. For C2 (period 7), the caller calls with
    state_t_plus_T = evolve(state_t, 7).
    """
    if not is_stationary_glider(state_t, state_t_plus_T, anchor, extent, time_t):
        return False
    for cum_w in range(SPATIAL_PERIOD):
        matches_this_phase = True
        for j in range(extent):
            pos = anchor + j
            if not (0 <= pos < len(state_t)):
                matches_this_phase = False
                break
            expected = ether_cell(pos + cum_w + 4 * time_t)
            if state_t[pos] != expected:
                matches_this_phase = False
                break
        if matches_this_phase:
            return False
    return True


def is_real_displaced_glider(snapshots, anchor, extent,
                             displacement, time_t_start, period_t, n_periods=3):
    """Stronger displaced check across multiple periods.

    `snapshots` must be a sequence of `n_periods+1` Rule 110 states,
    `period_t` evolutions apart, starting at `time_t_start`. Returns True
    iff the pattern at `anchor` in `snapshots[0]` reappears at
    `anchor + k*displacement` in `snapshots[k]` for every k in
    [1, n_periods], AND the pattern differs from every Cook-shifted
    ether phase at time_t_start (excludes shifted-ether false matches
    that arise because 4*period_t mod 14 = 0).
    """
    if len(snapshots) < n_periods + 1:
        return False
    n = len(snapshots[0])
    if anchor < 0 or anchor + extent > n:
        return False
    window = tuple(snapshots[0][anchor + j] for j in range(extent))
    for k in range(1, n_periods + 1):
        moved = anchor + k * displacement
        if moved < 0 or moved + extent > n:
            return False
        for j in range(extent):
            if snapshots[k][moved + j] != window[j]:
                return False
    for cum_w in range(SPATIAL_PERIOD):
        matches = True
        for j in range(extent):
            if snapshots[0][anchor + j] != ether_cell(anchor + j + cum_w + 4 * time_t_start):
                matches = False
                break
        if matches:
            return False
    return True


def find_displaced_glider(state_t, state_t_plus_T, displacement,
                          time_t, extent=8,
                          search_left=None, search_right=None):
    """Scan state_t for a window of length `extent` whose contents reappear
    in state_t_plus_T shifted by `displacement` cells, where the window
    is non-ether at time t.

    Returns the leftmost anchor satisfying these conditions, or None.

    Search bounds default to the full state (less a safety margin for the
    displacement). For a leftward-moving glider (displacement < 0), the
    target position `anchor + displacement` must still be in bounds.
    """
    n = len(state_t)
    if search_left is None:
        search_left = max(0, -displacement)
    if search_right is None:
        search_right = n - max(0, displacement) - extent

    for anchor in range(search_left, search_right):
        if not _differs_from_ether(state_t, anchor, extent, time_t):
            continue
        target = anchor + displacement
        if target < 0 or target + extent > n:
            continue
        match = True
        for j in range(extent):
            if state_t[anchor + j] != state_t_plus_T[target + j]:
                match = False
                break
        if match:
            return anchor
    return None
