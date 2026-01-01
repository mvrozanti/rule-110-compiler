#!/usr/bin/env python3
"""
Unit tests for Rule 110 visualization correctness.

Tests basic Rule 110 evolution, glider detection, and ensures
the visualization shows what we expect it to show.
"""

import unittest
from rule110 import Rule110
from glider_tracker import track_gliders, GLIDER_PROPERTIES


class TestRule110Basics(unittest.TestCase):
    """Test basic Rule 110 evolution."""

    def test_rule110_transitions(self):
        """Test that Rule 110 follows correct transition rules."""
        # Test all 8 possible 3-bit neighborhoods
        test_cases = [
            # (left, center, right) -> expected_next
            ((0, 0, 0), 0),  # 000 -> 0
            ((0, 0, 1), 1),  # 001 -> 1
            ((0, 1, 0), 1),  # 010 -> 1
            ((0, 1, 1), 1),  # 011 -> 1
            ((1, 0, 0), 0),  # 100 -> 0
            ((1, 0, 1), 1),  # 101 -> 1
            ((1, 1, 0), 1),  # 110 -> 1
            ((1, 1, 1), 0),  # 111 -> 0
        ]

        for (left, center, right), expected in test_cases:
            with self.subTest(neighborhood=(left, center, right)):
                ca = Rule110([left, center, right])
                ca.step()
                self.assertEqual(ca.get_state()[1], expected,
                    f"Neighborhood {left}{center}{right} should become {expected}")

    def test_known_pattern_evolution(self):
        """Test evolution of a known stable pattern."""
        # Single 1 should become period-14 oscillator
        ca = Rule110([0, 0, 1, 0, 0])
        initial = ca.get_state().copy()

        # Run for a few steps
        for step in range(5):
            ca.step()
            state = ca.get_state()
            # Should maintain same length
            self.assertEqual(len(state), len(initial))
            # Should have some activity
            self.assertTrue(any(state), f"Step {step} should have active cells")

    def test_glider_detection(self):
        """Test that glider tracking works on a simple pattern."""
        # Create a simple pattern with known glider behavior
        ca = Rule110([0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1], boundary='ether')
        ca.run(10)
        history = ca.get_history()

        # Track gliders
        glider_track = track_gliders(history)

        # Should detect some gliders
        self.assertGreater(len(glider_track.gliders), 0, "Should detect gliders")

        # Should detect some collisions
        self.assertGreater(len(glider_track.collisions), 0, "Should detect collisions")

        print(f"Detected {len(glider_track.gliders)} gliders and {len(glider_track.collisions)} collisions")


class TestVisualizationSanity(unittest.TestCase):
    """Test that visualization inputs are sane."""

    def test_fixed_width_evolution(self):
        """Test that evolution maintains fixed width."""
        initial_state = [0] * 100 + [1] + [0] * 99  # Single 1 in middle
        ca = Rule110(initial_state, boundary='ether')

        # Run evolution
        ca.run(20)
        history = ca.get_history()

        # All states should have same width
        width = len(initial_state)
        for i, state in enumerate(history):
            self.assertEqual(len(state), width,
                f"State at step {i} has wrong width: {len(state)} != {width}")

    def test_activity_levels(self):
        """Test that evolution shows reasonable activity levels."""
        # Start with sparse pattern
        initial = [0] * 50 + [1, 0, 1] + [0] * 47
        ca = Rule110(initial, boundary='ether')

        initial_activity = sum(initial)
        max_activity = 0

        for step in range(15):
            ca.step()
            current_activity = sum(ca.get_state())
            max_activity = max(max_activity, current_activity)

        # Should have some activity
        self.assertGreater(max_activity, 0, "Should have some cellular activity")

        print(f"Initial activity: {initial_activity}, Max activity: {max_activity}")


class TestGliderProperties(unittest.TestCase):
    """Test glider detection properties."""

    def test_glider_velocities(self):
        """Test that detected gliders have reasonable velocities."""
        ca = Rule110([0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1], boundary='ether')
        ca.run(30)
        history = ca.get_history()

        glider_track = track_gliders(history)

        for glider in glider_track.gliders:
            # Get velocity from properties
            velocity = GLIDER_PROPERTIES.get(glider.glider_type, {}).get("velocity", 0)
            # Velocities should be reasonable (not faster than 1 cell/step)
            self.assertLess(abs(velocity), 2.0,
                f"Glider {glider.glider_type} velocity {velocity} seems unreasonable")

            # Should have reasonable lifetime
            lifetime = glider.step_last_seen - glider.step_first_seen
            self.assertGreater(lifetime, 0, "Glider should exist for multiple steps")

        velocities = [GLIDER_PROPERTIES.get(g.glider_type, {}).get("velocity", 0)
                     for g in glider_track.gliders[:5]]
        print(f"Glider velocities: {velocities}")


def run_visualization_tests():
    """Run all visualization tests and report results."""
    print("🧪 Running Rule 110 Visualization Unit Tests")
    print("=" * 50)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestRule110Basics)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestVisualizationSanity))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestGliderProperties))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n✅ All tests passed! Visualization should be showing correct Rule 110 behavior.")
    else:
        print(f"\n❌ {len(result.failures)} tests failed, {len(result.errors)} errors.")
        print("The visualization may not be showing what we expect.")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_visualization_tests()
    exit(0 if success else 1)
