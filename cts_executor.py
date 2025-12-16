"""Run CTS-encoded Rule 110 initial states and extract simple outputs."""
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict

from cook_cts_encoder import CTSSpec, encode_cts, default_unary_duplicator
from rule110 import Rule110


@dataclass
class CTSRunResult:
    history: List[List[int]]
    warnings: List[str]
    initial_state: List[int]
    spec: CTSSpec


def run_cts(spec: Optional[CTSSpec] = None, steps: int = 400, boundary: str = "ether") -> CTSRunResult:
    spec = spec or default_unary_duplicator()
    encoding = encode_cts(spec)
    ca = Rule110(encoding.initial_state, boundary=boundary)
    ca.run(steps)
    return CTSRunResult(
        history=ca.get_history(),
        warnings=encoding.schedule_warnings,
        initial_state=encoding.initial_state,
        spec=spec,
    )


def extract_queue_slice(history: List[List[int]], window: Tuple[int, int]) -> List[int]:
    start, end = window
    return [state[start:end] for state in history]


def active_counts(history: List[List[int]]) -> List[int]:
    """Return active (1-bit) counts per step for quick regression checks."""
    return [sum(state) for state in history]


def queue_window(history: List[List[int]], center: int, radius: int) -> List[List[int]]:
    """
    Extract a window around a center index across history.
    """
    start = max(center - radius, 0)
    end = center + radius
    return [state[start:end] for state in history]
