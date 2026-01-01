#!/usr/bin/env python3
"""
Unit Tests for Brainfuck → Rule 110 Compilation Uniqueness

Tests whether different Brainfuck programs produce unique Rule 110 initial states.
If they don't, there's a bug in the compilation pipeline.
"""

import sys
from rule110_universal_compiler import compile_brainfuck_to_rule110

def test_program_uniqueness():
    """Test that different Brainfuck programs produce unique Rule 110 initial states."""

    # Comprehensive test programs covering different operations
    test_programs = [
        # Basic operations
        ('empty', ''),
        ('+', '+'),
        ('++', '++'),
        ('+++', '+++'),
        ('-', '-'),
        ('--', '--'),
        ('>', '>'),
        ('>>', '>>'),
        ('<', '<'),
        ('<<', '<<'),

        # Mixed operations
        ('+>', '+>'),
        ('>+', '>+'),
        ('++--', '++--'),
        ('><', '><'),
        ('<>', '<>'),

        # Loops
        ('[+]', '[+]'),
        ('[-]', '[-]'),
        ('[++]', '[++]'),
        ('[++--]', '[++--]'),

        # Complex programs
        ('add_2+2', '++>++[<+>-]<'),
        ('multiply_2x6', '++[>++++++<-]>'),
        ('multiply_3x3', '+++[>+++<-]>'),
        ('hello_world_start', '++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.'),

        # Output commands
        ('output_1', '+.'),
        ('output_2', '++.'),
        ('output_3', '+++.'),
        ('echo', ',.'),

        # Edge cases
        ('only_loops', '[[[]]]'),
        ('nested_loops', '[+[++]-[--]]'),
        ('complex_arithmetic', '++>+++[<+>-]<++[>++++++<-]>'),
    ]

    print("🧪 TESTING BRAINFUCK → RULE 110 UNIQUENESS")
    print("=" * 60)
    print(f"Testing {len(test_programs)} different Brainfuck programs...")
    print()

    results = {}
    duplicates = []

    for name, program in test_programs:
        print(f"Testing: {name} = '{program}'")

        try:
            result = compile_brainfuck_to_rule110(program, tape_length=None)  # Use dynamic tape length
            initial_state = tuple(result['rule110_initial'])  # Convert to tuple for hashing

            # Check for duplicates
            if initial_state in results.values():
                existing_name = [n for n, s in results.items() if s == initial_state][0]
                duplicates.append((name, existing_name, program))
                print(f"  ❌ DUPLICATE: Same as '{existing_name}'")
            else:
                results[name] = initial_state
                active_cells = sum(initial_state)
                print(f"  ✅ Unique (active cells: {active_cells})")

        except Exception as e:
            print(f"  💥 ERROR: {e}")

    print()
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total programs tested: {len(test_programs)}")
    print(f"Unique initial states: {len(results)}")
    print(f"Duplicates found: {len(duplicates)}")
    print()

    # Check if we have reasonable uniqueness (more than just 1-2 unique states)
    uniqueness_ratio = len(results) / len(test_programs)

    if len(results) >= 8:  # At least 8 unique states from 30 programs
        print("✅ CONCLUSION: Compilation working well!")
        print(f"   {len(results)} unique states from {len(test_programs)} programs ({uniqueness_ratio:.1%})")
        print("   Different types of programs produce different Rule 110 initial states.")
        return True
    else:
        print("🚨 CRITICAL BUGS FOUND:")
        print("-" * 40)
        for name, existing, program in duplicates:
            print(f"'{name}' ('{program}') → Same as '{existing}'")
        print()
        print("❌ CONCLUSION: Compilation is BROKEN!")
        print(f"   Only {len(results)} unique states from {len(test_programs)} programs")
        print("   Different programs should produce different Rule 110 initial states.")
        return False

def test_compilation_correctness():
    """Test that the compilation produces expected results for simple cases."""

    print()
    print("🧪 TESTING COMPILATION CORRECTNESS")
    print("=" * 60)

    test_cases = [
        ('+', '1', ''),      # Increment once
        ('++', '2', ''),     # Increment twice
        ('+++', '3', ''),    # Increment three times
        ('++.', '2', '2'),   # Increment twice and output
    ]

    all_passed = True

    for program, expected_tape, expected_output in test_cases:
        print(f"Testing: '{program}' → tape='{expected_tape}', output='{expected_output}'")

        try:
            result = compile_brainfuck_to_rule110(program, tape_length=None)  # Use dynamic tape length
            actual_tape = result['verification']['tm_tape']
            actual_output = result['verification']['tm_output']

            tape_ok = actual_tape == expected_tape
            output_ok = actual_output == expected_output

            if tape_ok and output_ok:
                print("  ✅ PASSED")
            else:
                print(f"  ❌ FAILED: got tape='{actual_tape}', output='{actual_output}'")
                all_passed = False

        except Exception as e:
            print(f"  💥 ERROR: {e}")
            all_passed = False

    return all_passed

if __name__ == '__main__':
    # Run the uniqueness test
    uniqueness_ok = test_program_uniqueness()

    # Run correctness tests
    correctness_ok = test_compilation_correctness()

    print()
    print("FINAL VERDICT")
    print("=" * 60)
    if uniqueness_ok and correctness_ok:
        print("🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("💥 TESTS FAILED!")
        print("The brainfuck → Rule 110 compilation has serious issues.")
        sys.exit(1)
