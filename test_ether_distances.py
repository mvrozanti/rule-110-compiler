"""
Tests for Cook's ! and ! distance calculations.
"""

import unittest
from ether_distances import (
    get_ether_triangle_row, get_ether_triangle_column,
    calculate_over_distance, calculate_under_distance,
    position_glider_at_over_distance, position_glider_at_under_distance,
    validate_cook_distances
)


class TestEtherTriangleCalculations(unittest.TestCase):
    """Test basic ether triangle distance calculations."""

    def test_ether_triangle_row(self):
        """Test diagonal ether row calculations."""
        # Test basic row calculations
        self.assertEqual(get_ether_triangle_row(0), 0)
        self.assertEqual(get_ether_triangle_row(7), 1)  # 7 cells per diagonal step
        self.assertEqual(get_ether_triangle_row(14), 2)

    def test_ether_triangle_column(self):
        """Test vertical ether column calculations."""
        # Ether pattern is 14 cells long
        self.assertEqual(get_ether_triangle_column(0), 0)
        self.assertEqual(get_ether_triangle_column(14), 1)
        self.assertEqual(get_ether_triangle_column(28), 2)

    def test_over_distance_calculation(self):
        """Test ! distance calculations."""
        # Test basic over distances
        dist1 = calculate_over_distance(0, 7)  # One diagonal step
        self.assertEqual(dist1, 1)

        dist2 = calculate_over_distance(7, 14)  # Another step
        self.assertEqual(dist2, 1)

        # Test mod 6 (for Ē gliders)
        dist3 = calculate_over_distance(0, 42)  # 6 steps = 0 mod 6
        self.assertEqual(dist3, 0)

    def test_under_distance_calculation(self):
        """Test ! distance calculations."""
        # Test basic under distances
        dist1 = calculate_under_distance(0, 14)  # One ether period
        self.assertEqual(dist1, 1)

        dist2 = calculate_under_distance(14, 28)  # Another period
        self.assertEqual(dist2, 1)

        # Test mod 4 (for Ē gliders)
        dist3 = calculate_under_distance(0, 56)  # 4 periods = 0 mod 4
        self.assertEqual(dist3, 0)

    def test_position_at_over_distance(self):
        """Test positioning glider at ! distance."""
        pos = position_glider_at_over_distance(0, 2)  # !2 from position 0
        # Should be approximately 14 cells away (2 * 7)
        self.assertGreater(pos, 10)
        self.assertLess(pos, 20)

    def test_position_at_under_distance(self):
        """Test positioning glider at ! distance."""
        pos = position_glider_at_under_distance(0, 1)  # !1 from position 0
        # Should be approximately 14 cells away (1 ether period)
        self.assertGreater(pos, 10)
        self.assertLess(pos, 18)


class TestCookDistanceValidation(unittest.TestCase):
    """Test Cook's distance constraint validation."""

    def test_valid_c2_spacing(self):
        """Test valid C2 glider spacing (!2 apart)."""
        # C2 gliders at positions that should be !2 apart
        glider_positions = [
            ("C2", 0),
            ("C2", 14),  # Should be !2 from first
            ("Ē", 50)
        ]

        # This should pass Cook's validation
        result = validate_cook_distances(glider_positions)
        self.assertTrue(result)

    def test_invalid_c2_spacing(self):
        """Test invalid C2 glider spacing."""
        # C2 gliders too close together
        glider_positions = [
            ("C2", 0),
            ("C2", 7),  # Wrong spacing
        ]

        result = validate_cook_distances(glider_positions)
        self.assertFalse(result)

    def test_valid_e_spacing(self):
        """Test valid Ē glider spacing (!4 apart)."""
        glider_positions = [
            ("Ē", 0),
            ("Ē", 28),  # Should be !4 from first
        ]

        result = validate_cook_distances(glider_positions)
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()