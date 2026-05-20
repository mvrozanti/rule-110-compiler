"""Generate a standard 8-bit BF program that simulates rule 110.

Prints N cells × K rows as '#'/'.' + '\\n' using zero boundary. Used by the
meta-recursion viz demo: this BF program, when loaded into the viz pipeline,
gets compiled to TM → CTS → R110 IC — so a rule110-simulating BF program is
itself encoded as a rule110 initial condition.

Tape layout (W=8 BF cells per CA cell):
  CA cell j at BF positions [8j .. 8j+7]
    slot 0 = v (current state)
    slot 1 = next (computed value, drained back to slot 0 in apply phase)
    slots 2..7 = scratch
  CA cells: 0 = left sentinel, 1..N = state, N+1 = right sentinel
  CA cell N+2: slot 0 = K-loop step counter

Cursor convention: between major ops, cursor sits at BF position 0
(cell 0 slot 0 = sentinel = always 0).
"""

W = 8


def cells(n: int) -> str:
    return ">" * (W * n) if n >= 0 else "<" * (W * (-n))


def gen(N: int = 8, K: int = 8, seed: list[int] | None = None) -> str:
    if seed is None:
        seed = [0] * N
        seed[N // 2] = 1
    assert len(seed) == N

    P: list[str] = []
    a = P.append

    # ---- INIT ----
    pos = 0
    for i, b in enumerate(seed):
        if b:
            tgt = i + 1
            a(cells(tgt - pos))
            a("+")
            pos = tgt
    a(cells((N + 2) - pos))
    a("+" * K)
    a(cells(-(N + 2)))

    # ---- K-LOOP ----
    a(cells(N + 2))
    a("[")
    a("-")
    a(cells(-(N + 2)))

    # PRINT ROW
    a(cells(1))
    for i in range(N):
        a("[->>+>+<<<]>>>[-<<<+>>>]<<<")
        a(">>>+<")
        a("[")
        a("-")
        a(">-<")
        a(">+++++[<+++++++>-]<.[-]")
        a("]")
        a(">")
        a("[")
        a("-")
        a(">++++++[<+++++++>-]<++++.[-]")
        a("]")
        a("<<<")
        if i < N - 1:
            a(cells(1))
    a(">++++++++++.[-]<")
    a(cells(-N))

    # COMPUTE NEXT
    a(cells(1))
    for i in range(N):
        a("[->>+>>+>+<<<<<]>>[-<<+>>]<<")
        a(cells(-1))
        a("[->>>>>>>+>>>+<<<<<<<<<<]")
        a(">>>>>>>[-<<<<<<<+>>>>>>>]<<<<<<<")
        a(cells(1))
        a(cells(1))
        a("[->+<<+<+>>]")
        a(">[-<+>]<")
        a(cells(-1))
        a(">>[->>[->>[-<<<+>>>]<<]<<]")
        a(">>[-]>>[-]<<<<")
        a(">>>[-<<<<+>>>>]")
        a(">>[-<<<<<<[-]+>>>>>>]")
        a("<<<<[-<<[-]>>]")
        a("<<<")
        if i < N - 1:
            a(cells(1))
    a(cells(-N))

    # APPLY: slot 0 = slot 1
    a(cells(1))
    for i in range(N):
        a("[-]>[-<+>]<")
        if i < N - 1:
            a(cells(1))
    a(cells(-N))

    a(cells(N + 2))
    a("]")
    return "".join(P)


if __name__ == "__main__":
    import sys
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    K = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    src = gen(N=N, K=K)
    print(src)
    print(f"\n# length: {len(src)} chars, N={N}, K={K}", file=sys.stderr)
