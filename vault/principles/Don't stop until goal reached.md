---
type: principle
era: side-projects
tags: [rule-110, principle, non-negotiable]
date: 2026-05-18
---

# Don't stop until goal reached

The first non-negotiable in `AGENTS.md` of the [[Rule 110 compiler]] repo. Added mid-session after the agent stopped at a series of intermediate "good places to pause" with the end goal still unmet.

Exact rule:

> Do not stop until the goal is reached. When the user has set a goal — explicit or implicit — keep working until it is verifiably achieved or until the user explicitly redirects. Intermediate progress is not a stopping condition. Running out of obvious next moves is not a stopping condition; finding non-obvious ones is part of the job. Reaching a natural-feeling end-of-session is not a stopping condition.

Three companion clauses live alongside it:

- **Be honest about scope.** Surface obstacles explicitly; keep working on tractable parts; do not pre-emptively scope-down silently.
- **Sub-goal progress counts.** When the end goal decomposes into verifiable sub-steps, each new sub-step verified is genuine progress and should be committed and announced.
- The [[Honesty mandate]] is the other binding constraint of the project.

Exists because the project had been restarted multiple times by agents stopping at intermediate milestones with the goal unmet. The rule changed observable behaviour the same session: a 42-minute test ([[42-minute test ran on slow python evolver]]) that would otherwise have been left "verified once, marked slow" got numpy-accelerated to 18 seconds and put back in the default suite.

## Connects to

- [[Honesty mandate]]
- [[42-minute test ran on slow python evolver]]
- [[Detector audit reversal]]
- [[Rule 110 compiler]]
