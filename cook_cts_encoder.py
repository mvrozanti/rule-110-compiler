"""Encode a small CTS instance into a Rule 110 initial state using Cook-style packages."""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

from cook_gliders import GLIDER_PACKAGES, PackagePlacement, build_base_tape, ETHER_BASE, max_package_len, PHASE_MOD
from cts_scheduler import schedule_packages, MIN_SPACING, ScheduleResult


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
    symbol_map: Dict[str, str]
    spacing: int
    ether_length: int


def default_unary_duplicator() -> CTSSpec:
    """Minimal CTS that appends one symbol (toy example for validation)."""
    rules = [CTSRule(symbol="1", production=["1", "1"])]
    return CTSSpec(queue=["1"], rules=rules)


def cts_example_small() -> CTSSpec:
    """
    Simple CTS with two symbols to use as a regression fixture.
    Production:
      X -> XY
      Y -> X
    """
    rules = [
        CTSRule(symbol="X", production=["X", "Y"]),
        CTSRule(symbol="Y", production=["X"]),
    ]
    return CTSSpec(queue=["X"], rules=rules)


def _queue_packages(spec: CTSSpec) -> List[PackagePlacement]:
    placements: List[PackagePlacement] = []
    cursor = spec.spacing
    for symbol in spec.queue:
        pkg_name = spec.symbol_map.get(symbol) or spec.symbol_map.get("1") or "A"
        if not pkg_name:
            raise ValueError(f"No package mapped for symbol '{symbol}'")
        placements.append(PackagePlacement(pkg_name, cursor, phase=cursor % PHASE_MOD))
        cursor += spec.spacing
    # delimiter after queue
    placements.append(PackagePlacement(spec.delimiter_package, cursor, phase=cursor % PHASE_MOD))
    cursor += spec.spacing
    # rule block as repeated packages for now
    for rule in spec.rules:
        for sym in rule.production:
            pkg_name = spec.symbol_map.get(sym)
            placements.append(PackagePlacement(pkg_name, cursor, phase=cursor % PHASE_MOD))
            cursor += spec.spacing
        placements.append(PackagePlacement(spec.delimiter_package, cursor, phase=cursor % PHASE_MOD))
        cursor += spec.spacing
    return placements


def encode_cts(spec: CTSSpec) -> CTSEncoding:
    _validate_spec(spec)
    placements = _queue_packages(spec)
    min_gap = max(3, spec.spacing - max_package_len())
    sched: ScheduleResult = schedule_packages(
        placements,
        min_gap=min_gap,
        phase_mod=PHASE_MOD,
        strict=True,
    )
    if not sched.valid:
        raise ValueError(f"Invalid CTS schedule: {sched.warnings}")
    tape, applied = build_base_tape(spec.ether_length, sched.placements)
    return CTSEncoding(
        initial_state=tape,
        placements=applied,
        schedule_warnings=sched.warnings,
        symbol_map=spec.symbol_map,
        spacing=spec.spacing,
        ether_length=spec.ether_length,
    )


def _validate_spec(spec: CTSSpec) -> None:
    if spec.spacing < MIN_SPACING:
        raise ValueError(f"spacing {spec.spacing} too small; need >= {MIN_SPACING}")
    if spec.delimiter_package not in GLIDER_PACKAGES:
        raise ValueError(f"delimiter '{spec.delimiter_package}' missing from GLIDER_PACKAGES")
    if not spec.queue:
        raise ValueError("CTS queue must not be empty")
    if not spec.rules:
        raise ValueError("CTS rules must not be empty")

    # Ensure all symbols map to packages
    for symbol in spec.queue:
        if symbol not in spec.symbol_map:
            raise ValueError(f"No package mapping for queue symbol '{symbol}'")
    for rule in spec.rules:
        if rule.symbol not in spec.symbol_map:
            raise ValueError(f"No package mapping for rule symbol '{rule.symbol}'")
        for prod_sym in rule.production:
            if prod_sym not in spec.symbol_map:
                raise ValueError(f"No package mapping for production symbol '{prod_sym}'")

    # Ensure spacing is feasible with package lengths
    if spec.spacing - max_package_len() < 0:
        raise ValueError(f"spacing {spec.spacing} too small for package length {max_package_len()}")
