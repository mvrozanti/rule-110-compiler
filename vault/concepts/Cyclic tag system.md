---
type: concept
era: side-projects
tags: [rule-110, cook, cts, tag-system]
date: 2026-05
---

# Cyclic tag system

A Turing-complete rewriting system used by [[Cook universality proof|Cook]] as the intermediate target between Turing machines and [[Rule 110]]. Alphabet `{Y, N}`. State: a finite tape over `{Y, N}` plus a cursor over a finite cyclic list of *appendants* (strings over `{Y, N}`).

One step:
- If tape empty, halt.
- Else pop the leftmost symbol. If Y, append the appendant at the cursor to the tape's right; if N, do nothing. Advance cursor cyclically.

Reductions (`compiler/` in the [[Rule 110 compiler]]):
- Turing machine → 2-tag (Cook §2.1) via `compiler/tm_to_tagsystem.py` — the "alignment" subtlety is handled by `aligned_tagsystem.py`.
- 2-tag → CTS (Cook §2.2) via `compiler/tagsystem_to_cts.py` — encodes each tag symbol as a length-k Y/N block, with a 2k-appendant structure (first k real, second k empty).

The full pipeline runs the CTS until terminal in Python; the goal of [[Rule 110 compiler]] is to run the CTS *steps* inside Rule 110 spacetime via Cook's glider construction. The structural sub-step of "moving data crosses tape data" is the [[Cook crossing window|C2 × Ē crossing]]; the "append" half needs the ossifier reaction.

## Connects to

- [[Cook universality proof]]
- [[Cook-faithful glider catalogue]]
- [[Cook crossing window]]
- [[Rule 110 compiler]]
