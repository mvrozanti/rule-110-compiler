"""
CTS executor that runs a Cook-aligned initial state and extracts output
from the evolved CTS queue (not fixed offsets).
"""

from typing import Dict, List, Optional, Tuple

from cook_cts_encoder import CTSSpec, encode_cts
from rule110 import DynamicRule110


def run_cts(cts: CTSSpec, steps: int = 400, output_window: Optional[Tuple[int, int]] = None) -> Dict[str, object]:
    """
    Execute a CTS program using dynamic Rule 110 and return evolution + output.

    Args:
        cts: CTS specification.
        steps: Number of evolution steps.
        output_window: Optional (start, end) window to read output bits.
    """
    encoding = encode_cts(cts)
    initial_tape = encoding.initial_state if hasattr(encoding, "initial_state") else encoding
    ca = DynamicRule110(initial_tape, boundary="ether")
    ca.run(steps)

    history = ca.get_history()
    final_state = history[-1]
    output_bits = extract_output(final_state, output_window)

    return {
        "history": history,
        "final_state": final_state,
        "output_bits": output_bits,
        "initial_state": initial_tape,
        "warnings": getattr(encoding, "schedule_warnings", []),
    }


def extract_output(state: List[int], window: Optional[Tuple[int, int]] = None) -> List[int]:
    """
    Extract output from a final state by reading a window around active cells.
    """
    if window:
        start, end = window
        return state[start:end]

    # Auto-detect active region
    active_idxs = [i for i, b in enumerate(state) if b == 1]
    if not active_idxs:
        return []
    start = max(min(active_idxs) - 5, 0)
    end = min(max(active_idxs) + 6, len(state))
    return state[start:end]
