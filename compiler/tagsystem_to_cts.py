"""Reduce a 2-tag system to a cyclic tag system (Cook 2004 §2.2).

Encoding: number the K tag-system symbols 1..K. Each tag symbol i becomes a
length-K binary string with Y at position i and N elsewhere.

CTS appendants list: for each tag symbol i (in fixed order), the encoded form
of the tag-system production for symbol i, padded if necessary so the cyclic
schedule aligns. Specifically: between any two real appendants we insert K-1
empty appendants (N-strings of length K) so each real appendant is reached
exactly when the encoded symbol for tag symbol i is the leading bit on the
tape.

The CTS reads one bit per step; the K-bit encoding of a tag symbol takes K
CTS steps. Of those K, exactly one Y triggers an append (the i-th step for
tag symbol i). The other K-1 N-bits cycle the CTS cursor through positions
where we placed empty appendants, so no spurious appends happen.

Reference: Cook 2004 §2.2; standard construction.
"""

from compiler.cts import CTSSpec
from compiler.tagsystem import TagSystem


def encode_symbol(index: int, k: int) -> tuple[str, ...]:
    return tuple("Y" if j == index else "N" for j in range(k))


def encode_string(symbols: tuple[str, ...], symbol_index: dict[str, int], k: int) -> tuple[str, ...]:
    out: list[str] = []
    for s in symbols:
        out.extend(encode_symbol(symbol_index[s], k))
    return tuple(out)


def build_cts(ts: TagSystem) -> tuple[CTSSpec, dict[str, int]]:
    ordered_symbols = sorted(ts.productions.keys())
    k = len(ordered_symbols)
    symbol_index = {s: i for i, s in enumerate(ordered_symbols)}

    appendants: list[tuple[str, ...]] = []
    for s in ordered_symbols:
        prod = ts.productions[s]
        encoded = encode_string(prod, symbol_index, k)
        appendants.append(encoded)

    cts_appendants: list[tuple[str, ...]] = []
    for app in appendants:
        cts_appendants.append(app)

    initial = encode_string(ts.initial_tape, symbol_index, k)
    return CTSSpec(appendants=tuple(cts_appendants), initial_tape=initial), symbol_index


def decode_tape(cts_tape: tuple[str, ...], symbol_index: dict[str, int]) -> tuple[str, ...]:
    k = len(symbol_index)
    inv = {i: s for s, i in symbol_index.items()}
    out: list[str] = []
    for start in range(0, len(cts_tape) - k + 1, k):
        block = cts_tape[start:start + k]
        ys = [j for j, c in enumerate(block) if c == "Y"]
        if len(ys) != 1:
            continue
        out.append(inv[ys[0]])
    return tuple(out)
