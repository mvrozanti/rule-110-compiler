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
    ("Phase 6: BF parser + BF->TM lowering",
     ["pytest", "tests/test_bf_to_tm.py", "-q"]),
    ("Phase 8: Viz parity (gliders.js mirrors gliders.py)",
     ["pytest", "tests/test_viz_parity.py", "-q"]),
]

NOT_YET = [
    "Phase 2: Cook glider E (15, -4) -- 5/6 verified; E shares velocity "
    "with Ebar and was not isolated in 2000-seed random-IC sweep nor in "
    "2-glider collision sweeps.",
    "Phase 3: collision table -- scripts/collide.py sandbox lands but the "
    "documented Cook collisions are not yet encoded as test fixtures.",
    "Phase 4: cts_to_r110.py encoder -- needs phase 3 collisions + a "
    "small set of CTS-encoding gliders placed at Cook ether-distances.",
    "Phase 5: tag_to_cts with alignment -- compiler/tagsystem_to_cts.py "
    "handles standard 1-tag; aligned 2-tag with use_offset metadata needs "
    "the 'pad with K Ns to shift alignment' trick from Cook s2.2.",
    "Phase 5: tm_to_tagsystem on non-zero initial tape -- currently xfailed; "
    "needs a transformation that fills undefined (k, z) transitions with "
    "synthesized ones to the same k', so that alignment-flips during L/R "
    "pair processing always find a valid production.",
    "Phase 7: end-to-end BF -> R110 -- blocked on phase 3 / 4 / 5.",
    "Phase 8: cross-layer linking in viz -- once tm_to_cts is online, the "
    "four panes can share a single t map.",
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
