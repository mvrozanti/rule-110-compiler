#!/usr/bin/env python3
"""
CTS-first CLI visualizer for Cook-style runs.
"""

import sys
import argparse
from typing import List, Optional

from cts_executor import run_cts


def render_state(state: List[int]) -> str:
    return "".join("█" if b else " " for b in state)


def print_long_run(history: List[List[int]], step_stride: int = 5, window: Optional[slice] = None, max_rows: int = 200):
    """
    Print a sampled long-run view (useful for ether/glider integrity checks).
    """
    if not history:
        print("(no history)")
        return
    sampled = history[:: step_stride or 1][:max_rows]
    for idx, state in enumerate(sampled):
        step_num = idx * (step_stride or 1)
        view = state[window] if window else state
        line = render_state(view)
        print(f"Step {step_num:4d}: {line}")


def main():
    parser = argparse.ArgumentParser(
        description="Run a Cook CTS demo and print a sampled evolution."
    )
    parser.add_argument("-s", "--steps", type=int, default=400, help="Number of steps to run.")
    parser.add_argument("--stride", type=int, default=5, help="Sampling stride for printing.")
    parser.add_argument("--window", type=str, default=None, help="Slice window start:end for printing.")
    args = parser.parse_args()

    # Run default CTS (unary duplicator) using ether boundaries.
    result = run_cts(steps=args.steps, boundary="ether")

    window = None
    if args.window:
        try:
            start_str, end_str = args.window.split(":")
            start = int(start_str) if start_str else None
            end = int(end_str) if end_str else None
            window = slice(start, end)
        except Exception:
            print("Invalid window slice; expected start:end", file=sys.stderr)

    print("CTS run (default unary duplicator)")
    if result.warnings:
        print("Warnings:")
        for w in result.warnings:
            print(f"- {w}")
    print(f"Initial length: {len(result.initial_state)}")
    print_long_run(result.history, step_stride=args.stride, window=window)


if __name__ == "__main__":
    sys.exit(main())
