"""Encode a small CTS instance into a Rule 110 initial state using Cook-style packages."""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

from cook_gliders import GLIDER_PACKAGES, PackagePlacement, build_base_tape, ETHER_BASE
from cts_scheduler import schedule_packages, MIN_SPACING


@dataclass
class CTSSymbol:
    name: str  # e.g., '1' or '0'
    package: str  # package key in GLIDER_PACKAGES


@dataclass
class CTSRule:
    symbol: str
    production: List[str]


@dataclass
class CTSSpec:
    queue: List[str]
    rules: List[CTSRule]
    ether_length: int = 400
    spacing: int = 14
    delimiter_package: str = "DELIM"
    symbol_map: Dict[str, str] = field(
        default_factory=lambda: {"1": "A", "0": "B", "X": "A", "Y": "B"}
    )
    ether_periods: Optional[int] = None

    def __post_init__(self):
        if self.ether_periods:
            # Prefer explicit ether periods if provided
            self.ether_length = self.ether_periods * len(ETHER_BASE)


@dataclass
class CTSEncoding:
    initial_state: List[int]
    placements: List[PackagePlacement]
    schedule_warnings: List[str]


def default_unary_duplicator() -> CTSSpec:
    """Minimal CTS that appends one symbol (toy example for validation)."""
    rules = [CTSRule(symbol="1", production=["1", "1"])]
    return CTSSpec(queue=["1"], rules=rules)


def _queue_packages(spec: CTSSpec) -> List[PackagePlacement]:
    placements: List[PackagePlacement] = []
    cursor = spec.spacing
    for symbol in spec.queue:
        pkg_name = spec.symbol_map.get(symbol) or spec.symbol_map.get("1") or "A"
        if not pkg_name:
            raise ValueError(f"No package mapped for symbol '{symbol}'")
        placements.append(PackagePlacement(pkg_name, cursor, phase=cursor % len(GLIDER_PACKAGES[pkg_name])))
        cursor += spec.spacing
    # delimiter after queue
    placements.append(PackagePlacement(spec.delimiter_package, cursor, phase=cursor))
    cursor += spec.spacing
    # rule block as repeated packages for now
    for rule in spec.rules:
        for sym in rule.production:
            pkg_name = spec.symbol_map.get(sym)
            placements.append(PackagePlacement(pkg_name, cursor, phase=cursor))
            cursor += spec.spacing
        placements.append(PackagePlacement(spec.delimiter_package, cursor, phase=cursor))
        cursor += spec.spacing
    return placements


def encode_cts(spec: CTSSpec) -> CTSEncoding:
    placements = _queue_packages(spec)
    sched = schedule_packages(placements, min_gap=spec.spacing // 2)
    tape, applied = build_base_tape(spec.ether_length, sched.placements)
    return CTSEncoding(initial_state=tape, placements=applied, schedule_warnings=sched.warnings)
