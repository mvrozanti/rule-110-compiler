---
type: concept
era: side-projects
tags: [rule-110, cook, placement, ether]
date: 2026-05
---

# Two-phase ether placement

How `compiler/cook_tape.py` and `core/cook_gliders.place_cook_glider` lay a Cook-faithful glider into a state. The glider has different [[Phase-shifted ether|ether phases]] on its two sides (left at phase `cumulative_width_before`, right at `cumulative_width_before + glider.width`), so placement requires three steps:

1. Snap the requested anchor forward so the cells at the anchor are at the glider's `left_phase` in the **current cumulative-width context**.
2. Write the glider's delta bits at `[anchor, anchor + extent)`.
3. Rewrite every cell from `anchor + extent` to the end of the state as ether at phase `cumulative_width_before + glider.width`. This sets up the next glider's left halo correctly.

Chaining: each `place_cook_glider` returns `(delta_anchor, new_cumulative_width)`. The caller threads the cumulative width through successive placements left-to-right.

The earlier `core/gliders.py` placement model overlaid bits on a single shared phase — fine for gliders with [[Cook glider width|width]] 0, but wrong for Cook's specific variants. The two-phase model is why the Cook-faithful catalogue could finally be discovered (see [[Cook-faithful glider catalogue]]).

## Connects to

- [[Cook glider width]]
- [[Cook-faithful glider catalogue]]
- [[Phase-shifted ether]]
- [[Cook ether lattice]]
- [[Rule 110 compiler]]
