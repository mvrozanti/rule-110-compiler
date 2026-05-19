---
type: concept
era: side-projects
tags: [rule-110, cook, glider, catalogue]
date: 2026-05
---

# Cook-faithful glider catalogue

`core/cook_gliders.py` in the [[Rule 110 compiler]]: three Cook-faithful glider variants discovered empirically via `scripts/find_cook_variants.py`.

- **A**: period (3, +2), [[Cook glider width|width 6]], left_phase 4, delta `(1, 0, 1, 1, 1, 0)`.
- **C2**: period (7, 0), width 3, left_phase 2, delta `(1, 0, 0, 0, 0, 0)`. Cook's tape-data glider.
- **Ē (Ebar)**: period (30, −8), width 7, left_phase 4, delta `(1, 1, 0, 0, 1, 1, 1)`. Cook's moving-data glider.

Distinct from the earlier catalogue (`core/gliders.py`) of A/B/C/D/Ē at width 0 — that catalogue is real Rule 110 gliders but **not Cook's specific variants** (different ether-phase relationship on the two sides). The Cook-faithful set was found only after fixing the search to allow [[Two-phase ether placement|two-phase ether halos]] (left at phase L, right at phase L+W).

Glider E (period 15, −4, width E_n = 11+8n) is still **unfound** — see [[Glider E unfound after 172k-pattern sweep]].

The Cook construction's other compound objects are built on this catalogue: A₄ = 4 As packed at 14-cell spacing; ossifier = 16 As in 4 groups; leader = 8 Ēs; tape character = 4 C2s; appendant component = 2 Ēs.

## Connects to

- [[Cook glider width]]
- [[Cook universality proof]]
- [[Two-phase ether placement]]
- [[Cook crossing window]]
- [[Glider E unfound after 172k-pattern sweep]]
- [[Detector audit reversal]]
- [[Rule 110 compiler]]
