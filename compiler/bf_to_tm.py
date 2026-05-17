"""Lower a Brainfuck AST into a Turing machine.

Encoding (MVP-B):
  - Tape alphabet: {0, 1, ..., CELL_MAX} where CELL_MAX is the largest cell
    value the program may produce. Default CELL_MAX = 7 (3-bit wrap), sufficient
    for `+++`, `+++[-]`, and similar small programs.
  - Each BF cell is one TM cell at the same tape position. TM head at position
    `p` is BF data pointer at cell `p`.
  - Each BF instruction maps to a fixed bundle of TM transitions parameterised
    by the instruction's program-counter index.

States are named `pc{i}_<role>` where `i` is the BF-AST instruction index
(flattened pre-order traversal) and `<role>` is `enter`, `inc_w<v>`, etc.
The state `halt` is the unique terminal state; no transitions leave it.

Loops compile to conditional branches at `[`: if the head reads 0 (cell is
zero), jump to the state immediately after the matching `]`; otherwise enter
the body. `]` jumps unconditionally back to `[`.
"""

from compiler.bf import Dec, Get, Inc, Left, Loop, Node, Put, Right
from compiler.tm import TM, Transition

CELL_MAX = 7
ALPHABET = tuple(range(CELL_MAX + 1))


def _flatten_with_pcs(ast: tuple[Node, ...], pc: int = 0) -> tuple[list[tuple[int, Node]], int]:
    out: list[tuple[int, Node]] = []
    cur = pc
    for node in ast:
        out.append((cur, node))
        cur += 1
        if isinstance(node, Loop):
            inner, cur = _flatten_with_pcs(node.body, cur)
            out.extend(inner)
            out.append((cur, "ENDLOOP"))
            cur += 1
    return out, cur


def _loop_pairs(flat: list[tuple[int, object]]) -> dict[int, int]:
    stack: list[int] = []
    pairs: dict[int, int] = {}
    for pc, node in flat:
        if isinstance(node, Loop):
            stack.append(pc)
        elif node == "ENDLOOP":
            open_pc = stack.pop()
            pairs[open_pc] = pc
            pairs[pc] = open_pc
    if stack:
        raise ValueError("unclosed loop in flatten")
    return pairs


def _state(pc: int, role: str = "enter") -> str:
    return f"pc{pc}_{role}"


def compile_bf(source_or_ast, initial_tape: tuple[int, ...] = ()) -> TM:
    from compiler.bf import parse as _parse
    if isinstance(source_or_ast, str):
        ast = _parse(source_or_ast)
    else:
        ast = source_or_ast

    flat, total = _flatten_with_pcs(ast)
    pairs = _loop_pairs(flat)
    halt_state = "halt"
    after_last = _state(total, "enter") if total else halt_state

    def next_pc_state(pc: int) -> str:
        for q, _ in flat:
            if q > pc:
                return _state(q, "enter")
        return halt_state

    transitions: dict[tuple[str, int], Transition] = {}

    for pc, node in flat:
        s = _state(pc, "enter")
        nxt = next_pc_state(pc)

        if isinstance(node, Inc):
            for v in ALPHABET:
                transitions[(s, v)] = (nxt, (v + 1) % (CELL_MAX + 1), "S")
        elif isinstance(node, Dec):
            for v in ALPHABET:
                transitions[(s, v)] = (nxt, (v - 1) % (CELL_MAX + 1), "S")
        elif isinstance(node, Right):
            for v in ALPHABET:
                transitions[(s, v)] = (nxt, v, "R")
        elif isinstance(node, Left):
            for v in ALPHABET:
                transitions[(s, v)] = (nxt, v, "L")
        elif isinstance(node, (Put, Get)):
            for v in ALPHABET:
                transitions[(s, v)] = (nxt, v, "S")
        elif isinstance(node, Loop):
            after_close_pc = pairs[pc]
            after_close = next_pc_state(after_close_pc)
            for v in ALPHABET:
                if v == 0:
                    transitions[(s, v)] = (after_close, v, "S")
                else:
                    body_first = next_pc_state(pc)
                    transitions[(s, v)] = (body_first, v, "S")
        elif node == "ENDLOOP":
            open_pc = pairs[pc]
            for v in ALPHABET:
                transitions[(s, v)] = (_state(open_pc, "enter"), v, "S")

    return TM(
        transitions=transitions,
        initial_state=_state(0, "enter") if flat else halt_state,
        initial_tape=initial_tape,
        initial_head=0,
        blank=0,
    )


def run_bf_reference(source_or_ast, tape_size: int = 32, max_ops: int = 100_000) -> dict[int, int]:
    """Reference interpreter for parity testing against compile_bf + TM run."""
    from compiler.bf import parse as _parse
    if isinstance(source_or_ast, str):
        ast = _parse(source_or_ast)
    else:
        ast = source_or_ast

    cells = [0] * tape_size
    dp = 0
    ops = 0

    def execute(nodes: tuple[Node, ...]) -> None:
        nonlocal dp, ops
        for node in nodes:
            ops += 1
            if ops > max_ops:
                raise RuntimeError("BF reference exceeded max_ops")
            if isinstance(node, Inc):
                cells[dp] = (cells[dp] + 1) % (CELL_MAX + 1)
            elif isinstance(node, Dec):
                cells[dp] = (cells[dp] - 1) % (CELL_MAX + 1)
            elif isinstance(node, Right):
                dp += 1
            elif isinstance(node, Left):
                dp -= 1
            elif isinstance(node, Loop):
                while cells[dp] != 0:
                    execute(node.body)
                    ops += 1
            elif isinstance(node, (Put, Get)):
                pass

    execute(ast)
    return {i: v for i, v in enumerate(cells) if v != 0}
