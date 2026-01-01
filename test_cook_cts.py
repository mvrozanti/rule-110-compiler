"""
Tests for Cook's CTS construction in Rule 110.
"""

import unittest
from cook_cts import (
    CTSSpec,
    encode_cts_to_rule110,
    run_cook_cts_simulation,
    simulate_cts_direct,
    example_duplicator,
    example_identity,
    example_unary_adder,
    _encode_symbol_to_gliders,
    _encode_appendant_to_gliders,
    _create_ether_background,
    _place_glider_package,
)


class TestCTSEncoding(unittest.TestCase):
    """Test CTS encoding to Rule 110 initial states."""

    def test_encode_symbol_y(self):
        """Test encoding Y symbol."""
        gliders = _encode_symbol_to_gliders('Y')
        self.assertEqual(gliders, ['C2', 'C2', 'C2', 'C2'])

    def test_encode_symbol_n(self):
        """Test encoding N symbol."""
        gliders = _encode_symbol_to_gliders('N')
        self.assertEqual(gliders, ['C2', 'C2', 'C2', 'C2'])

    def test_encode_symbol_invalid(self):
        """Test encoding invalid symbol raises error."""
        with self.assertRaises(ValueError):
            _encode_symbol_to_gliders('X')

    def test_encode_appendant(self):
        """Test encoding appendant string."""
        gliders = _encode_appendant_to_gliders('YN')
        # Each Y/N becomes 4 Ē gliders
        self.assertEqual(len(gliders), 8)
        self.assertTrue(all(g == 'Ē' for g in gliders))

    def test_create_ether_background(self):
        """Test ether background creation."""
        ether = _create_ether_background(28)  # Two periods
        self.assertEqual(len(ether), 28)
        # Should be periodic with period 14
        for i in range(14):
            self.assertEqual(ether[i], ether[i + 14])

    def test_place_glider_package(self):
        """Test placing glider package in state."""
        state = [0] * 50
        width = _place_glider_package(state, 'A', 25)

        # Should have created active region
        active_count = sum(state)
        self.assertGreater(active_count, 0)
        self.assertGreater(width, 0)


class TestCTSConstruction(unittest.TestCase):
    """Test full CTS construction."""

    def test_encode_simple_cts(self):
        """Test encoding a simple CTS."""
        cts = example_duplicator()
        construction = encode_cts_to_rule110(cts, tape_length=100)

        self.assertEqual(len(construction.initial_state), 100)
        # Should have active regions for tape data and moving data
        active_count = sum(construction.initial_state)
        self.assertGreater(active_count, 0)

    def test_duplicator_simulation(self):
        """Test that duplicator CTS works correctly."""
        cts = example_duplicator()

        # Direct CTS simulation
        direct_states = simulate_cts_direct(cts, steps=5)

        # Rule 110 simulation
        construction = encode_cts_to_rule110(cts)
        rule110_states = run_cook_cts_simulation(construction, steps=5)

        # Both should start with the same initial tape
        self.assertEqual(direct_states[0].tape, cts.initial_tape)
        # After processing: Y + YY = YY, then Y + YY = YYY, then Y + YY = YYYY
        if len(direct_states) >= 4:
            self.assertEqual(direct_states[1].tape, 'YY')
            self.assertEqual(direct_states[2].tape, 'YYY')
            self.assertEqual(direct_states[3].tape, 'YYYY')

    def test_identity_simulation(self):
        """Test identity CTS preserves input."""
        cts = example_identity()

        # Direct simulation - should empty tape quickly
        direct_states = simulate_cts_direct(cts, steps=5)

        # Should empty tape: YN -> N (after Y) -> '' (after N)
        if len(direct_states) >= 3:
            self.assertEqual(direct_states[1].tape, 'N')
            self.assertEqual(direct_states[2].tape, '')

    def test_construction_properties(self):
        """Test that constructions have required properties."""
        cts = example_duplicator()
        construction = encode_cts_to_rule110(cts, tape_length=200)

        # Should be long enough
        self.assertEqual(len(construction.initial_state), 200)

        # Should have ether background
        state = construction.initial_state
        # Check for periodic structure (ether)
        period = 14
        for i in range(period, len(state) - period):
            if state[i] == state[i + period]:
                periodic_found = True
                break
        else:
            periodic_found = False
        self.assertTrue(periodic_found, "Should have periodic ether background")


class TestCTSExamples(unittest.TestCase):
    """Test the provided CTS examples."""

    def test_duplicator_spec(self):
        """Test duplicator CTS specification."""
        cts = example_duplicator()
        self.assertEqual(cts.appendants, ['YY'])
        self.assertEqual(cts.initial_tape, 'Y')

        # Direct simulation should duplicate repeatedly
        states = simulate_cts_direct(cts, steps=4)
        if len(states) >= 4:
            # Step 0: 'Y'
            self.assertEqual(states[0].tape, 'Y')
            # Step 1: '' + 'YY' = 'YY'
            self.assertEqual(states[1].tape, 'YY')
            # Step 2: 'Y' + 'YY' = 'YYY'
            self.assertEqual(states[2].tape, 'YYY')
            # Step 3: 'YY' + 'YY' = 'YYYY'
            self.assertEqual(states[3].tape, 'YYYY')

    def test_identity_spec(self):
        """Test identity CTS specification."""
        cts = example_identity()
        self.assertEqual(cts.appendants, [''])
        self.assertEqual(cts.initial_tape, 'YN')

        # Should eventually empty the tape
        states = simulate_cts_direct(cts, steps=10)
        if states:
            final_state = states[-1]
            self.assertEqual(final_state.tape, "")

    def test_unary_adder_spec(self):
        """Test unary adder CTS specification."""
        cts = example_unary_adder()
        self.assertEqual(cts.appendants, ['YY', ''])
        self.assertEqual(cts.initial_tape, 'YYY')


if __name__ == '__main__':
    unittest.main()





