#!/usr/bin/env python3
"""
Find Cook's exact glider patterns by simulation.

Runs Rule 110 with random initial states and extracts stable moving patterns
that match Cook's glider descriptions (velocities, periods, widths).
"""

import random
from collections import defaultdict
from rule110 import Rule110, DynamicRule110


def find_moving_patterns():
    """Find stable moving patterns in Rule 110 evolution."""
    patterns_found = defaultdict(list)

    # Run many simulations with random initial states
    for trial in range(100):
        # Create random initial state with some density
        initial = [1 if random.random() < 0.3 else 0 for _ in range(200)]
        ca = DynamicRule110(initial, boundary="ether")

        # Run for many steps to let patterns stabilize
        ca.run(200)

        # Look for stable moving patterns in later evolution
        for step in range(100, 200, 10):  # Sample every 10 steps
            state = ca.get_history()[step]

            # Scan for potential gliders (dense active regions)
            pos = 0
            while pos < len(state) - 20:
                # Look for active region
                if state[pos] == 1:
                    # Find extent of active region
                    start = pos
                    while pos < len(state) and state[pos] == 1:
                        pos += 1
                    end = pos

                    width = end - start
                    if 5 <= width <= 25:  # Reasonable glider width range
                        pattern = state[max(0, start-5):min(len(state), end+5)]
                        # Pad to consistent length for comparison
                        if len(pattern) >= 10:
                            pattern_key = tuple(pattern[:15])  # First 15 bits as key
                            patterns_found[pattern_key].append((step, start, pattern))

                pos += 1

    # Filter for patterns that appear multiple times (stable)
    stable_patterns = {}
    for pattern_key, occurrences in patterns_found.items():
        if len(occurrences) >= 3:  # Appears in multiple trials/steps
            # Take the most common pattern
            patterns = [occ[2] for occ in occurrences]
            # Find most common length
            lengths = [len(p) for p in patterns]
            common_length = max(set(lengths), key=lengths.count)

            # Average similar patterns
            similar = [p for p in patterns if len(p) == common_length]
            if similar:
                avg_pattern = []
                for i in range(common_length):
                    ones = sum(1 for p in similar if i < len(p) and p[i] == 1)
                    avg_pattern.append(1 if ones > len(similar)/2 else 0)

                stable_patterns[pattern_key] = avg_pattern

    return stable_patterns


def analyze_patterns(patterns):
    """Analyze found patterns for Cook glider characteristics."""
    print(f"Found {len(patterns)} stable patterns")

    candidates = {}

    for i, (key, pattern) in enumerate(patterns.items()):
        print(f"\nPattern {i}: length {len(pattern)}")
        print(f"Bits: {''.join(map(str, pattern))}")

        # Analyze properties
        active_cells = sum(pattern)
        density = active_cells / len(pattern)

        # Look for periodic structure (ether background suggests this)
        period_14 = check_periodicity(pattern, 14)
        period_7 = check_periodicity(pattern, 7)

        print(f"Active cells: {active_cells}, Density: {density:.2f}")
        print(f"Period 14 correlation: {period_14:.2f}")
        print(f"Period 7 correlation: {period_7:.2f}")

        # Classify based on Cook's descriptions
        if density > 0.4 and period_14 > 0.3:
            candidates[f"A_candidate_{i}"] = pattern
            print("→ Possible A/B glider (dense, periodic)")
        elif density > 0.2 and active_cells < 15:
            candidates[f"C_candidate_{i}"] = pattern
            print("→ Possible C glider (moderate density)")
        elif density < 0.3:
            candidates[f"E_candidate_{i}"] = pattern
            print("→ Possible Ē glider (sparse)")

    return candidates


def check_periodicity(pattern, period):
    """Check how well a pattern matches a given period."""
    if len(pattern) < period * 2:
        return 0.0

    matches = 0
    total = 0

    for i in range(len(pattern) - period):
        if pattern[i] == pattern[i + period]:
            matches += 1
        total += 1

    return matches / total if total > 0 else 0.0


def test_glider_movement(pattern, steps=50):
    """Test if a pattern moves like a glider."""
    # Place pattern in ether background
    ether_pattern = [0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0]
    state = ether_pattern * 10  # Ether background

    # Place pattern in center
    center = len(state) // 2
    for i, bit in enumerate(pattern):
        if center + i < len(state):
            state[center + i] = bit

    ca = DynamicRule110(state, boundary="ether")
    ca.run(steps)

    # Track pattern center over time
    centers = []
    for step_state in ca.get_history():
        # Find active region center
        active_positions = [i for i, bit in enumerate(step_state) if bit == 1]
        if active_positions:
            center_pos = sum(active_positions) / len(active_positions)
            centers.append(center_pos)

    if len(centers) >= 10:
        # Check if moving at constant velocity
        velocities = []
        for i in range(1, len(centers)):
            vel = centers[i] - centers[i-1]
            velocities.append(vel)

        avg_velocity = sum(velocities) / len(velocities)
        velocity_std = (sum((v - avg_velocity)**2 for v in velocities) / len(velocities))**0.5

        print(f"Average velocity: {avg_velocity:.3f}, Std: {velocity_std:.3f}")

        # Classify based on velocity (Cook's values)
        if abs(avg_velocity - 2/3) < 0.1:
            return "A_glider"
        elif abs(avg_velocity + 0.5) < 0.1:
            return "B_glider"
        elif abs(avg_velocity) < 0.05:
            return "C_glider"
        elif abs(avg_velocity + 4/15) < 0.1:
            return "E_glider"
        else:
            return f"unknown_velocity_{avg_velocity:.2f}"

    return "no_movement"


if __name__ == '__main__':
    print("Searching for Cook's glider patterns...")

    # Find stable patterns
    patterns = find_moving_patterns()
    candidates = analyze_patterns(patterns)

    print(f"\n=== Testing {len(candidates)} Candidates ===")

    cook_gliders = {}
    for name, pattern in candidates.items():
        print(f"\nTesting {name}...")
        classification = test_glider_movement(pattern)
        print(f"Classification: {classification}")

        if not classification.startswith("unknown") and not classification.startswith("no"):
            cook_gliders[name] = {
                'pattern': pattern,
                'type': classification,
                'length': len(pattern)
            }

    print(f"\n=== Found {len(cook_gliders)} Potential Cook Gliders ===")
    for name, data in cook_gliders.items():
        print(f"{name}: {data['type']}, length {data['length']}")
        print(f"  Pattern: {''.join(map(str, data['pattern']))}")





