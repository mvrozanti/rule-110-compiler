#!/usr/bin/env python3
"""
Debug the output detection logic specifically.
"""

from rule110_universal_compiler import compile_brainfuck_to_rule110
from rule110 import Rule110
from glider_tracker import track_gliders
from output_detection import detect_output_region

def debug_output_detection():
    """Debug output detection for a simple program"""
    print("=== DEBUGGING OUTPUT DETECTION ===")

    # Test with '+' program
    program = "+"
    print(f"Testing program: {program}")

    result = compile_brainfuck_to_rule110(program, tape_length=50)
    print(f"Rule 110 initial state length: {len(result['rule110_initial'])}")

    # Run evolution
    ca = Rule110(result['rule110_initial'], boundary="ether")
    ca.run(40)
    history = ca.get_history()
    print(f"Evolution steps: {len(history)}")

    # Track gliders
    glider_track = track_gliders(history)
    print(f"Gliders detected: {len(glider_track.gliders)}")

    # Debug glider information
    print("\nGlider details:")
    for i, glider in enumerate(glider_track.gliders[:5]):  # First 5 gliders
        print(f"  Glider {i}: type={glider.glider_type}, pos={glider.position:.1f}, start={glider.step_first_seen}, end={glider.step_last_seen}")

    # Get regions from server-style processing
    from server import identify_glider_regions

    # Identify regions in initial state
    initial_regions = identify_glider_regions(result['rule110_initial'])

    # Convert to the format expected by output detection
    region_ranges_for_detection = {}
    current_type = None
    current_start = None
    for i in range(len(result['rule110_initial'])):
        cell_type = initial_regions.get(i, 'unknown')
        if cell_type != current_type:
            if current_type and current_start is not None:
                if current_type not in region_ranges_for_detection:
                    region_ranges_for_detection[current_type] = []
                region_ranges_for_detection[current_type].append({
                    'start': current_start,
                    'end': i
                })
            current_type = cell_type
            current_start = i
    # Add final region
    if current_type and current_start is not None:
        if current_type not in region_ranges_for_detection:
            region_ranges_for_detection[current_type] = []
        region_ranges_for_detection[current_type].append({
            'start': current_start,
            'end': len(result['rule110_initial'])
        })

    print(f"\nRegions: {list(region_ranges_for_detection.keys())}")

    for region_type, ranges in region_ranges_for_detection.items():
        print(f"  {region_type}: {len(ranges)} ranges")
        for r in ranges[:2]:
            print(f"    {r['start']}-{r['end']}")

    # Test output detection
    print("\n=== TESTING OUTPUT DETECTION ===")
    output_region = detect_output_region(history, glider_track.gliders, region_ranges_for_detection)

    if output_region:
        print(f"Output region detected: {output_region}")
    else:
        print("No output region detected!")

    # Manual inspection of final state
    final_state = history[-1]
    print("\nFinal state (last 20 cells):", final_state[-20:])

    # Look for any gliders in final state manually
    print("\nChecking for glider patterns in final state...")
    from glider_tracker import COOK_GLIDER_PATTERNS

    found_patterns = []
    for pos in range(len(final_state) - 20, len(final_state)):
        for glider_type, pattern in COOK_GLIDER_PATTERNS.items():
            if pos + len(pattern) <= len(final_state):
                if final_state[pos:pos+len(pattern)] == pattern:
                    found_patterns.append((glider_type, pos))

    if found_patterns:
        print(f"Found glider patterns: {found_patterns}")
    else:
        print("No glider patterns found in final state")

if __name__ == "__main__":
    debug_output_detection()
