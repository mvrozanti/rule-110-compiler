import pytest

from cook_cts_encoder import default_unary_duplicator, encode_cts, cts_example_small
from cts_scheduler import schedule_packages, MIN_SPACING
from cook_gliders import PackagePlacement, GLIDER_PACKAGES
from cts_executor import run_cts, extract_queue_slice, active_counts, queue_window
from cook_ca_decoder import decode_queue_from_state
from cts_decode import run_cts_symbolic


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


def test_scheduler_detects_overlap_by_length():
    # B placed inside length of A
    a_len = len(GLIDER_PACKAGES["A"])
    placements = [
        PackagePlacement("A", 10),
        PackagePlacement("B", 10 + a_len - 2),  # overlaps by 2 cells
    ]
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


def test_cts_example_small_encodes_and_runs():
    spec = cts_example_small()
    encoding = encode_cts(spec)
    assert encoding.initial_state
    result = run_cts(spec, steps=12)
    assert len(result.history) == 13
    counts = active_counts(result.history)
    assert len(counts) == 13
    assert all(c >= 0 for c in counts)
    # metadata is preserved
    assert result.spacing == spec.spacing
    assert result.ether_length == spec.ether_length
    assert result.symbol_map == spec.symbol_map


def test_default_cts_active_counts_signature():
    result = run_cts(steps=20)
    counts = active_counts(result.history)
    # Signature updated after adopting Cook-like glider packages
    expected = [209, 236, 247, 245, 242, 274, 253, 248, 249, 331, 292, 237, 262, 268, 295, 342, 211, 222, 229, 297, 271]
    assert counts == expected


def test_small_cts_active_counts_signature():
    spec = cts_example_small()
    result = run_cts(spec, steps=15)
    counts = active_counts(result.history)
    expected = [212, 239, 248, 249, 240, 270, 254, 245, 250, 321, 289, 238, 259, 267, 291, 331]
    assert counts == expected


def test_default_cts_fingerprint_window():
    result = run_cts(steps=12)
    state = result.history[10]
    window = state[50:80]
    fingerprint = "".join(str(b) for b in window)
    assert fingerprint == "110011111000101100110101101111"


def test_small_cts_fingerprint_window():
    spec = cts_example_small()
    result = run_cts(spec, steps=12)
    state = result.history[10]
    window = state[50:80]
    fingerprint = "".join(str(b) for b in window)
    assert fingerprint == "110011111000101100110101101011"


def test_symbolic_cts_matches_expected_queue():
    spec = cts_example_small()
    symbolic = run_cts_symbolic(spec, steps=5)
    # For rules X->XY, Y->X (pop head, append production):
    expected = [
        ["X"],
        ["X", "Y"],
        ["Y", "X", "Y"],
        ["X", "Y", "X"],
        ["Y", "X", "X", "Y"],
        ["X", "X", "Y", "X"],
    ]
    assert symbolic == expected


def test_decode_initial_state_matches_symbolic_queue():
    spec = default_unary_duplicator()
    result = run_cts(spec, steps=0)
    decoded = decode_queue_from_state(result.initial_state, result.symbol_map, tolerance=0)
    assert decoded[:1] == spec.queue  # first symbol recovered


def test_decode_small_initial_state_matches_symbolic_queue():
    spec = cts_example_small()
    result = run_cts(spec, steps=0)
    decoded = decode_queue_from_state(result.initial_state, result.symbol_map, tolerance=0)
    assert decoded[:1] == spec.queue


def test_decode_fails_on_bad_alignment():
    spec = default_unary_duplicator()
    result = run_cts(spec, steps=0)
    shifted = [0] + result.initial_state  # break alignment
    decoded = decode_queue_from_state(shifted, result.symbol_map, tolerance=0)
    # Require a stricter match (first two symbols); expect mismatch or short decode
    assert decoded[:2] != spec.queue[:2]
