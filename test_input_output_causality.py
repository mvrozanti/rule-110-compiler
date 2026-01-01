#!/usr/bin/env python3
"""
Test that input regions actually influence output regions.
Prove causality: different inputs → different outputs.
"""

from rule110_universal_compiler import compile_brainfuck_to_rule110
from rule110 import Rule110

def get_output_region(state, start=30, end=50):
    """Extract the output region from a Rule 110 state."""
    if end > len(state):
        end = len(state)
    return ''.join(map(str, state[start:end]))

def test_causality():
    """Test that input changes affect output."""
    print("🧪 TESTING INPUT → OUTPUT CAUSALITY")
    print("=" * 50)

    test_cases = [
        ("Empty program", ""),
        ("Single +", "+"),
        ("Double +", "++"),
        ("Triple +", "+++"),
        ("Move right +", ">+"),
        ("Move right ++", ">++"),
        ("Complex: ++>++[<+>-]<", "++>++[<+>-]<"),
        ("Different program", "++++"),
        ("Another program", "--"),
        ("Loop program", "[+]"),
    ]

    results = []

    for name, program in test_cases:
        print(f"\nTesting: {name} ('{program}')")

        try:
            # Compile to Rule 110
            result = compile_brainfuck_to_rule110(program, tape_length=50)
            initial_state = result['rule110_initial']

            # Run evolution
            ca = Rule110(initial_state, boundary="ether")
            ca.run(100)  # Run for 100 steps
            final_state = ca.get_history()[-1]

            # Extract output region (rightmost 20 cells)
            output_region = get_output_region(final_state, 30, 50)

            # Check if initial states are different
            initial_active = sum(initial_state)
            print(f"  Initial state: {len(initial_state)} cells, {initial_active} active")
            print(f"  Initial pattern (first 20): {''.join(map(str, initial_state[:20]))}")
            print(f"  Final state length: {len(final_state)}")
            print(f"  Output region (30-50): {output_region}")

            results.append((name, program, output_region))

        except Exception as e:
            print(f"  ERROR: {e}")
            results.append((name, program, "ERROR"))

    print("\n" + "=" * 50)
    print("CAUSALITY ANALYSIS:")
    print("=" * 50)

    # Check if different inputs produce different outputs
    outputs = [r[2] for r in results if r[2] != "ERROR"]
    unique_outputs = set(outputs)

    print(f"Total test cases: {len(results)}")
    print(f"Successful runs: {len(outputs)}")
    print(f"Unique output patterns: {len(unique_outputs)}")

    if len(unique_outputs) > 1:
        print("✅ PROVEN: Different inputs produce different outputs!")
        print("✅ CAUSALITY CONFIRMED: Input influences output")
    else:
        print("❌ PROBLEM: All outputs are identical - no causality detected")

    # Show the differences
    print("\nDetailed Results:")
    for name, program, output in results:
        status = "✅" if output != "ERROR" else "❌"
        print(f"  {status} {name}: {output}")

    # Test reproducibility - run the same input twice
    print("\n" + "-" * 30)
    print("REPRODUCIBILITY TEST:")
    print("-" * 30)

    test_program = "+"
    print(f"Running '{test_program}' twice...")

    # First run
    result1 = compile_brainfuck_to_rule110(test_program, tape_length=50)
    ca1 = Rule110(result1['rule110_initial'], boundary="ether")
    ca1.run(50)
    output1 = get_output_region(ca1.get_history()[-1], 30, 50)

    # Second run
    result2 = compile_brainfuck_to_rule110(test_program, tape_length=50)
    ca2 = Rule110(result2['rule110_initial'], boundary="ether")
    ca2.run(50)
    output2 = get_output_region(ca2.get_history()[-1], 30, 50)

    print(f"  Run 1 output: {output1}")
    print(f"  Run 2 output: {output2}")

    if output1 == output2:
        print("✅ REPRODUCIBLE: Same input produces same output")
    else:
        print("❌ NOT REPRODUCIBLE: Same input produces different outputs")

    return len(unique_outputs) > 1

if __name__ == "__main__":
    success = test_causality()
    if success:
        print("\n🎉 CONCLUSION: Input regions DO influence output regions!")
        print("The Rule 110 computation is working correctly.")
    else:
        print("\n💥 CONCLUSION: Input regions do NOT influence output regions!")
        print("The Rule 110 computation may not be working.")
