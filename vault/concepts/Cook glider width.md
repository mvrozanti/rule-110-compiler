---
type: concept
era: side-projects
tags: [rule-110, cook, glider, width]
date: 2026-05
---

# Cook glider width

Cook's per-glider "width" (Figure 5 of `Cook_2004_UniversalityInElementaryCellularAutomata.pdf`): the offset, mod 14, of the [[Cook ether lattice|ether]] on the glider's right relative to the extrapolated continuation of the ether on its left. A → 6, B → 8, C₁ → 9, **C₂ → 3**, C₃ → 11, **Ē → 7**, etc.

Width is the central quantity for **placing** Cook gliders. The [[Cook-faithful glider catalogue]] entries differ from the project's earlier-extracted "minimal delta" gliders precisely on this point: the older ones had width 0 (no ether shift), and were therefore not Cook's specific variants at all.

Practical consequence: a Cook glider has **different ether phases on its two sides**. Placing it requires [[Two-phase ether placement]] — write the delta, then rewrite the cells to its right as ether at phase shifted by `width`. Chaining multiple gliders compounds the shift.

Width also explains why our [[Cook crossing window]] exists at a specific gap range: the crossing requires the incoming Ē to be at α₃ from the C₂ it crosses, which translates to specific cell offsets relative to the ether lattice.

## Connects to

- [[Cook ether lattice]]
- [[Cook-faithful glider catalogue]]
- [[Two-phase ether placement]]
- [[Cook crossing window]]
- [[Cook universality proof]]
- [[Rule 110 compiler]]
