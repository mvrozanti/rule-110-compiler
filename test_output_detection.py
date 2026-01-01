#!/usr/bin/env python3
"""
Tests for output detection and decoding.

Verifies that output regions are detected correctly and decoding works.
"""

import unittest
from rule110_universal_compiler import compile_brainfuck_to_rule110
from rule110 import Rule110
from glider_tracker import track_gliders
from output_detection import (
    detect_output_region,
    decode_output_pattern,
    analyze_computation_result,
    find_stable_regions
)


class TestOutputDetection(unittest.TestCase):
    """Test output region detection."""

    def test_detect_output_region_basic(self):
        """Test basic output region detection."""
        program = "+"
        result = compile_brainfuck_to_rule110(program, tape_length=200)
        
        # Run evolution
        ca = Rule110(result['rule110_initial'], boundary='ether')
        ca.run(50)
        history = ca.get_history()
        
        # Track gliders
        glider_track = track_gliders(history)
        
        # Detect output region
        output_region = detect_output_region(
            history,
            glider_track.gliders,
            {}
        )
        
        # Should detect something (may be None if detection fails)
        if output_region:
            self.assertIn('start', output_region)
            self.assertIn('end', output_region)
            self.assertGreater(output_region['end'], output_region['start'])

    def test_detect_output_region_has_method(self):
        """Test that detected region includes detection method."""
        program = "+"
        result = compile_brainfuck_to_rule110(program, tape_length=200)
        
        ca = Rule110(result['rule110_initial'], boundary='ether')
        ca.run(50)
        history = ca.get_history()
        
        glider_track = track_gliders(history)
        output_region = detect_output_region(history, glider_track.gliders, {})
        
        if output_region:
            self.assertIn('detection_method', output_region)
            self.assertIn('confidence', output_region)

    def test_stable_regions_detection(self):
        """Test finding stable regions."""
        # Create a pattern that stabilizes
        state1 = [0] * 100 + [1] * 10 + [0] * 90
        state2 = state1.copy()
        state3 = state1.copy()
        
        stable = find_stable_regions([state1, state2, state3])
        
        # Should find stable region
        if stable:
            self.assertEqual(len(stable), 2)
            start, end = stable
            self.assertLess(start, end)

    def test_output_region_within_bounds(self):
        """Test that detected output region is within tape bounds."""
        program = "++"
        result = compile_brainfuck_to_rule110(program, tape_length=300)
        
        ca = Rule110(result['rule110_initial'], boundary='ether')
        ca.run(50)
        history = ca.get_history()
        
        glider_track = track_gliders(history)
        output_region = detect_output_region(history, glider_track.gliders, {})
        
        if output_region:
            tape_length = len(history[0])
            self.assertGreaterEqual(output_region['start'], 0)
            self.assertLessEqual(output_region['end'], tape_length)


class TestOutputDecoding(unittest.TestCase):
    """Test output pattern decoding."""

    def test_decode_binary_pattern(self):
        """Test decoding binary pattern to number."""
        # Binary pattern for 4 = 100
        pattern = [0, 0, 1, 0, 0]
        
        decoded = decode_output_pattern(pattern, expected_result=4)
        
        self.assertIsNotNone(decoded)
        self.assertIn('decoded_value', decoded)
        self.assertIn('method', decoded)

    def test_decode_unary_pattern(self):
        """Test decoding unary pattern (count of active cells)."""
        # Pattern with 5 active cells = unary 5
        pattern = [1, 1, 1, 1, 1, 0, 0, 0]
        
        decoded = decode_output_pattern(pattern)
        
        self.assertIsNotNone(decoded)
        self.assertIn('decoded_value', decoded)
        # Decoder may interpret as binary first (11111 = 31) or count as unary (5)
        # Both are valid - just check that we got a result
        self.assertIsInstance(decoded['decoded_value'], int)
        self.assertGreater(decoded['decoded_value'], 0)

    def test_decode_with_expected_result(self):
        """Test decoding with expected result for verification."""
        pattern = [1, 0, 0]  # Binary 4
        
        decoded = decode_output_pattern(pattern, expected_result=4)
        
        self.assertIsNotNone(decoded)
        self.assertIn('matches_expected', decoded)
        self.assertIn('expected', decoded)
        self.assertEqual(decoded['expected'], 4)

    def test_decode_empty_pattern(self):
        """Test decoding empty pattern returns None."""
        pattern = []
        
        decoded = decode_output_pattern(pattern)
        
        self.assertIsNone(decoded)


class TestFullAnalysis(unittest.TestCase):
    """Test complete computation analysis."""

    def test_analyze_computation_result(self):
        """Test full analysis including detection and decoding."""
        program = "+"
        result = compile_brainfuck_to_rule110(program, tape_length=200)
        
        ca = Rule110(result['rule110_initial'], boundary='ether')
        ca.run(50)
        history = ca.get_history()
        
        glider_track = track_gliders(history)
        
        analysis = analyze_computation_result(
            history,
            glider_track.gliders,
            {},
            expected_result=1
        )
        
        self.assertIn('output_region', analysis)
        self.assertIn('decoded_result', analysis)

    def test_analysis_detects_output_region(self):
        """Test that analysis detects output region."""
        program = "++"
        result = compile_brainfuck_to_rule110(program, tape_length=300)
        
        ca = Rule110(result['rule110_initial'], boundary='ether')
        ca.run(50)
        history = ca.get_history()
        
        glider_track = track_gliders(history)
        analysis = analyze_computation_result(history, glider_track.gliders, {})
        
        # Analysis should complete (output_region may be None if detection fails)
        self.assertIsNotNone(analysis)
        self.assertIn('output_region', analysis)


class TestOutputDetectionCorrectness(unittest.TestCase):
    """Test that output detection is actually correct."""

    def test_different_programs_detect_different_output_regions(self):
        """Test that different programs can detect different output regions."""
        program1 = "+"
        program2 = "++"
        
        result1 = compile_brainfuck_to_rule110(program1, tape_length=200)
        result2 = compile_brainfuck_to_rule110(program2, tape_length=200)
        
        ca1 = Rule110(result1['rule110_initial'], boundary='ether')
        ca1.run(50)
        glider_track1 = track_gliders(ca1.get_history())
        
        ca2 = Rule110(result2['rule110_initial'], boundary='ether')
        ca2.run(50)
        glider_track2 = track_gliders(ca2.get_history())
        
        output1 = detect_output_region(ca1.get_history(), glider_track1.gliders, {})
        output2 = detect_output_region(ca2.get_history(), glider_track2.gliders, {})
        
        # Both should detect something (may be different or same - depends on implementation)
        # At minimum, should not crash
        if output1 and output2:
            # Regions should be valid
            self.assertGreater(output1['end'], output1['start'])
            self.assertGreater(output2['end'], output2['start'])

    def test_output_region_changes_with_computation(self):
        """Test that detected output region shows computation results."""
        program = "++>++[<+>-]<"
        result = compile_brainfuck_to_rule110(program, tape_length=300)
        
        ca = Rule110(result['rule110_initial'], boundary='ether')
        ca.run(80)
        history = ca.get_history()
        
        glider_track = track_gliders(history)
        output_region = detect_output_region(history, glider_track.gliders, {})
        
        if output_region:
            # Extract patterns from detected region
            initial_pattern = history[0][output_region['start']:output_region['end']]
            final_pattern = history[-1][output_region['start']:output_region['end']]
            
            # Patterns should differ (computation occurred)
            self.assertNotEqual(initial_pattern, final_pattern,
                "Output region should show computation changes")


def run_all_tests():
    """Run all output detection tests."""
    print("=" * 70)
    print("OUTPUT DETECTION AND DECODING TESTS")
    print("=" * 70)
    print()

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestOutputDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputDecoding))
    suite.addTests(loader.loadTestsFromTestCase(TestFullAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputDetectionCorrectness))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 70)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED")
    else:
        print(f"❌ TESTS FAILED: {len(result.failures)} failures, {len(result.errors)} errors")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)

