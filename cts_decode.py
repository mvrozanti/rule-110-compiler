"""
Symbolic CTS decoder/simulator to validate productions against specs.

This does not decode from CA tape; it simulates CTS queue evolution using the
rule set, providing an expected symbolic trace to compare against CA-derived
observations later.
"""
from typing import List

from cook_cts_encoder import CTSSpec, CTSRule


def step_cts(queue: List[str], rules: List[CTSRule]) -> List[str]:
    """
    Apply one CTS production: pop head, append production for matching rule.

    Cook CTS semantics: remove the first symbol, then append its production.
    """
    if not queue:
        return []
    head, rest = queue[0], queue[1:]
    production: List[str] = []
    for rule in rules:
        if rule.symbol == head:
            production = rule.production
            break
    return rest + production


def run_cts_symbolic(spec: CTSSpec, steps: int) -> List[List[str]]:
    """Return the queue evolution over steps (inclusive of initial)."""
    q = list(spec.queue)
    history = [q.copy()]
    for _ in range(steps):
        q = step_cts(q, spec.rules)
        history.append(q.copy())
    return history
