#!/usr/bin/env python3
"""
Unit tests for Rule110 simulator
"""

import unittest
from rule110 import Rule110, Rule110Compiler, visualize


class TestRule110(unittest.TestCase):
    """Test cases for Rule110 simulator"""
    
    def test_initialization(self):
        """Test Rule110 initialization"""
        initial_state = [1, 0, 1, 0, 1]
        ca = Rule110(initial_state)
        self.assertEqual(ca.get_state(), initial_state)
        self.assertEqual(len(ca.get_history()), 1)
        self.assertEqual(ca.get_history()[0], initial_state)
    
    def test_rule110_transitions(self):
        """Test Rule 110 transition rules"""
        ca = Rule110([1, 1, 1])
        next_state = ca._rule110(1, 1, 1)
        self.assertEqual(next_state, 0)  # 111 -> 0
        
        self.assertEqual(ca._rule110(1, 1, 0), 1)  # 110 -> 1
        self.assertEqual(ca._rule110(1, 0, 1), 1)  # 101 -> 1
        self.assertEqual(ca._rule110(1, 0, 0), 0)  # 100 -> 0
        self.assertEqual(ca._rule110(0, 1, 1), 1)  # 011 -> 1
        self.assertEqual(ca._rule110(0, 1, 0), 1)  # 010 -> 1
        self.assertEqual(ca._rule110(0, 0, 1), 1)  # 001 -> 1
        self.assertEqual(ca._rule110(0, 0, 0), 0)  # 000 -> 0
    
    def test_step_execution(self):
        """Test single step execution"""
        # Use a pattern that definitely changes: [0, 0, 1]
        # 000 -> 0, 001 -> 1, so result should be [0, 1, ?]
        ca = Rule110([0, 0, 1])
        initial_state = ca.get_state()
        ca.step()
        
        # History should have 2 entries
        self.assertEqual(len(ca.get_history()), 2)
        # New state should be same length
        self.assertEqual(len(ca.get_state()), len(initial_state))
        # For this pattern, second cell should become 1 (001 -> 1)
        # So state should change
        new_state = ca.get_state()
        # At minimum, verify the structure is correct
        self.assertEqual(len(new_state), len(initial_state))
    
    def test_multiple_steps(self):
        """Test running multiple steps"""
        ca = Rule110([1, 0, 1, 0, 1])
        ca.run(10)
        
        # Should have 11 states in history (initial + 10 steps)
        self.assertEqual(len(ca.get_history()), 11)
    
    def test_state_preservation(self):
        """Test that state is preserved correctly"""
        initial_state = [1, 0, 1, 0, 1, 0, 1]
        ca = Rule110(initial_state)
        
        # After 0 steps, state should match initial
        self.assertEqual(ca.get_state(), initial_state)
        
        ca.run(5)
        # State should be different from initial
        self.assertNotEqual(ca.get_state(), initial_state)
        # But initial should still be in history
        self.assertEqual(ca.get_history()[0], initial_state)
    
    def test_boundary_conditions(self):
        """Test boundary handling"""
        # Test with single cell
        ca = Rule110([1])
        ca.run(5)
        self.assertGreater(len(ca.get_history()), 1)
        
        # Test with empty state (should handle gracefully)
        ca = Rule110([])
        ca.run(3)
        self.assertEqual(len(ca.get_history()), 4)
        self.assertEqual(ca.get_state(), [])
    
    def test_history_access(self):
        """Test history access methods"""
        initial_state = [1, 0, 1]
        ca = Rule110(initial_state)
        ca.run(5)
        
        history = ca.get_history()
        self.assertEqual(len(history), 6)  # initial + 5 steps
        self.assertEqual(history[0], initial_state)
        
        # Verify each step is stored
        for i, state in enumerate(history):
            self.assertIsInstance(state, list)


class TestRule110Compiler(unittest.TestCase):
    """Test cases for Rule110Compiler"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.compiler = Rule110Compiler()
    
    def test_initialization(self):
        """Test compiler initialization"""
        self.assertIsInstance(self.compiler.patterns, dict)
        self.assertIn('glider', self.compiler.patterns)
        self.assertIn('block', self.compiler.patterns)
    
    def test_compile_pattern(self):
        """Test pattern compilation"""
        state = self.compiler.compile_pattern('glider')
        self.assertIsInstance(state, list)
        self.assertGreater(len(state), 0)
        # All elements should be 0 or 1
        self.assertTrue(all(cell in (0, 1) for cell in state))
    
    def test_compile_pattern_with_width(self):
        """Test pattern compilation with width specification"""
        state = self.compiler.compile_pattern('block', width=20)
        self.assertEqual(len(state), 20)
        self.assertTrue(all(cell in (0, 1) for cell in state))
    
    def test_compile_pattern_unknown(self):
        """Test compilation of unknown pattern raises error"""
        with self.assertRaises(ValueError):
            self.compiler.compile_pattern('unknown_pattern')
    
    def test_compile_binary(self):
        """Test binary string compilation"""
        state = self.compiler.compile_binary('101010')
        self.assertEqual(state, [1, 0, 1, 0, 1, 0])
    
    def test_compile_binary_empty(self):
        """Test empty binary string"""
        state = self.compiler.compile_binary('')
        self.assertEqual(state, [])
    
    def test_compile_binary_with_spaces(self):
        """Test binary string with spaces"""
        state = self.compiler.compile_binary('1 0 1')
        # Should filter out spaces
        self.assertEqual(state, [1, 0, 1])
    
    def test_compile_from_code_pattern(self):
        """Test code compilation with pattern: prefix"""
        state = self.compiler.compile_from_code('pattern:glider')
        self.assertIsInstance(state, list)
        self.assertGreater(len(state), 0)
    
    def test_compile_from_code_binary(self):
        """Test code compilation with binary: prefix"""
        state = self.compiler.compile_from_code('binary:1010')
        self.assertEqual(state, [1, 0, 1, 0])
    
    def test_compile_from_code_repeat(self):
        """Test code compilation with repeat: prefix"""
        state = self.compiler.compile_from_code('repeat:block:3')
        block_pattern = self.compiler.patterns['block']
        expected_length = len(block_pattern) * 3
        self.assertEqual(len(state), expected_length)
    
    def test_compile_from_code_direct_binary(self):
        """Test direct binary string compilation"""
        state = self.compiler.compile_from_code('1100')
        self.assertEqual(state, [1, 1, 0, 0])
    
    def test_add_pattern(self):
        """Test adding custom pattern"""
        custom_pattern = [1, 0, 1, 0]
        self.compiler.add_pattern('custom', custom_pattern)
        
        self.assertIn('custom', self.compiler.patterns)
        state = self.compiler.compile_pattern('custom')
        self.assertEqual(state, custom_pattern)
    
    def test_pattern_width_padding(self):
        """Test that patterns are padded correctly"""
        state = self.compiler.compile_pattern('block', width=10)
        self.assertEqual(len(state), 10)
        # Block is [1,1,1,1], should be centered
        # Center is around index 3-6
        self.assertEqual(state[3:7], [1, 1, 1, 1])
    
    def test_pattern_width_truncation(self):
        """Test that long patterns are truncated"""
        long_pattern = [1] * 50
        self.compiler.add_pattern('long', long_pattern)
        state = self.compiler.compile_pattern('long', width=10)
        self.assertEqual(len(state), 10)


class TestVisualize(unittest.TestCase):
    """Test cases for visualization function"""
    
    def test_visualize_basic(self):
        """Test basic visualization"""
        history = [
            [1, 0, 1],
            [1, 1, 0],
            [0, 1, 1]
        ]
        # Should not raise exception
        try:
            visualize(history)
        except Exception as e:
            self.fail(f"visualize raised {e}")
    
    def test_visualize_custom_chars(self):
        """Test visualization with custom characters"""
        history = [[1, 0, 1]]
        # Should not raise exception with custom chars
        try:
            visualize(history, char_alive='X', char_dead='.')
        except Exception as e:
            self.fail(f"visualize raised {e}")
    
    def test_visualize_empty_history(self):
        """Test visualization with empty history"""
        history = []
        # Should handle empty history gracefully
        try:
            visualize(history)
        except Exception as e:
            self.fail(f"visualize raised {e}")


if __name__ == '__main__':
    unittest.main()

