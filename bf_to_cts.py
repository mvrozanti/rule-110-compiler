"""
Brainfuck-to-CTS scaffold.

This is a minimal translator that maps Brainfuck instructions to CTS symbols
and emits a CTSSpec suitable for encoding. Semantics are not implemented; the
goal is to produce a well-formed CTS tape for regression wiring.
"""
from typing import List

from cook_cts_encoder import CTSSpec, CTSRule

# Map BF instructions to CTS symbols
BF_SYMBOLS = {
    ">": "R",
    "<": "L",
    "+": "P",
    "-": "M",
    ".": "O",
    ",": "I",
    "[": "B",
    "]": "E",
}


def compile_brainfuck(source: str, ether_length: int = 400, spacing: int = 14) -> CTSSpec:
    symbols: List[str] = [BF_SYMBOLS[c] for c in source if c in BF_SYMBOLS]
    if not symbols:
        symbols = ["P"]  # default nop-ish

    # Identity rules (no-op) to keep the CTS evolving structurally
    unique_syms = sorted(set(symbols))
    rules = [CTSRule(symbol=s, production=[s]) for s in unique_syms]

    symbol_map = {s: "A" if i % 2 == 0 else "B" for i, s in enumerate(unique_syms)}
    # Ensure delimiter uses DELIM
    return CTSSpec(
        queue=symbols,
        rules=rules,
        ether_length=ether_length,
        spacing=spacing,
        delimiter_package="DELIM",
        symbol_map=symbol_map,
    )
