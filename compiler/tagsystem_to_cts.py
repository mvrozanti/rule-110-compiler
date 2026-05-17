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


def build_cts_from_aligned(ats) -> tuple[CTSSpec, dict[str, int], int]:
    """Cook §2.2 for 2-tag: 2k appendants (first k real, second k empty).

    Halt symbols (those without a production in the tag system) get an
    empty appendant in the CTS too; the CTS will keep consuming their
    encoded bits without producing, and the CTS halts on empty tape.

    When the 2-tag is aligned with use_offset = 1, prepend k N bits to the
    CTS initial tape. The CTS cursor advances by k while reading those Ns
    (no Ys, nothing fires), landing on the start of the empty half. The
    first real tag symbol's encoding then fires an EMPTY appendant
    (ignored), and the second tag symbol fires a real one (used). This
    mirrors the 2-tag "use the second symbol of each pair" semantics.

    Returns (cts_spec, symbol_index, prefix_n_count).
    """
    all_syms: set[str] = set(ats.productions.keys()) | set(ats.initial_tape)
    for app in ats.productions.values():
        all_syms.update(app)

    ordered = sorted(all_syms)
    k = len(ordered)
    symbol_index = {s: i for i, s in enumerate(ordered)}

    encoded_appendants: list[tuple[str, ...]] = []
    for s in ordered:
        prod = ats.productions.get(s, ())
        encoded = encode_string(prod, symbol_index, k)
        encoded_appendants.append(encoded)

    all_appendants: list[tuple[str, ...]] = list(encoded_appendants) + [() for _ in range(k)]

    initial = list(encode_string(ats.initial_tape, symbol_index, k))
    if ats.initial_use_offset == 1:
        initial = ["N"] * k + initial

    return (
        CTSSpec(appendants=tuple(all_appendants), initial_tape=tuple(initial)),
        symbol_index,
        k * ats.initial_use_offset,
    )


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
