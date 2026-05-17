"""End-to-end verifier: runs each phase's test and reports status.

Honest accounting of what works and what doesn't. Exit code 0 only if every
verified-claimed phase still passes its test. The 'not yet verified' section
lists what is still in progress and what is blocking it.

Usage:
    nix develop --command python -m scripts.verify_all
"""

import subprocess
import sys


PHASES = [
    ("Phase 1: Rule 110 + ether",
     ["pytest", "tests/test_rule110.py", "tests/test_ether.py", "-q"]),
    ("Phase 2: Cook gliders (A, B, C, D, Ebar)",
     ["pytest", "tests/test_gliders.py", "-q"]),
    ("Phase 4: Pure CTS simulator",
     ["pytest", "tests/test_cts.py", "-q"]),
    ("Phase 5: Tag system + tag->CTS",
     ["pytest", "tests/test_tagsystem.py", "-q"]),
    ("Phase 5: TM -> aligned tag (Cook s2.1)",
     ["pytest", "tests/test_tm_to_tagsystem.py", "-q"]),
    ("Phase 5: aligned tag -> CTS (Cook s2.2)",
     ["pytest", "tests/test_aligned_to_cts.py", "-q"]),
    ("Phase 5: end-to-end BF -> TM -> tag -> CTS chain",
     ["pytest", "tests/test_chain_bf_to_cts.py", "-q"]),
    ("Phase 6: BF parser + BF->TM lowering",
     ["pytest", "tests/test_bf_to_tm.py", "-q"]),
    ("Phase 8: Viz parity (gliders.js mirrors gliders.py)",
     ["pytest", "tests/test_viz_parity.py", "-q"]),
]

NOT_YET = [
    "Phase 2: Cook glider E (15, -4) -- 5/6 verified; E shares velocity "
    "with Ebar and was not isolated in 2000-seed random-IC sweep nor in "
    "2-glider collision sweeps at widths up to 18.",
    "Phase 3: verified collision table -- scripts/collide.py sandbox lands "
    "but the documented Cook collisions are not yet encoded as test fixtures.",
    "Phase 4: cts_to_r110.py encoder -- needs phase 3 collisions plus a "
    "set of CTS-encoding gliders placed at Cook ether-distances.",
    "Phase 5: tm_to_tagsystem on non-zero initial tape -- currently xfailed; "
    "needs more careful alignment tracking through L/R pair processing.",
    "Phase 5: multi-cell BF -> 2-symbol TM -- compile_bf produces 8-symbol "
    "TMs; Cook s2.1 needs 2-symbol input. Hand-mapping works for trivial "
    "programs (test_chain_bf_to_cts uses bf '+'). A unary-encoding pass "
    "would unblock all BF programs.",
    "Phase 7: end-to-end BF -> R110 -- blocked on phase 2 (E) / 3 / 4.",
    "Phase 8: cross-layer hover linking in viz -- region_map from compile-"
    "time would let hover on any pane highlight the corresponding cells in "
    "the others. Blocked on phase 4 emitting the region_map.",
]


def run_phase(name, cmd):
    print(f"\n{'='*64}\n{name}\n{'='*64}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout[-1200:] if result.stdout else "(no stdout)")
    if result.returncode != 0:
        print(f"STDERR:\n{result.stderr[-600:]}")
    return result.returncode == 0


def main():
    results = []
    for name, cmd in PHASES:
        ok = run_phase(name, cmd)
        results.append((name, ok))

    print(f"\n{'='*64}\nVerified-phase summary\n{'='*64}")
    for name, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}]  {name}")

    print(f"\n{'='*64}\nNot yet verified\n{'='*64}")
    for item in NOT_YET:
        print(f"  - {item}")

    all_ok = all(ok for _, ok in results)
    print(f"\nResult: {'GREEN (all verified phases pass)' if all_ok else 'RED (regression in verified phase)'}")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
