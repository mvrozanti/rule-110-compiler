"""Spacing and phase scheduler for Cook-style glider packages."""
from dataclasses import dataclass
from typing import List, Tuple

from cook_gliders import PackagePlacement, ETHER_BASE

# Minimal safe gap between packages (heuristic; Cook spacing is phase-sensitive).
MIN_SPACING = 6


@dataclass
class ScheduleResult:
    placements: List[PackagePlacement]
    warnings: List[str]
    valid: bool


def schedule_packages(packages: List[PackagePlacement], min_gap: int = MIN_SPACING, phase_mod: int = None) -> ScheduleResult:
    """
    Ensure package ordering, spacing, and (optionally) phase alignment.

    Args:
        packages: placements with desired offsets
        min_gap: minimal cell gap between consecutive packages
        phase_mod: optional modulus for phase consistency (defaults to ether period)
    """
    warnings: List[str] = []
    if not packages:
        return ScheduleResult([], ["No packages supplied"], False)

    phase_mod = phase_mod or len(ETHER_BASE)
    ordered = sorted(packages, key=lambda p: p.offset)
    valid = True

    for i in range(1, len(ordered)):
        gap = ordered[i].offset - (ordered[i - 1].offset + 1)
        if gap < min_gap:
            warnings.append(f"Gap too small between {ordered[i-1].name} and {ordered[i].name}: {gap} < {min_gap}")
            valid = False
    for p in ordered:
        if p.phase % phase_mod != ordered[0].phase % phase_mod:
            warnings.append(f"Phase mismatch on {p.name}: {p.phase} vs base phase {ordered[0].phase}")
            valid = False

    return ScheduleResult(ordered, warnings, valid)
