"""Lower a Brainfuck AST into a 2-symbol Turing machine.

This is the entrypoint Cook §2.1 (compiler/tm_to_tagsystem.py) expects: a TM
whose alphabet is exactly {0, 1}. The 8-symbol TM produced by
compiler/bf_to_tm.py is correct but cannot feed Cook §2.1 directly.

Scope: BF programs whose cell values stay in {0, 1}. This is the natural
binary subset and is sufficient for `+`, `>+`, `+[-]`, `+[->+<]` on a
zero-initial tape (each cell either stays 0 or toggles once between 0 and 1).
Outside this subset, `+` past 1 wraps to 0 with no error: the reference
interpreter in compiler/bf_to_tm uses CELL_MAX=7, so this lowering is a
strictly narrower domain than the 8-symbol one. The chain still runs end-to-
end on the supported subset.

Encoding:
  - Tape symbol is the BF cell value itself, in {0, 1}.
  - TM head position equals BF data pointer.
  - Each BF instruction lowers to a small bundle of TM transitions keyed on
    the read bit, parameterized by program-counter index.

States: `q{i}_<role>` where i is the flattened-AST instruction index. Halt
state is `qhalt`.
"""

from compiler.bf import Dec, Get, Inc, Left, Loop, Node, Put, Right
from compiler.bf_to_tm import _flatten_with_pcs, _loop_pairs
from compiler.tm import TM, Transition


HALT = "qhalt"


def _state(pc: int) -> str:
    return f"q{pc}"


def compile_bf_2sym(source_or_ast, initial_tape: tuple[int, ...] = ()) -> TM:
    from compiler.bf import parse as _parse
    if isinstance(source_or_ast, str):
        ast = _parse(source_or_ast)
    else:
        ast = source_or_ast

    flat, total = _flatten_with_pcs(ast)
    pairs = _loop_pairs(flat)

    def next_pc_state(pc: int) -> str:
        for q, _ in flat:
            if q > pc:
                return _state(q)
        return HALT

    transitions: dict[tuple[str, int], Transition] = {}

    for pc, node in flat:
        s = _state(pc)
        nxt = next_pc_state(pc)

        if isinstance(node, Inc):
            transitions[(s, 0)] = (nxt, 1, "S")
            transitions[(s, 1)] = (nxt, 0, "S")
        elif isinstance(node, Dec):
            transitions[(s, 0)] = (nxt, 1, "S")
            transitions[(s, 1)] = (nxt, 0, "S")
        elif isinstance(node, Right):
            for v in (0, 1):
                transitions[(s, v)] = (nxt, v, "R")
        elif isinstance(node, Left):
            for v in (0, 1):
                transitions[(s, v)] = (nxt, v, "L")
        elif isinstance(node, (Put, Get)):
            for v in (0, 1):
                transitions[(s, v)] = (nxt, v, "S")
        elif isinstance(node, Loop):
            close_pc = pairs[pc]
            after_close = next_pc_state(close_pc)
            body_first = next_pc_state(pc)
            transitions[(s, 0)] = (after_close, 0, "S")
            transitions[(s, 1)] = (body_first, 1, "S")
        elif node == "ENDLOOP":
            open_pc = pairs[pc]
            for v in (0, 1):
                transitions[(s, v)] = (_state(open_pc), v, "S")

    if total == 0:
        initial_state = HALT
    else:
        initial_state = _state(0)

    return TM(
        transitions=transitions,
        initial_state=initial_state,
        initial_tape=initial_tape,
        initial_head=0,
        blank=0,
    )


def run_bf_2sym_reference(source_or_ast, tape_size: int = 16, max_ops: int = 100_000) -> dict[int, int]:
    """Reference BF interpreter restricted to {0, 1} cells (wrap modulo 2).

    Used for parity testing the 2-symbol TM lowering. Programs that would
    exceed cell value 1 are silently wrapped here too, so the parity test
    measures equivalence under the chosen encoding.
    """
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
                cells[dp] = (cells[dp] + 1) % 2
            elif isinstance(node, Dec):
                cells[dp] = (cells[dp] - 1) % 2
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
