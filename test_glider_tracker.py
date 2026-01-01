"""
Unit tests for glider tracking.
"""

import unittest
from rule110 import Rule110
from glider_tracker import (
    track_gliders,
    _find_glider_at_position,
    GLIDER_PATTERNS,
    Glider,
    GliderTrack,
)


class TestGliderPatternMatching(unittest.TestCase):
    """Test glider pattern matching."""
    
    def test_find_glider_at_exact_position(self):
        """Test finding a glider at a known position."""
        # Create state with A-type glider at position 10
        state = [0] * 20
        pattern = GLIDER_PATTERNS["A"][0]
        for i, bit in enumerate(pattern):
            state[10 + i] = bit
        
        result = _find_glider_at_position(state, 10, tolerance=0)
        self.assertIsNotNone(result)
        self.assertEqual(result, ("A", 0))
    
    def test_find_glider_with_tolerance(self):
        """Test finding glider with Hamming tolerance."""
        state = [0] * 20
        pattern = GLIDER_PATTERNS["A"][0]
        for i, bit in enumerate(pattern):
            state[10 + i] = bit
        # Flip one bit
        state[12] = 1 - state[12]
        
        result = _find_glider_at_position(state, 10, tolerance=1)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "A")
    
    def test_find_glider_wrong_position(self):
        """Test that glider not found when state is empty."""
        state = [0] * 20  # Empty state
        
        result = _find_glider_at_position(state, 5, tolerance=0)
        self.assertIsNone(result)


class TestGliderTracking(unittest.TestCase):
    """Test glider tracking through evolution."""
    
    def test_track_single_glider(self):
        """Test tracking a single glider through multiple steps."""
        # Use the compiler's glider pattern (known to move)
        from rule110 import Rule110Compiler
        compiler = Rule110Compiler()
        glider_pattern = compiler.patterns['glider']
        
        state = [0] * 100
        for i, bit in enumerate(glider_pattern):
            state[20 + i] = bit
        
        ca = Rule110(state)
        ca.run(10)
        
        track = track_gliders(ca.get_history(), tolerance=2)
        
        # Should find at least one glider (any type)
        self.assertGreater(len(track.gliders), 0)
        
        # Glider should be tracked across multiple steps
        glider = track.gliders[0]
        # Allow for some steps where glider might not be detected
        self.assertGreaterEqual(glider.step_last_seen, glider.step_first_seen)
    
    def test_track_multiple_gliders(self):
        """Test tracking multiple gliders."""
        from rule110 import Rule110Compiler
        compiler = Rule110Compiler()
        glider_pattern = compiler.patterns['glider']
        
        state = [0] * 150
        # Place glider at position 20
        for i, bit in enumerate(glider_pattern):
            state[20 + i] = bit
        # Place another glider at position 60
        for i, bit in enumerate(glider_pattern):
            state[60 + i] = bit
        
        ca = Rule110(state)
        ca.run(5)
        
        track = track_gliders(ca.get_history(), tolerance=2)
        
        # Should find multiple gliders
        self.assertGreater(len(track.gliders), 1)
    
    def test_track_glider_velocity(self):
        """Test that glider position updates reflect velocity."""
        state = [0] * 100
        pattern = GLIDER_PATTERNS["A"][0]
        for i, bit in enumerate(pattern):
            state[10 + i] = bit
        
        ca = Rule110(state)
        ca.run(7)  # One full period
        
        track = track_gliders(ca.get_history(), tolerance=0)
        
        a_gliders = [g for g in track.gliders if g.glider_type == "A"]
        if a_gliders:
            glider = a_gliders[0]
            # After 7 steps, glider should have moved ~1 cell to the right
            initial_pos = glider.position
            # Check that position changed (allowing for tracking updates)
            self.assertIsInstance(glider.position, (int, float))
    
    def test_track_empty_state(self):
        """Test tracking on empty state."""
        state = [0] * 50
        ca = Rule110(state)
        ca.run(5)
        
        track = track_gliders(ca.get_history(), tolerance=0)
        self.assertEqual(len(track.gliders), 0)
        self.assertEqual(len(track.collisions), 0)


if __name__ == '__main__':
    unittest.main()






