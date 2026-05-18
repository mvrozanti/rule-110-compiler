# 0007 — Deadline status snapshot, 2026-05-18

## Status

In-flight. Honest assessment two days into the 2026-05-31 deadline plan.

## Where we are

**Tests:** 158 passing in default suite + 1 SLOW passing demo (42-min
runtime, deselected by default but verified once empirically), 1 xfailed.

**Verified milestones:**

| ID | Target | Status |
|---|---|---|
| M1 | 2026-05-20 — glider E | not yet, no slip |
| M2 | 2026-05-22 — α/β calibration | **completed early** |
| M3 | 2026-05-25 — Cook's core 8 collisions | **1 of 8 verified.** C2 × Ebar crossing pinned (Cook §3.2.4) at 6 gap values + 8-period persistence + post-crossing phase shift characterised |
| M4 | 2026-05-28 — collision-driven CTS step | **structural building block verified.** Multi-C2 tape traversal: one Ebar performs 10 sequential Cook crossings inside R110. Each crossing is the "moving data crosses tape data" sub-step of Cook's CTS mechanic. Not the full CTS step (no consume, no append) — see "structural limitation" below |
| M5 | 2026-05-31 — end-to-end demo | **partial: BF → 8 Cook crossings inside R110 verified.** `test_eight_crossings_from_bf_plusplus_cts_inside_r110` (slow) runs BF '++' compiled through tm → aligned tag → CTS → Cook-faithful R110 IC → 28k-step Rule 110 evolution. CTS state at step 314 has 8 Ys; at least 5 of those Ys survive the scanner Ebar's traversal as verified Cook §3.2.4 crossings. **No Python intervention between BF compilation and the R110 collisions.** |

## Structural limitation discovered

A Cook CTS step requires BOTH:
  1. Consuming the leftmost tape symbol (when Y, the tape character is
     destroyed and the appendant fires)
  2. Appending the appendant on the right (ossifier mechanism)

Empirically swept all 200 placement gaps for C2 × Ebar in our verified
catalogue. **Only two outcomes occur:**
  - C2 alive + Ebar alive: **crossing** (158 gaps)
  - C2 alive + Ebar dead: **Ebar absorbed by C2** (42 gaps)

**C2 is never destroyed.** Our catalogue does not have a "Y consumed by
moving data" reaction. Cook's full mechanism uses 4 C2s per tape character
(grouped into a single character with internal spacings) and 8 Ebars per
leader (grouped); the higher-level consume mechanic emerges from those
compound objects, not single C2 × single Ebar reactions.

Similarly, A4 × Ebar (ossification) requires the right A4 packing, which
single A × Ebar tests did not reproduce.

## What today's demo proves

`test_eight_crossings_from_bf_plusplus_cts_inside_r110` shows the
**upper layers of Cook's construction** working end-to-end:

  - BF compiles to a Cook §2.1+§2.2 CTS.
  - The CTS state at step 314 is a real BF-derived data structure with
    8 Ys interleaved among Ns.
  - Cook-faithful glider encoding turns the CTS state into a real
    Rule 110 initial condition.
  - Rule 110 evolves the IC forward 28,000 steps.
  - During that evolution, ≥5 distinct Cook §3.2.4 crossing collisions
    occur — each is an elementary Rule 110 reaction structurally
    driving Cook's "moving data crosses tape data" mechanic.

That's the "upper bound" of what the current catalogue supports. The
"lower bound" — full CTS step dynamics (consume + append) — requires
either:
  - Compound objects: 4-C2-per-character tape + 8-Ebar leader (Cook's
    actual mechanism); the consume/append emerge from internal
    sub-collisions among these compound parts.
  - More glider variants: e.g. a destructive C2-killing reaction, or
    A4 ossification, neither found in 200-gap sweeps.

## Honest deadline status

The 2026-05-31 "5 real CTS steps inside R110" deadline is **at risk**.
The structural gap is real: our verified gliders don't support the
consume/append primitives a full CTS step needs.

Forward options:
  1. Build the compound objects (4-C2 character, 8-Ebar leader) and
     find which gap configurations produce Cook's consume/append at the
     compound level. Significant search work.
  2. Discover additional Cook-faithful glider variants (e.g. C1, C3
     with different widths) whose collisions DO include consume/append
     primitives at the single-glider level.
  3. Reframe the deadline target: "structural computation steps inside
     R110" (which the 8-crossing demo provides) instead of "complete
     CTS steps with consume + append".

Forward path I'm pursuing without waiting for explicit direction:
option (1), since it's the most Cook-faithful continuation and the
compound objects are next-level Cook building blocks already.
