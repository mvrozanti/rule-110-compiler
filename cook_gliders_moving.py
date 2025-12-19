"""
Moving glider package metadata (structure + placeholder bitstrings).

This module provides a single place to register measured glider packages and
their velocities/phase offsets. The current values mirror the static packages
from `cook_gliders.py` and should be replaced with empirically measured
Cook glider traces (bit patterns per phase).
"""
from dataclasses import dataclass
from typing import Dict, List

from cook_gliders import GLIDER_PACKAGES, PHASE_MOD


@dataclass
class MovingPackage:
    name: str
    bits: List[int]
    velocity: float  # cells per step
    phase: int       # phase offset modulo PHASE_MOD


# Placeholder moving packages; swap bits/velocity/phase with measured data.
MOVING_PACKAGES: Dict[str, MovingPackage] = {
    name: MovingPackage(name=name, bits=bits, velocity=0.5, phase=0)
    for name, bits in GLIDER_PACKAGES.items()
}


def get_moving_package(name: str) -> MovingPackage:
    return MOVING_PACKAGES[name]
