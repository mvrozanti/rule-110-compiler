---
type: concept
era: side-projects
tags: [rule-110, cellular-automaton, wolfram]
date: 2026-05
---

# Rule 110

The Wolfram-class-4 elementary cellular automaton. One-dimensional, binary cells, nearest-neighbour update by the rule named for the binary `01101110 = 110`:

```
111 → 0    011 → 1
110 → 1    010 → 1
101 → 1    001 → 1
100 → 0    000 → 0
```

Equivalently: "a cell at state 0 becomes 1 iff its right neighbour is 1; a cell at state 1 becomes 0 iff both neighbours are 1." Wolfram calls this "LeftLife" by analogy with Game of Life — life spreads left, crowded cells die.

[[Cook universality proof|Cook (2004)]] proved Rule 110 is computationally universal, the simplest 1D CA shown to be so. The proof routes a cyclic tag system through Cook's glider construction, with [[Cook crossing window]] as the central "moving data crosses tape data" sub-step and the ossifier as the "append new tape data" sub-step.

The [[Cook ether lattice|ether]] background and the [[Cook-faithful glider catalogue|six known glider classes]] are the substrate of the construction. Implementation lives at [[Rule 110 compiler]].

## Connects to

- [[Cook universality proof]]
- [[Cook ether lattice]]
- [[Cook-faithful glider catalogue]]
- [[Rule 110 compiler]]
