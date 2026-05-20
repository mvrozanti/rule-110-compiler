import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from compiler.bf import run_bf_byte
from core.rule110 import step

SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from gen_rule110_bf import gen


def _render(row):
    return "".join("#" if c else "." for c in row) + "\n"


def _oracle(N, K, seed):
    state = tuple(seed)
    rows = []
    for _ in range(K):
        rows.append(_render(state))
        state = step(state, boundary="zero")
    return "".join(rows)


def test_rule110_in_bf_default_seed():
    N, K = 8, 8
    src = gen(N=N, K=K)
    out = run_bf_byte(src, max_ops=50_000_000).decode("ascii")
    seed = [0] * N
    seed[N // 2] = 1
    expected = _oracle(N, K, seed)
    assert out == expected, f"\n--- BF ---\n{out}--- ORACLE ---\n{expected}"


def test_rule110_in_bf_custom_seeds():
    seeds = [
        [0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 1, 0, 1, 0, 1],
    ]
    for s in seeds:
        N, K = 8, 6
        src = gen(N=N, K=K, seed=s)
        out = run_bf_byte(src, max_ops=50_000_000).decode("ascii")
        expected = _oracle(N, K, s)
        assert out == expected, f"seed={s}\n--- BF ---\n{out}--- ORACLE ---\n{expected}"


if __name__ == "__main__":
    test_rule110_in_bf_default_seed()
    test_rule110_in_bf_custom_seeds()
    print("ok")
