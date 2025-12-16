"""Helpers for Cook-style ether and glider packages.

Patterns below follow the canonical 14-cell ether described by Cook (2004).
Glider packages are still placeholders: we approximate A/B/C/D + DELIM to
maintain structure and spacing/phase checks. Swap these with measured Cook
packages when available; phase modulus remains 14.
"""
from dataclasses import dataclass
from typing import List, Dict, Tuple

# Ether pattern: canonical 14-cell period for Rule 110 ether (Cook, 2004).
# Ether repeats every 14 cells; phase alignment is always mod 14.
ETHER_BASE: List[int] = [0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0]
PHASE_MOD = len(ETHER_BASE)

# Package snippets (structured placeholders). Replace with measured Cook
# patterns when available; lengths preserved for scheduler constraints.
GLIDER_PACKAGES: Dict[str, List[int]] = {
    "A": [1, 0, 1, 1, 0, 0, 1, 1, 0],
    "B": [1, 1, 0, 1, 1, 0, 0, 1],
    "C": [1, 1, 1, 0, 0, 1, 0, 1],
    "D": [1, 0, 0, 1, 1, 0, 1, 0, 0],
    "DELIM": [1, 1, 1, 0, 1, 0, 0, 1],
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
    placements = [PackagePlacement(name, offset, phase % PHASE_MOD) for name, offset, phase in packages]
    tape, _ = build_base_tape(length, placements)
    return tape


def max_package_len() -> int:
    """Return the maximum package length (for spacing heuristics)."""
    return max(len(pkg) for pkg in GLIDER_PACKAGES.values())
