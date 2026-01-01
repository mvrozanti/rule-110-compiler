#!/usr/bin/env python3
"""
Verify that our collected glider patterns match Cook's specifications.
"""

from rule110 import DynamicRule110
from cook_gliders_exact import COOK_GLIDER_PATTERNS, ETHER_PATTERN


def test_pattern_velocity(pattern: list, expected_velocity: float, name: str) -> dict:
    """Test a single pattern's velocity in ether background."""
    print(f"\nTesting {name}: {''.join(map(str, pattern))}")

    # Create ether background
    ether_repeats = 20
    state = (ETHER_PATTERN * ether_repeats)[:400]

    # Place pattern in ether
    center = len(state) // 2
    start = center - len(pattern) // 2

    for i, bit in enumerate(pattern):
        pos = start + i
        if 0 <= pos < len(state):
            state[pos] = bit

    # Run evolution
    ca = DynamicRule110(state, boundary="ether")
    ca.run(30)  # Enough steps for velocity measurement

    # Track pattern movement
    positions = []

    for step, step_state in enumerate(ca.get_history()):
        # Find active region near where pattern should be
        active_region = []
        for i in range(max(0, center-50), min(len(step_state), center+50)):
            if step_state[i] == 1:
                active_region.append(i)

        if active_region:
            center_pos = sum(active_region) / len(active_region)
            positions.append((step, center_pos))

    if len(positions) < 10:
        print(f"  Pattern disappeared after {len(positions)} steps")
        return {"success": False, "reason": "disappeared"}

    # Calculate velocity
    velocities = []
    for i in range(1, len(positions)):
        step1, pos1 = positions[i-1]
        step2, pos2 = positions[i]
        if step2 > step1:
            vel = (pos2 - pos1) / (step2 - step1)
            velocities.append(vel)

    if not velocities:
        print("  No velocity data")
        return {"success": False, "reason": "no_velocity"}

    avg_velocity = sum(velocities) / len(velocities)
    velocity_std = (sum((v - avg_velocity)**2 for v in velocities) / len(velocities))**0.5

    print(".3f")
    print(".3f")

    # Check if velocity matches expected
    velocity_match = abs(avg_velocity - expected_velocity) < 0.1

    # Check direction
    direction = "right" if avg_velocity > 0.1 else "left" if avg_velocity < -0.1 else "stationary"

    return {
        "success": velocity_match,
        "velocity": avg_velocity,
        "std": velocity_std,
        "direction": direction,
        "steps_tracked": len(positions)
    }


def main():
    """Test all collected Cook glider patterns."""
    print("Verifying Cook glider patterns against specifications...")

    # Cook's specifications
    specs = {
        "A": {"velocity": 2/3, "direction": "right"},
        "B": {"velocity": -1/2, "direction": "left"},
        "C1": {"velocity": 0, "direction": "stationary"},
        "C2": {"velocity": 0, "direction": "stationary"},
        "Ē": {"velocity": -4/15, "direction": "left"}
    }

    results = {}

    for glider_name, pattern in COOK_GLIDER_PATTERNS.items():
        if glider_name in specs:
            spec = specs[glider_name]
            result = test_pattern_velocity(pattern, spec["velocity"], glider_name)
            results[glider_name] = result

            if result["success"]:
                print(f"✓ {glider_name}: VERIFIED - matches Cook specifications")
            else:
                print(f"✗ {glider_name}: FAILED - does not match Cook specifications")
        else:
            print(f"? {glider_name}: No specification available for comparison")

    # Summary
    verified = sum(1 for r in results.values() if r["success"])
    total = len(results)

    print(f"\nSUMMARY: {verified}/{total} patterns verified against Cook specifications")

    if verified == total:
        print("🎉 ALL PATTERNS VERIFIED - We have Cook-faithful glider patterns!")
    else:
        print("⚠️  Some patterns need adjustment to match Cook specifications")

    return results


if __name__ == '__main__':
    main()





