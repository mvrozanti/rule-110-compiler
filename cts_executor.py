"""Run CTS-encoded Rule 110 initial states and extract simple outputs."""
from dataclasses import dataclass
from typing import List, Tuple, Optional

from cook_cts_encoder import CTSSpec, encode_cts, default_unary_duplicator
from rule110 import Rule110


@dataclass
class CTSRunResult:
    history: List[List[int]]
    warnings: List[str]
    initial_state: List[int]


def run_cts(spec: Optional[CTSSpec] = None, steps: int = 400, boundary: str = "ether") -> CTSRunResult:
    spec = spec or default_unary_duplicator()
    encoding = encode_cts(spec)
    ca = Rule110(encoding.initial_state, boundary=boundary)
    ca.run(steps)
    return CTSRunResult(history=ca.get_history(), warnings=encoding.schedule_warnings, initial_state=encoding.initial_state)


def extract_queue_slice(history: List[List[int]], window: Tuple[int, int]) -> List[int]:
    start, end = window
    return [state[start:end] for state in history]
