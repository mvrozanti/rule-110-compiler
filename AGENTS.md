# AGENTS.md

Conventions for contributors (human or AI) to `rule-110-compiler`.

## Non-negotiables

These rules supersede all other instructions in this file and elsewhere. They
exist because the project has been restarted multiple times by agents
stopping at intermediate milestones with the goal unmet.

1. **Do not stop until the goal is reached.** When the user has set a
   goal — explicit or implicit — keep working until it is verifiably
   achieved or until the user explicitly redirects. Intermediate
   "progress" is not a stopping condition. Running out of obvious next
   moves is not a stopping condition; finding non-obvious ones is part
   of the job. Reaching a natural-feeling end-of-session is not a
   stopping condition. The only stopping conditions are: (a) the goal
   is met and verifiable, (b) the user redirects, or (c) a destructive
   action would be required that needs explicit confirmation (per the
   global Claude Code rules). A long session is not a violation. A
   "good place to pause" is not a stopping condition.

2. **Be honest about scope.** If after substantial effort the goal
   appears unreachable in the current direction, surface the obstacle
   explicitly to the user — but keep working on the parts that are
   still tractable while waiting for redirection. Don't pre-emptively
   scope-down silently.

3. **Sub-goal progress counts.** When the end goal decomposes into
   verifiable sub-steps, each new sub-step verified is genuine
   progress and should be committed and announced. Don't withhold
   sub-step commits waiting for the full end-goal to be complete; the
   user wants to see progress materialise.

## Mission

Compile Brainfuck programs down to Rule 110 initial conditions per Matthew
Cook's 2004 universality proof, and visualize the layered correspondence
between source program and cellular-automaton evolution. Honesty about what
works is the binding constraint: this project has been restarted multiple
times because previous attempts shipped scaffolding without verifying any
layer empirically.

## Pipeline

```
BF source --> TM --> CTS --> Rule 110 initial bitstring --> evolution --> decoded output
   §6        §6     §5             §4                          §1            §7
```

Each phase has its own module(s) and test file, and is gated by an empirical
test that fails loudly when the layer is wrong. No phase begins until the
previous phase's tests are green.

## Honesty mandate

1. Don't claim a layer works without a test that fails loudly when it doesn't.
2. Commit messages describe what changed, not what was achieved. Conventional
   Commits (`type(scope): summary`), imperative, lowercase, no trailing period,
   no emojis, no "complete" / "comprehensive" / "world's first" rhetoric.
3. Anything broken is named in the README status table in the same commit that
   breaks it. A row moves to `verified` only when a green test proves it.

## Cook faithfulness

Carries forward the substance of the prior `.cursor/rules/cook-faithfulness.mdc`.
The cellular-automaton layer must be exactly Cook's:

- Glider patterns sourced (cite `15-1-1.pdf` §X.Y or an external reference table).
  No inferred or hand-waved patterns.
- Ether is the exact 14-cell period `(1,1,1,1,1,0,0,0,1,0,0,1,1,0)`,
  translating 4 cells left per step, temporal period 7. Verified in
  `tests/test_ether.py`. (The prior codebase used a different 14-bit string
  that does **not** reproduce under Rule 110 — a load-bearing example of why
  every primitive needs an empirical test.)
- Collisions are designed, not timed. Operations emerge from glider interactions,
  not from artificial wall-clock dispatch.
- Spacing uses Cook's α (diagonal) and β (vertical) ether-distance arithmetic
  from §3.2.2-§3.2.4.

One intentional relaxation: the **TM → CTS** stage uses the Neary-Woods 2006
reduction rather than Cook's §5 construction. Reason: tractability and clearer
published references. Documented in `docs/decisions/0001-tm-to-cts-reduction.md`.
The Rule 110 layer itself remains pure Cook.

## Visualization caution

Carries forward `.cursor/rules/visualization_caution.md`:

- The user is the arbiter of visual correctness. "Looks right to the developer"
  does not count.
- One change at a time. Show, don't claim. Never write "fixed" without user
  confirmation.
- Conservative defaults; toggles for verification; clear labels.
- Build the simplest viz first (2 panes), get approval, then extend.

## Build invariants

- Every Cook primitive gets a passing test before any downstream code uses it.
- No comments in code. Module docstrings and named functions only. Comments
  rot; tests don't.
- Files under 200 LOC. One concept per file.
- Conventional Commits, no emojis. Each commit is one coherent unit of change.
- Tests stay green. If a phase breaks, the offending change reverts or the
  status table flips.

## File layout

```
core/        Rule 110 simulator + ether + Cook glider primitives + verified collisions
compiler/    pipeline stages: bf, bf_to_tm, tm, tm_to_cts, cts, cts_to_r110
runtime/     evolve + decode (R110 final state -> CTS -> TM -> BF output)
viz/         single-page synchronized-pane visualization (static HTML+JS)
tests/       pytest, one file per phase
docs/        pipeline.md, glider_atlas.md, decisions/, reference/
scripts/     collide.py (collision sandbox), verify_all.py (end-to-end check)
```

## Verification ladder

In order. A phase may not begin until the phase above is green.

| Phase | Command |
|---|---|
| 1 | `pytest tests/test_rule110.py tests/test_ether.py` |
| 2 | `pytest tests/test_gliders.py` |
| 3 | `pytest tests/test_collisions.py` |
| 4 | `pytest tests/test_cts.py tests/test_cts_in_r110.py` |
| 5 | `pytest tests/test_tm_to_cts.py` |
| 6 | `pytest tests/test_bf_to_tm.py` |
| 7 | `pytest tests/test_end_to_end.py` then `python scripts/verify_all.py` |
| 8 | Open `viz/index.html` in a browser; user confirms each pane reads correctly |

## Status

See the table in `README.md`. Updated in the same commit that changes status.
