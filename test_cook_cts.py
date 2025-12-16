import pytest

from cook_cts_encoder import default_unary_duplicator, encode_cts
from cts_scheduler import schedule_packages, MIN_SPACING
from cook_gliders import PackagePlacement
from cts_executor import run_cts, extract_queue_slice, active_counts, queue_window


def test_encode_cts_not_empty():
    spec = default_unary_duplicator()
    encoding = encode_cts(spec)
    assert len(encoding.initial_state) == spec.ether_length
    assert encoding.placements, "placements should not be empty"


def test_scheduler_spacing_ok():
    placements = [PackagePlacement("A", 10), PackagePlacement("B", 30), PackagePlacement("DELIM", 50)]
    result = schedule_packages(placements, min_gap=MIN_SPACING)
    assert result.valid is True
    assert not result.warnings


def test_scheduler_spacing_fail():
    placements = [PackagePlacement("A", 10), PackagePlacement("B", 12)]
    result = schedule_packages(placements, min_gap=MIN_SPACING)
    assert result.valid is False
    assert any("Gap too small" in w for w in result.warnings)


def test_encode_cts_rejects_too_small_spacing():
    spec = default_unary_duplicator()
    spec.spacing = MIN_SPACING - 1
    with pytest.raises(ValueError):
        encode_cts(spec)


def test_run_cts_produces_history():
    result = run_cts(steps=50)
    assert len(result.history) == 51  # includes initial
    assert result.initial_state
    assert result.spec


def test_extract_queue_slice_and_counts():
    result = run_cts(steps=10)
    window = (0, 20)
    sliced = extract_queue_slice(result.history, window)
    assert len(sliced) == 11
    counts = active_counts(result.history)
    assert len(counts) == 11
    assert all(c >= 0 for c in counts)


def test_queue_window_signature_stable():
    result = run_cts(steps=12)
    # Take a small window around the middle; ensure length and shape are stable
    win = queue_window(result.history, center=10, radius=5)
    assert len(win) == len(result.history)
    assert all(len(row) == 10 for row in win[:-1]) or all(len(row) in (9, 10) for row in win)  # tolerate edge
