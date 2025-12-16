"""Spacing and phase scheduler for Cook-style glider packages."""
from dataclasses import dataclass
from typing import List, Tuple

from cook_gliders import PackagePlacement, ETHER_BASE, PHASE_MOD, max_package_len, GLIDER_PACKAGES

# Minimal safe gap between packages (heuristic; Cook spacing is phase-sensitive).
MIN_SPACING = max_package_len()


@dataclass
class ScheduleResult:
    placements: List[PackagePlacement]
    warnings: List[str]
    valid: bool


def schedule_packages(packages: List[PackagePlacement], min_gap: int = MIN_SPACING, phase_mod: int = None, strict: bool = True) -> ScheduleResult:
    """
    Ensure package ordering, spacing, and (optionally) phase alignment.

    Args:
        packages: placements with desired offsets
        min_gap: minimal cell gap between consecutive packages (after package length)
        phase_mod: optional modulus for phase consistency (defaults to ether period)
        strict: if True, invalid spacing/phase marks schedule invalid
    """
    warnings: List[str] = []
    if not packages:
        return ScheduleResult([], ["No packages supplied"], False)

    phase_mod = phase_mod or PHASE_MOD
    ordered = sorted(packages, key=lambda p: p.offset)
    valid = True

    for i in range(1, len(ordered)):
        prev = ordered[i - 1]
        curr = ordered[i]
        prev_len = len(GLIDER_PACKAGES.get(prev.name, []))
        curr_len = len(GLIDER_PACKAGES.get(curr.name, []))
        prev_end = prev.offset + max(prev_len, 1) - 1
        gap = curr.offset - prev_end - 1
        if gap < min_gap:
            warnings.append(
                f"Gap too small between {prev.name} (end {prev_end}) and {curr.name} (start {curr.offset}): {gap} < {min_gap}"
            )
            valid = False
    for p in ordered:
        if p.phase % phase_mod != ordered[0].phase % phase_mod:
            warnings.append(f"Phase mismatch on {p.name}: {p.phase} vs base phase {ordered[0].phase}")
            valid = False

    if strict and not valid:
        warnings.append("Schedule marked invalid under strict mode.")

    return ScheduleResult(ordered, warnings, valid)
