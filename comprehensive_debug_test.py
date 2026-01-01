#!/usr/bin/env python3
"""
Comprehensive debugging and testing of the Brainfuck → Rule 110 compilation pipeline.
Tests each layer systematically and makes wild assumptions about what could be wrong.
"""

import sys
import json
from rule110_universal_compiler import compile_brainfuck_to_rule110
from rule110 import Rule110, DynamicRule110
from glider_tracker import track_gliders, GLIDER_PROPERTIES
from output_detection import analyze_computation_result
import brainfuck_compiler
from turing_to_cts import compile_turing_to_cts, simulate_turing_through_cts
from cts_to_rule110 import compile_cts_to_rule110, simulate_cts_in_rule110

def test_brainfuck_to_tm():
    """Test Brainfuck → Turing Machine compilation"""
    print("=== TESTING BRAINFUCK → TURING MACHINE ===")

    # Test simple increment
    program = "+"
    print(f"Program: {program}")
    tm = brainfuck_compiler.compile_brainfuck_to_turing(program)
    print(f"TM States: {len(tm.states)}")
    print(f"TM Alphabet: {tm.alphabet}")
    print(f"Initial state: {tm.initial_state}")
    print(f"Accept state: {tm.accept_state}")

    # Simulate TM execution
    result = brainfuck_compiler.execute_turing_machine(tm, "")
    print(f"Execution result: {result}")
    print()

def test_simple_programs():
    """Test simple programs that should have predictable outputs"""
    print("=== TESTING SIMPLE PROGRAMS ===")

    test_cases = [
        ("+", "Should increment cell 0 to '1'"),
        ("++", "Should increment cell 0 to '2'"),
        ("+++", "Should increment cell 0 to '3'"),
        (">+", "Should increment cell 1 to '1'"),
        ("<+", "Should increment cell 0 to '1' (underflow handling)"),
        ("+", "Basic increment test"),
        ("++>++[<+>-]<", "2+2 should give 4"),
    ]

    for program, description in test_cases:
        print(f"Testing: {program} - {description}")
        try:
            result = compile_brainfuck_to_rule110(program, tape_length=50)

            print(f"  TM Tape: {result['verification']['tm_tape']}")
            print(f"  TM Output: {result['verification']['tm_output']}")

            # Run Rule 110 evolution
            ca = Rule110(result['rule110_initial'], boundary="ether")
            ca.run(40)  # Shorter run for testing
            history = ca.get_history()

            # Track gliders
            glider_track = track_gliders(history)

            print(f"  Rule 110 length: {len(result['rule110_initial'])}")
            print(f"  Evolution steps: {len(history)}")
            print(f"  Gliders detected: {len(glider_track.gliders)}")

            # Check for obvious issues
            if len(result['rule110_initial']) == 0:
                print("  ❌ ERROR: Rule 110 initial state is empty!")
            if len(history) < 2:
                print("  ❌ ERROR: Evolution didn't run!")
            if len(glider_track.gliders) == 0:
                print("  ⚠️  WARNING: No gliders detected")

        except Exception as e:
            print(f"  ❌ ERROR: {e}")

        print()

def test_wild_assumptions():
    """Test wild assumptions about what could be wrong"""
    print("=== TESTING WILD ASSUMPTIONS ===")

    # Assumption 1: Tape length is wrong
    print("Wild Assumption 1: Tape length affects compilation")
    for tape_len in [10, 50, 100, 200, 500]:
        try:
            result = compile_brainfuck_to_rule110("+", tape_length=tape_len)
            print(f"  Tape length {tape_len}: Rule 110 length {len(result['rule110_initial'])}")
        except Exception as e:
            print(f"  Tape length {tape_len}: ERROR {e}")

    # Assumption 2: Rule 110 evolution is wrong
    print("\nWild Assumption 2: Rule 110 evolution is buggy")
    ca = Rule110([0, 0, 1, 1, 1, 0, 0, 0], boundary="ether")
    ca.run(10)
    history = ca.get_history()
    print(f"  Test pattern evolution length: {len(history)}")
    print(f"  Final state: {history[-1]}")

    # Assumption 3: Glider patterns are wrong
    print("\nWild Assumption 3: Glider pattern detection is wrong")
    from glider_tracker import COOK_GLIDER_PATTERNS
    print(f"  Known glider patterns: {list(COOK_GLIDER_PATTERNS.keys())}")
    for name, pattern in COOK_GLIDER_PATTERNS.items():
        print(f"    {name}: {pattern}")

    # Assumption 4: Output detection is completely wrong
    print("\nWild Assumption 4: Output detection logic is flawed")
    test_state = [0, 1, 1, 1, 0, 0, 0, 1, 1, 0]
    regions = {"input-tape": [{"start": 0, "end": 5}], "output-tape": [{"start": 5, "end": 10}]}
    analysis = analyze_computation_result([test_state], [], regions, None)
    print(f"  Test analysis: {analysis}")

    # Assumption 5: Compilation produces garbage
    print("\nWild Assumption 5: Compilation produces random data")
    result = compile_brainfuck_to_rule110("+++", tape_length=20)
    initial = result['rule110_initial']
    print(f"  Initial state: {initial}")
    print(f"  Non-zero cells: {sum(1 for x in initial if x != 0)}")
    print(f"  Entropy (rough): {len(set(initial))} unique values")

def test_glider_properties():
    """Test that glider properties are correct"""
    print("=== TESTING GLIDER PROPERTIES ===")

    print("Known glider types and properties:")
    for glider_type, props in GLIDER_PROPERTIES.items():
        print(f"  {glider_type}: velocity={props.get('velocity', 'unknown')}, period={props.get('period', 'unknown')}")

    # Test actual glider patterns
    print("\nActual glider patterns:")
    from glider_tracker import COOK_GLIDER_PATTERNS
    for name, pattern in COOK_GLIDER_PATTERNS.items():
        print(f"  {name}: {pattern}")

def test_end_to_end():
    """Test end-to-end compilation with manual verification"""
    print("=== TESTING END-TO-END COMPILATION ===")

    # Manual verification: what should "+" produce?
    print("Manual verification for '+' program:")
    print("Brainfuck '+': increment cell 0 by 1")
    print("Expected: cell 0 = '1' (in unary/decimal representation)")

    result = compile_brainfuck_to_rule110("+", tape_length=20)
    print(f"TM Tape: {result['verification']['tm_tape']}")
    print(f"TM Output: {result['verification']['tm_output']}")

    # Run evolution
    ca = Rule110(result['rule110_initial'], boundary="ether")
    ca.run(30)
    history = ca.get_history()
    final_state = history[-1]

    print(f"Final Rule 110 state length: {len(final_state)}")
    print(f"Active cells in final state: {sum(final_state)}")

    # Check if output detection finds anything
    regions = result.get('regions', {})
    if 'output-tape' in regions:
        output_ranges = regions['output-tape']
        print(f"Output regions: {output_ranges}")
        for r in output_ranges:
            output_pattern = final_state[r['start']:r['end']]
            print(f"  Output pattern: {output_pattern}")
    else:
        print("No output regions detected")

def main():
    """Run all tests"""
    print("COMPREHENSIVE BRAINFUCK → RULE 110 DEBUGGING")
    print("=" * 50)

    test_brainfuck_to_tm()
    test_simple_programs()
    test_wild_assumptions()
    test_glider_properties()
    test_end_to_end()

    print("=" * 50)
    print("DEBUGGING COMPLETE")

if __name__ == "__main__":
    main()
