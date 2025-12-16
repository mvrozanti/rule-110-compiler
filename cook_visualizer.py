"""
Lightweight long-run visualization for CTS/ether/glider integrity checks.
"""

from typing import List, Optional


def render_long_run(history: List[List[int]], step_stride: int = 5, max_rows: int = 200, window: Optional[slice] = None) -> List[str]:
    """
    Create a textual long-run view of the automaton.

    Args:
        history: Evolution history from DynamicRule110.run().
        step_stride: Sample every Nth step for readability.
        max_rows: Cap number of rendered rows.
        window: Optional slice to crop columns (e.g., slice(0, 120)).
    """
    if not history:
        return ["(no history)"]
    sampled = history[:: step_stride or 1][:max_rows]
    lines = []
    for idx, state in enumerate(sampled):
        step_num = idx * (step_stride or 1)
        view = state[window] if window else state
        line = "".join("█" if b else " " for b in view)
        lines.append(f"Step {step_num:4d}: {line}")
    return lines
