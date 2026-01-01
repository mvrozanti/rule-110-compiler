#!/usr/bin/env python3
"""
Test the known working C1 and C2 patterns to validate the testing method.
"""

from verify_cook_patterns import test_pattern_velocity

# Test the patterns that we know work
C1_PATTERN = [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0]
C2_PATTERN = [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0]

print("Testing known working patterns...")

# Test C1 (should be stationary, velocity 0)
c1_result = test_pattern_velocity(C1_PATTERN, 0, "C1")
print(f"C1 result: {c1_result}")

# Test C2 (should be stationary, velocity 0)
c2_result = test_pattern_velocity(C2_PATTERN, 0, "C2")
print(f"C2 result: {c2_result}")

print("\nIf these work, the testing method is valid.")
print("If they don't, there's a bug in the testing.")






