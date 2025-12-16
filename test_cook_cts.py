import pytest

from cook_cts_encoder import default_unary_duplicator, encode_cts
from cts_scheduler import schedule_packages
from cook_gliders import PackagePlacement
from cts_executor import run_cts


def test_encode_cts_not_empty():
    spec = default_unary_duplicator()
    encoding = encode_cts(spec)
    assert len(encoding.initial_state) == spec.ether_length
    assert encoding.placements, "placements should not be empty"


def test_scheduler_spacing_ok():
    placements = [PackagePlacement("A", 10), PackagePlacement("B", 30), PackagePlacement("DELIM", 50)]
    result = schedule_packages(placements, min_gap=5)
    assert result.valid is True
    assert not result.warnings


def test_run_cts_produces_history():
    result = run_cts(steps=50)
    assert len(result.history) == 51  # includes initial
    assert result.initial_state
