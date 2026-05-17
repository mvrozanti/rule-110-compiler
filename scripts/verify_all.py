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
    ("Phase 3: empirical collision fixtures (C x Ebar crossing, parallels)",
     ["pytest", "tests/test_collisions.py", "-q"]),
    ("Phase 4: Pure CTS simulator",
     ["pytest", "tests/test_cts.py", "-q"]),
    ("Phase 4: CTS -> R110 state encoding round-trip",
     ["pytest", "tests/test_cts_to_r110.py", "-q"]),
    ("Phase 5: Tag system + tag->CTS",
     ["pytest", "tests/test_tagsystem.py", "-q"]),
    ("Phase 5: TM -> aligned tag (Cook s2.1)",
     ["pytest", "tests/test_tm_to_tagsystem.py", "-q"]),
    ("Phase 5: aligned tag -> CTS (Cook s2.2)",
     ["pytest", "tests/test_aligned_to_cts.py", "-q"]),
    ("Phase 5: end-to-end BF -> TM -> tag -> CTS chain",
     ["pytest", "tests/test_chain_bf_to_cts.py", "-q"]),
    ("Phase 6: BF parser + BF->TM lowering (8-symbol)",
     ["pytest", "tests/test_bf_to_tm.py", "-q"]),
    ("Phase 6: BF -> 2-symbol TM (Cook s2.1 input)",
     ["pytest", "tests/test_bf_to_2sym_tm.py", "-q"]),
    ("Phase 7: end-to-end BF -> R110 IC -> evolve -> decode round-trip",
     ["pytest", "tests/test_end_to_end.py", "-q"]),
    ("Phase 8: Viz parity (gliders.js mirrors gliders.py)",
     ["pytest", "tests/test_viz_parity.py", "-q"]),
]

NOT_YET = [
    "Phase 2: Cook glider E (15, -4) -- 5/6 verified; E shares velocity "
    "with Ebar and was not isolated by width-14 exhaustive sweep over all "
    "phases, the 2000-seed random-IC track, or 2-glider collision sweeps. "
    "Constrained width-19 popcount sweeps and long random-IC sweeps "
    "(scripts/exhaustive_e_search_constrained.py, scripts/long_random_e.py) "
    "are the next escalations.",
    "Phase 3: full Cook collision atlas -- four collisions verified as test "
    "fixtures (C x Ebar crossing, A-A/C-C/Ebar-Ebar parallels). The 30+ "
    "collisions Cook documents in s3.3-s3.5 (leaders firing, components "
    "accepted/rejected, ossifiers producing tape data) are still empirical "
    "open work.",
    "Phase 4: cts_to_r110.py executing CTS *steps* in R110 -- the encoder "
    "round-trips CTS state through R110, but appendant dynamics (Y "
    "consumes appendant + appends; N skips) still execute in Python. "
    "Closing this requires the full collision atlas (Phase 3).",
    "Phase 5: tm_to_tagsystem on non-zero initial tape -- currently xfailed; "
    "needs more careful alignment tracking through L/R pair processing.",
    "Phase 5: 2-symbol BF -> CTS chain on programs that aren't R-only TMs "
    "-- compile_bf_2sym is correct as a TM lowering, but the Cook s2.1 "
    "alignment math currently halts uncleanly when the TM uses S-normalised "
    "moves. A redesign that emits only L/R TMs (or a tag-system halt-state "
    "alignment fix) would unblock arbitrary BF programs through the chain.",
    "Phase 8: cross-layer hover linking in viz -- the encoder now emits a "
    "region_map; wiring it into viz/index.html for hover-linked highlights "
    "remains open.",
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
