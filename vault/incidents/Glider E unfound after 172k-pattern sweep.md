---
type: incident
era: side-projects
tags: [rule-110, cook, glider, search, e]
date: 2026-05-17
---

# Glider E unfound after 172k-pattern sweep

Cook Figure 5 lists glider E at period **(15, −4)**, width `11 + 8n`. Shares velocity with Ē (−8/30 = −4/15). [[Cook universality proof|Cook's construction]] can avoid E (uses C / Ē / A primarily), but completing the catalogue would close the [[Cook-faithful glider catalogue]].

What was tried:
- 2000-seed random-IC track sweep — found A/B/C/D/Ē in isolation; E never appeared.
- 2-glider collision sweeps across all (A/B/C/D/Ē) pairs at varying offsets — no E among the products.
- Width-14 exhaustive bitmask sweep across all 14 ether phases (~172k candidate patterns) with strict ether-halo verification (`scripts/exhaustive_e_search.py`) — **zero hits**.
- Width-19 popcount-constrained sweep (Cook's natural E₁ extent), ~3.6M candidates, partial — launched but stopped at ~200k for downstream compute.
- Long random-IC sweeps with strict period-15 vs period-30 disambiguation (`scripts/long_random_e.py`).

Why E is hard: velocity overlaps Ē so the tracker biases toward whichever is checked first; natural width ≥ 19 cells exceeds the small-window phase-space; rare in random ICs.

> [!status]
> Open. The [[Cook universality proof|Cook construction]] does not require E for the C/Ē/A-primary CTS encoding, so this is a catalogue gap rather than a blocker for the [[Rule 110 compiler]] end goal.

## Connects to

- [[Cook-faithful glider catalogue]]
- [[Cook ether lattice]]
- [[Rule 110 compiler]]
