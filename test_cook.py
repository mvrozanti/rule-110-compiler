import unittest

from cook_gliders import ETHER_BASE, PHASE_MOD, make_ether, max_package_len
from cook_cts_encoder import CTSSpec, CTSRule, encode_cts
from cts_scheduler import MIN_SPACING, schedule_packages, PackagePlacement, ScheduleResult
from cook_cts_executor import run_cts
from rule110 import DynamicRule110


class TestCookEther(unittest.TestCase):
    def test_ether_length(self):
        ether = make_ether(len(ETHER_BASE) * 5)
        self.assertEqual(len(ether), 5 * len(ETHER_BASE))
        self.assertTrue(all(bit in (0, 1) for bit in ether))


class TestCookScheduler(unittest.TestCase):
    def test_spacing_respected(self):
        placements = [
            PackagePlacement("A", 10),
            PackagePlacement("B", 10 + MIN_SPACING + 1),
        ]
        result = schedule_packages(placements, min_gap=MIN_SPACING, phase_mod=PHASE_MOD, strict=True)
        self.assertTrue(result.valid)
        offsets = [p.offset for p in result.placements]
        self.assertGreaterEqual(offsets[1] - offsets[0] - 1, MIN_SPACING - 1)

    def test_phase_mismatch_detected(self):
        placements = [
            PackagePlacement("A", 0, phase=0),
            PackagePlacement("B", 20, phase=1),  # off by 1 from base phase
        ]
        result = schedule_packages(placements, min_gap=MIN_SPACING, phase_mod=PHASE_MOD, strict=False)
        self.assertFalse(result.valid)
        self.assertTrue(any("Phase mismatch" in w for w in result.warnings))


class TestCookEncoding(unittest.TestCase):
    def test_encode_cts_nonempty(self):
        spec = CTSSpec(queue=["X"], rules=[CTSRule("X", ["X"])])
        encoding = encode_cts(spec)
        tape = encoding.initial_state
        self.assertGreater(len(tape), 0)
        self.assertTrue(any(tape))  # should place at least one package


class TestCookExecutor(unittest.TestCase):
    def test_run_cts_executes(self):
        spec = CTSSpec(queue=["X"], rules=[CTSRule("X", ["X"])], ether_periods=30)
        result = run_cts(spec, steps=10)
        self.assertIn("history", result)
        self.assertGreater(len(result["history"]), 0)

    def test_dynamic_growth(self):
        ca = DynamicRule110([1], boundary="ether", grow_margin=1, grow_chunk=5)
        ca.run(3)
        # Expect growth to have occurred because activity is at edges
        self.assertGreaterEqual(len(ca.get_state()), 1 + 5)

    def test_dynamic_boundary_ether(self):
        ca = DynamicRule110([1], boundary="ether", grow_margin=1, grow_chunk=len(ETHER_BASE))
        ca.run(1)
        # After one step, boundary fill should use ether pattern
        left_val = ca._boundary_value(-1)
        right_val = ca._boundary_value(len(ca.get_state()))
        self.assertIn(left_val, (0, 1))
        self.assertIn(right_val, (0, 1))


if __name__ == "__main__":
    unittest.main()
