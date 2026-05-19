---
type: decision
era: side-projects
tags: [rule-110, cook, scope, faithfulness]
date: 2026-05-17
---

# Cook-inspired vs Cook-faithful

A scope question that ran through the middle of the [[Rule 110 compiler]] session, formalised in `docs/decisions/0002-empirical-catalog-divergence.md` and revisited in 0004.

[[Cook universality proof]] specifies glider variants by [[Cook glider width|width]] (A=6, C2=3, Ē=7, …). Our originally-extracted `core/gliders.py` catalogue had every glider at width **0** — real Rule 110 gliders, but not Cook's specific variants. Earlier ADRs proposed two paths:

- **Cook-inspired (Plan B)**: accept the width-0 catalogue, build a verifiable demo of "computation inside R110" using our gliders' specific collision behaviour, accept the resulting system is *not* Cook's universality construction.
- **Cook-faithful (Plan A)**: find Cook's specific width-W variants, rebuild placement to handle [[Two-phase ether placement|two-phase ether]], reproduce Cook's actual reactions.

Plan A was abandoned briefly (ADR 0003 declared it structurally blocked), then reversed (ADR 0004) once `scripts/find_cook_variants.py` found A/C2/Ē at the right widths within minutes of allowing the right-halo phase shift.

Outcome: Plan A is the active path. [[Cook-faithful glider catalogue]] verified; [[Cook crossing window]] verified at gaps 36..49; ossifier reaction verified. The four-mechanism composition for a full CTS step remains the open frontier.

## Connects to

- [[Cook universality proof]]
- [[Cook glider width]]
- [[Cook-faithful glider catalogue]]
- [[Two-phase ether placement]]
- [[Cook crossing window]]
- [[Rule 110 compiler]]
