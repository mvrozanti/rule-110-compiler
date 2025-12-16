"""Helpers for Cook-style ether and glider packages.

This is a pragmatic approximation to the packages described in
Cook (2004), enough to let us place ether, inject packages, and
validate spacing/phase when building CTS initial states.
"""
from dataclasses import dataclass
from typing import List, Dict, Tuple

# Ether pattern: canonical 14-cell period for Rule 110 ether (Cook, 2004).
ETHER_BASE: List[int] = [0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0]

# Canonical package snippets (approximations of Cook’s A/B/C/D glider packages).
# These are placeholders to keep structure; refine with measured patterns if available.
GLIDER_PACKAGES: Dict[str, List[int]] = {
    "A": [1, 1, 0, 1, 1, 0, 0, 1, 0],
    "B": [1, 0, 1, 1, 0, 0, 1, 1],
    "C": [1, 1, 1, 0, 0, 1, 0, 1],
    "D": [1, 0, 0, 1, 1, 0, 1, 0, 0],
    "DELIM": [1, 1, 1, 0, 1, 0, 0, 1],  # delimiter / marker
}

@dataclass
class PackagePlacement:
    name: str
    offset: int
    phase: int = 0


def make_ether(length: int, phase: int = 0) -> List[int]:
    """Return an ether tape of at least ``length`` cells starting at ``phase``."""
    if length <= 0:
        return []
    ether = []
    base = ETHER_BASE
    for i in range(length):
        ether.append(base[(phase + i) % len(base)])
    return ether


def place_package(state: List[int], package: List[int], offset: int) -> List[int]:
    """Return a new state with the package written at ``offset`` (extending if needed)."""
    if offset < 0:
        raise ValueError("offset must be non-negative")
    new_state = list(state)
    end = offset + len(package)
    if end > len(new_state):
        new_state.extend([0] * (end - len(new_state)))
    new_state[offset:end] = package
    return new_state


def build_base_tape(length: int, packages: List[PackagePlacement]) -> Tuple[List[int], List[PackagePlacement]]:
    """Create ether tape and place packages; returns (tape, placements used)."""
    tape = make_ether(length)
    applied: List[PackagePlacement] = []
    for placement in packages:
        pkg = GLIDER_PACKAGES.get(placement.name)
        if not pkg:
            raise ValueError(f"Unknown package '{placement.name}'")
        tape = place_package(tape, pkg, placement.offset)
        applied.append(placement)
    return tape, applied


def build_initial_state(packages: List[Tuple[str, int, int]], ether_periods: int = 200, ether_phase: int = 0) -> List[int]:
    """
    Construct an initial tape from (name, offset, phase) packages on ether.
    """
    length = ether_periods * len(ETHER_BASE)
    base = make_ether(length, phase=ether_phase)
    placements = [PackagePlacement(name, offset, phase) for name, offset, phase in packages]
    tape, _ = build_base_tape(length, placements)
    return tape
