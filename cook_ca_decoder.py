"""
CA-to-CTS decoder helpers.

Given a CA state (one step of history), locate glider packages by pattern
matching and decode them back to CTS symbols using the encoder's symbol map.

Note: This decoder matches static package shapes; with full Cook glider motion
you would need phase-aware tracking. This is sufficient to validate initial
encodings and simple regression windows.
"""
from typing import Dict, List, Tuple, Optional

from cook_gliders import GLIDER_PACKAGES


def _hamming(a: List[int], b: List[int]) -> int:
    if len(a) != len(b):
        return max(len(a), len(b))
    return sum(1 for x, y in zip(a, b) if x != y)


def find_packages(state: List[int], patterns: Dict[str, List[int]], tolerance: int = 0) -> List[Tuple[str, int]]:
    """Return (name, offset) for patterns found in state with <= tolerance mismatches."""
    hits: List[Tuple[str, int]] = []
    n = len(state)
    for name, pat in patterns.items():
        m = len(pat)
        for i in range(0, n - m + 1):
            window = state[i : i + m]
            if _hamming(window, pat) <= tolerance:
                hits.append((name, i))
    hits.sort(key=lambda x: x[1])
    return hits


def decode_queue_from_state(state: List[int], symbol_map: Dict[str, str], tolerance: int = 0) -> List[str]:
    """
    Decode a CTS queue from a CA state by matching package patterns.

    The symbol_map maps symbols to package names; we invert it to map packages
    back to symbols. If multiple symbols share a package, the first encountered
    is used.
    """
    inv_map: Dict[str, str] = {}
    for sym, pkg in symbol_map.items():
        inv_map.setdefault(pkg, sym)

    placements = find_packages(state, GLIDER_PACKAGES, tolerance=tolerance)
    decoded: List[str] = []
    for name, _ in placements:
        sym = inv_map.get(name)
        if sym:
            decoded.append(sym)
    return decoded


def decode_history(
    history: List[List[int]],
    symbol_map: Dict[str, str],
    window: Optional[Tuple[int, int]] = None,
    tolerance: int = 0,
) -> List[List[str]]:
    """
    Decode all steps in a history to symbol queues using a windowed region.
    """
    decoded_steps: List[List[str]] = []
    for state in history:
        region = state[slice(*window)] if window else state
        decoded_steps.append(decode_queue_from_state(region, symbol_map, tolerance=tolerance))
    return decoded_steps
