#!/usr/bin/env python3
"""
Test that information flow actually connects input regions to output regions.
"""

from rule110_universal_compiler import compile_brainfuck_to_rule110
from rule110 import Rule110

def test_input_to_output_connection():
    """Test if influence from input regions actually reaches output regions."""
    print("🧪 TESTING INPUT → OUTPUT CONNECTION")
    print("=" * 50)

    # Test with the multiply program that should have clear input/output
    program = "++[>++++++<-]>"  # 2 × 3 = 6
    print(f"Testing program: {program} (2 × 3 = 6)")

    result = compile_brainfuck_to_rule110(program, tape_length=50)
    print(f"Expected result: tape='2', output=''")

    # Run evolution
    ca = Rule110(result['rule110_initial'], boundary="ether")
    ca.run(80)
    history = ca.get_history()

    # Get regions
    input_regions = result.get('regions', {}).get('input-tape', [])
    output_regions = result.get('regions', {}).get('output-tape', [])

    print(f"Input regions: {len(input_regions)}")
    for r in input_regions:
        print(f"  {r['start']}-{r['end']} (center: {(r['start']+r['end'])/2:.1f})")

    print(f"Output regions: {len(output_regions)}")
    for r in output_regions:
        print(f"  {r['start']}-{r['end']} (center: {(r['start']+r['end'])/2:.1f})")

    # Simulate influence propagation (same logic as frontend)
    influenced_cells = set()

    # Step 1: Mark input cells at step 0
    input_region_positions = set()
    for range_data in input_regions:
        for x in range(range_data['start'], range_data['end']):
            input_region_positions.add(x)

    for x in range(len(history[0])):
        if x in input_region_positions and history[0][x]:  # Input cell with data
            influenced_cells.add(f"0-{x}")

    print(f"Initial influenced cells at step 0: {len([c for c in influenced_cells if c.startswith('0-')])}")

    # Step 2: Propagate influence
    width = len(history[0])
    total_propagated = 0

    for step in range(len(history) - 1):
        current_state = history[step]
        next_state = history[step + 1]
        step_propagated = 0

        for x in range(width):
            if next_state[x]:  # Cell is alive in next step
                # Check if influenced by neighbors
                left = x - 1
                center = x
                right = x + 1

                influenced_by_left = left >= 0 and f"{step}-{left}" in influenced_cells
                influenced_by_center = f"{step}-{center}" in influenced_cells
                influenced_by_right = right < width and f"{step}-{right}" in influenced_cells

                if influenced_by_left or influenced_by_center or influenced_by_right:
                    influenced_cells.add(f"{step + 1}-{x}")
                    step_propagated += 1

        if step_propagated > 0:
            total_propagated += step_propagated

    print(f"Total influence propagation: {total_propagated} cells influenced across {len(history)} steps")

    # Check if output region receives influence
    output_receives_influence = False
    influenced_output_cells = []

    for range_data in output_regions:
        for x in range(range_data['start'], range_data['end']):
            # Check final few steps
            for step in range(max(0, len(history) - 10), len(history)):
                if f"{step}-{x}" in influenced_cells:
                    output_receives_influence = True
                    influenced_output_cells.append((step, x))
                    break

    print(f"Output region receives influence: {output_receives_influence}")
    print(f"Influenced output cells: {len(influenced_output_cells)}")
    if influenced_output_cells:
        print(f"Sample influenced output cells: {influenced_output_cells[:5]}")

    # Check connectivity - is there a path from input to output?
    input_positions = set()
    for range_data in input_regions:
        for x in range(range_data['start'], range_data['end']):
            input_positions.add(x)

    output_positions = set()
    for range_data in output_regions:
        for x in range(range_data['start'], range_data['end']):
            output_positions.add(x)

    print(f"Input positions: {sorted(input_positions)}")
    print(f"Output positions: {sorted(output_positions)}")

    # Check if any output position is influenced by input positions
    connected = False
    for step in range(len(history)):
        for out_x in output_positions:
            if f"{step}-{out_x}" in influenced_cells:
                # Check if this output cell could be influenced by input
                # This is a simplified check - in reality the propagation is complex
                connected = True
                print(f"Output cell {out_x} is influenced at step {step}")
                break
        if connected:
            break

    if connected:
        print("✅ INPUT → OUTPUT CONNECTION: Verified!")
    else:
        print("❌ INPUT → OUTPUT CONNECTION: BROKEN!")
        print("The influence propagation does not reach the output region.")

    return connected

def test_simple_increment():
    """Test with simple increment to see if connection works."""
    print("\n🧪 TESTING SIMPLE INCREMENT")
    print("=" * 30)

    program = "+"  # Should increment cell 0 to 1
    result = compile_brainfuck_to_rule110(program, tape_length=30)

    ca = Rule110(result['rule110_initial'], boundary="ether")
    ca.run(30)
    history = ca.get_history()

    input_regions = result.get('regions', {}).get('input-tape', [])
    output_regions = result.get('regions', {}).get('output-tape', [])

    print(f"Input regions: {input_regions}")
    print(f"Output regions: {output_regions}")

    # Check if output regions exist
    if not output_regions:
        print("❌ No output regions detected!")
        return False

    # Simulate influence propagation
    influenced_cells = set()
    width = len(history[0])

    # Mark input
    for range_data in input_regions:
        for x in range(range_data['start'], range_data['end']):
            if history[0][x]:
                influenced_cells.add(f"0-{x}")

    # Propagate
    for step in range(len(history) - 1):
        current_state = history[step]
        next_state = history[step + 1]

        for x in range(width):
            if next_state[x]:
                left = x - 1
                center = x
                right = x + 1

                if (left >= 0 and f"{step}-{left}" in influenced_cells) or \
                   f"{step}-{center}" in influenced_cells or \
                   (right < width and f"{step}-{right}" in influenced_cells):
                    influenced_cells.add(f"{step + 1}-{x}")

    # Check output
    output_influenced = False
    for range_data in output_regions:
        for x in range(range_data['start'], range_data['end']):
            for step in range(len(history)):
                if f"{step}-{x}" in influenced_cells:
                    output_influenced = True
                    break

    if output_influenced:
        print("✅ Simple increment: Input → Output connected!")
    else:
        print("❌ Simple increment: No connection!")

    return output_influenced

def main():
    """Run all tests."""
    print("🔬 INFORMATION FLOW CONNECTIVITY TESTS")
    print("=" * 50)

    test1_passed = test_input_to_output_connection()
    test2_passed = test_simple_increment()

    print("\n" + "=" * 50)
    print("FINAL RESULTS:")
    print(f"Multiply program connection: {'✅' if test1_passed else '❌'}")
    print(f"Simple increment connection: {'✅' if test2_passed else '❌'}")

    if test1_passed and test2_passed:
        print("🎉 All tests passed! Information flow connects input to output.")
    else:
        print("💥 Connection issues detected. The visualization shows flow but doesn't connect input to output.")

if __name__ == "__main__":
    main()
