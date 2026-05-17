"""Cook (2004) §2.1 reduction: 2-symbol Turing machine to 2-tag system.

Tape encoding: TL = number formed by tape cells LEFT of head (less significant
bits closer to head); TR = number formed by tape cells RIGHT of head. So a
binary tape `... 0 1 1 | 0 1 ...` with head at the `|` gives TL=110_2=6,
TR=10_2=2 (head bit not included in either).

Tag tape:  H_{k1} H_{k0} [L_{k1} L_{k0}]^TL [R_{k1} R_{k0}]^TR
           (canonical form; the k1-first ordering is a convention. The actual
            "read" parity is tracked by `use_offset` in AlignedTagSystem.)

Productions for transition (state k, read bit z) → (state k', write bit z',
direction d ∈ {L, R}):

    H_{kz}   → [R_{k'*} R_{k'*}]^a [H_{k'}]^b H_{k'} [L_{k'} L_{k'}]^c
    L_{kz}   → L_{k'} [L_{k'} L_{k'} L_{k'}]^d
    R_{kz}   → R_{k'} [R_{k'} R_{k'} R_{k'}]^e

    a = 1 if d=L and z'=1, else 0
    b = 1 if z=0, else 0
    c = 1 if d=R and z'=1, else 0
    d = 1 if d=R, else 0    (this 'd' shadows the direction; here it's the
                              counter inside the L_{kz} formula)
    e = 1 if d=L, else 0

Auxiliary productions (no transition dependence):
    R_{k*} → R_k R_k
    H_k    → H_{k1} H_{k0}
    L_k    → L_{k1} L_{k0}
    R_k    → R_{k1} R_{k0}

A halt is a state k whose entries (k, 0) and (k, 1) have no transition. Such
states get NO H_{kz}, L_{kz}, R_{kz} productions (the tag system halts when
the leading pair's `used` symbol has no production).

For input: a TM with alphabet ⊆ {0, 1}, directions ∈ {L, R, S} (we eliminate
S by inserting an aux state that performs R then L).
"""

from dataclasses import dataclass

from compiler.aligned_tagsystem import AlignedTagSystem
from compiler.tm import TM


def _normalize_directions(tm: TM) -> TM:
    new_trans: dict[tuple[str, int], tuple[str, int, str]] = {}
    aux_counter = 0
    alphabet = {tm.blank}
    for (_, sym), (_, w, _) in tm.transitions.items():
        alphabet.add(sym); alphabet.add(w)
    for (state, sym), (new_state, write, direction) in tm.transitions.items():
        if direction in ("L", "R"):
            new_trans[(state, sym)] = (new_state, write, direction)
        elif direction == "S":
            aux = f"_s_{state}_{sym}_{aux_counter}"
            aux_counter += 1
            new_trans[(state, sym)] = (aux, write, "R")
            for s in alphabet:
                new_trans[(aux, s)] = (new_state, s, "L")
        else:
            raise ValueError(f"unknown direction {direction!r}")
    return TM(
        transitions=new_trans,
        initial_state=tm.initial_state,
        initial_tape=tm.initial_tape,
        initial_head=tm.initial_head,
        blank=tm.blank,
    )


def _fill_undefined_with_halt(tm: TM) -> TM:
    """For Cook §2.1: every non-halt state must have transitions for both
    z=0 and z=1, and both must go to the SAME new state (so that the L/R
    pair processing produces L_{k'}/R_{k'} consistently regardless of
    which subscript is read after alignment flips).

    Strategy: collect all states. For each state with at least one defined
    transition, find the new_state and direction of any defined (k, z).
    For the other z, synthesize (k, z) -> (same_new_state, z, same_direction).
    The synthesized transition writes back the read bit (z' = z) so it
    causes no tape change if ever actually hit, and it preserves k' so the
    tag-system encoding stays consistent across alignment flips.
    """
    states_used = {tm.initial_state}
    for (s, _), (ns, _, _) in tm.transitions.items():
        states_used.add(s)
        states_used.add(ns)

    new_trans = dict(tm.transitions)
    for k in states_used:
        defined_z = [z for z in (0, 1) if (k, z) in new_trans]
        if not defined_z:
            continue
        existing_new_state, _, existing_direction = new_trans[(k, defined_z[0])]
        for z in (0, 1):
            if (k, z) not in new_trans:
                new_trans[(k, z)] = (existing_new_state, z, existing_direction)
    return TM(
        transitions=new_trans,
        initial_state=tm.initial_state,
        initial_tape=tm.initial_tape,
        initial_head=tm.initial_head,
        blank=tm.blank,
    )


def _states_in(tm: TM) -> set[str]:
    s = {tm.initial_state}
    for (st, _), (ns, _, _) in tm.transitions.items():
        s.add(st); s.add(ns)
    return s


def _h(state: str, z: int | None = None) -> str:
    return f"H_{state}_{z}" if z is not None else f"H_{state}"


def _l(state: str, z: int | None = None) -> str:
    return f"L_{state}_{z}" if z is not None else f"L_{state}"


def _r(state: str, z: int | None = None) -> str:
    return f"R_{state}_{z}" if z is not None else f"R_{state}"


def _r_star(state: str) -> str:
    return f"R_{state}_*"


def build_aligned_tag(tm: TM) -> AlignedTagSystem:
    tm = _normalize_directions(tm)
    tm = _fill_undefined_with_halt(tm)
    states = _states_in(tm)
    alphabet = {0, 1}
    for sym in {tm.blank}:
        alphabet.discard(sym)
        if sym in (0, 1):
            alphabet.add(sym)
    alphabet = {0, 1}

    productions: dict[str, tuple[str, ...]] = {}

    for k in states:
        productions[_h(k)] = (_h(k, 1), _h(k, 0))
        productions[_l(k)] = (_l(k, 1), _l(k, 0))
        productions[_r(k)] = (_r(k, 1), _r(k, 0))
        productions[_r_star(k)] = (_r(k), _r(k))

        for z in (0, 1):
            if (k, z) not in tm.transitions:
                continue
            new_state, write, direction = tm.transitions[(k, z)]
            a = 1 if (direction == "L" and write == 1) else 0
            b = 1 if z == 0 else 0
            c = 1 if (direction == "R" and write == 1) else 0
            d_yes = 1 if direction == "R" else 0
            e_yes = 1 if direction == "L" else 0

            h_body: list[str] = []
            for _ in range(a):
                h_body.extend([_r_star(new_state), _r_star(new_state)])
            for _ in range(b):
                h_body.append(_h(new_state))
            h_body.append(_h(new_state))
            for _ in range(c):
                h_body.extend([_l(new_state), _l(new_state)])
            productions[_h(k, z)] = tuple(h_body)

            l_body = [_l(new_state)] + [_l(new_state)] * (3 * d_yes)
            productions[_l(k, z)] = tuple(l_body)

            r_body = [_r(new_state)] + [_r(new_state)] * (3 * e_yes)
            productions[_r(k, z)] = tuple(r_body)

    initial_state = tm.initial_state
    head_bit = 0
    if 0 <= tm.initial_head < len(tm.initial_tape):
        head_bit = tm.initial_tape[tm.initial_head]
    tl_bits = list(reversed(tm.initial_tape[:tm.initial_head]))
    tr_bits = list(tm.initial_tape[tm.initial_head + 1:])
    tl = sum(b << i for i, b in enumerate(tl_bits))
    tr = sum(b << i for i, b in enumerate(tr_bits))

    tape: list[str] = [_h(initial_state, 1), _h(initial_state, 0)]
    for _ in range(tl):
        tape.extend([_l(initial_state, 1), _l(initial_state, 0)])
    for _ in range(tr):
        tape.extend([_r(initial_state, 1), _r(initial_state, 0)])

    use_offset = 1 - head_bit
    return AlignedTagSystem(
        productions=productions,
        initial_tape=tuple(tape),
        initial_use_offset=use_offset,
    )


@dataclass(frozen=True)
class DecodedTagState:
    state: str
    head_bit: int
    tl: int
    tr: int


def decode_tape(tape: tuple[str, ...], use_offset: int) -> DecodedTagState | None:
    if len(tape) < 2:
        return None
    head_sym = tape[use_offset]
    if not head_sym.startswith("H_"):
        return None
    parts = head_sym.split("_")
    if len(parts) < 3:
        return None
    state = "_".join(parts[1:-1])
    z_str = parts[-1]
    if z_str not in ("0", "1"):
        return None
    head_bit = int(z_str)
    tl = 0
    tr = 0
    i = 2 + use_offset
    while i < len(tape) and tape[i].startswith(f"L_{state}_"):
        tl += 1
        i += 2
    while i < len(tape) and tape[i].startswith(f"R_{state}_"):
        tr += 1
        i += 2
    return DecodedTagState(state=state, head_bit=head_bit, tl=tl, tr=tr)
