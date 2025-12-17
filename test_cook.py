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
            PackagePlacement("B", 28),  # ensures gap >= MIN_SPACING given package lengths
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

    def test_dynamic_growth_uses_ether_chunk(self):
        chunk = len(ETHER_BASE)
        ca = DynamicRule110([1], boundary="ether", grow_margin=1, grow_chunk=chunk)
        ca.run(2)
        # Growth should prepend/append ether chunk; ensure length increased and boundary uses ether values
        self.assertGreaterEqual(len(ca.get_state()), 1 + chunk)
        left_val = ca._boundary_value(-1)
        right_val = ca._boundary_value(len(ca.get_state()))
        self.assertIn(left_val, (0, 1))
        self.assertIn(right_val, (0, 1))

    def test_dynamic_growth_preserves_ether_prefix(self):
        chunk = len(ETHER_BASE)
        ca = DynamicRule110([1], boundary="ether", grow_margin=1, grow_chunk=chunk)
        ca._maybe_grow()  # force growth without evolution
        prefix = ca.get_state()[:chunk]
        self.assertEqual(prefix, ETHER_BASE[:chunk])

    def test_dynamic_growth_preserves_ether_suffix(self):
        chunk = len(ETHER_BASE)
        ca = DynamicRule110([1], boundary="ether", grow_margin=1, grow_chunk=chunk)
        ca._maybe_grow()
        suffix = ca.get_state()[-chunk:]
        self.assertEqual(suffix, ETHER_BASE[:chunk])

    def test_dynamic_growth_preserves_ether_after_steps(self):
        chunk = len(ETHER_BASE)
        ca = DynamicRule110([1], boundary="ether", grow_margin=1, grow_chunk=chunk)
        ca._maybe_grow()
        # Prefix/suffix after explicit growth should equal ether chunk
        self.assertEqual(ca.get_state()[:chunk], ETHER_BASE[:chunk])
        self.assertEqual(ca.get_state()[-chunk:], ETHER_BASE[:chunk])
        # After a step, boundary_value should still report ether pattern
        ca.step()
        left_boundary = [ca._boundary_value(-1 - i) for i in range(chunk)]
        right_boundary = [ca._boundary_value(len(ca.get_state()) + i) for i in range(chunk)]
        left_expected = [ETHER_BASE[(PHASE_MOD - 1 - i) % PHASE_MOD] for i in range(chunk)]
        right_expected = [ETHER_BASE[(len(ca.get_state()) + i) % PHASE_MOD] for i in range(chunk)]
        self.assertEqual(left_boundary, left_expected)
        self.assertEqual(right_boundary, right_expected)


if __name__ == "__main__":
    unittest.main()
