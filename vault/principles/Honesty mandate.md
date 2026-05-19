---
type: principle
era: side-projects
tags: [rule-110, principle, honesty]
date: 2026-05
---

# Honesty mandate

The binding constraint of the [[Rule 110 compiler]] project, recorded in `AGENTS.md`. Three clauses:

1. **No layer claims `verified` without a green test that fails loudly when the layer is wrong.** Scaffolding without an empirical test does not count.
2. **Commits describe what changed, not what was achieved.** Conventional Commits, lowercase, imperative, no "complete" / "comprehensive" / "world's first" rhetoric.
3. **Anything broken is named in the README status table in the same commit that breaks it.** A row moves to `verified` only when a green test proves it; rows that flip from `verified` to `revised` must say so explicitly.

The mandate exists because this project has been restarted multiple times — earlier attempts shipped grand scaffolding (TM, CTS, R110 sim) without verifying any layer empirically, then collapsed under the load of un-verified primitives.

The mandate's hardest test in this codebase was the [[Detector audit reversal]]: claims that had been documented as "verified Cook crossings" turned out to be [[Ether false-positive in glider detection|ether false positives]]. The mandate required marking those claims `REVISED` in the README in the same commit that fixed the detector, even though the headline-grade test had been celebrated.

The companion mandate is [[Don't stop until goal reached]] (non-negotiable 1): being honest about scope is *not* a stopping condition. Surface the obstacle; keep working on tractable parts; redirect on user input.

## Connects to

- [[Don't stop until goal reached]]
- [[Detector audit reversal]]
- [[Ether false-positive in glider detection]]
- [[Rule 110 compiler]]
