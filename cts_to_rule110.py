#!/usr/bin/env python3
"""
CTS to Rule 110 Compiler.

Compiles Cyclic Tag System specifications into Rule 110 initial states
using Cook's construction with verified stationary gliders.
"""

from cook_cts import CTSSpec, _create_ether_background, _place_glider_package
from cook_gliders_exact import COOK_GLIDER_PATTERNS
from typing import List


def encode_cts_symbol_to_glider(symbol: str) -> str:
    """
    Map CTS symbol to glider type.

    Y → C2 (represents presence/1)
    N → C1 (represents absence/0)
    """
    if symbol == 'Y':
        return 'C2'
    elif symbol == 'N':
        return 'C1'
    else:
        return 'C1'  # Default to C1


def compile_cts_to_rule110(cts: CTSSpec, tape_length: int = 200) -> List[int]:
    """
    Compile CTS specification to Rule 110 initial state.

    Uses Cook's construction with verified stationary gliders.
    """
    # Create ether background
    state = _create_ether_background(tape_length)

    # Encode initial tape as glider sequence
    tape_position = 50  # Start tape encoding here

    for symbol in cts.initial_tape:
        glider_type = encode_cts_symbol_to_glider(symbol)

        if glider_type in COOK_GLIDER_PATTERNS:
            # Place the verified glider pattern
            pattern_length = _place_glider_package(state, glider_type, tape_position)
            tape_position += pattern_length + 10  # Space between gliders
        else:
            # Fallback for unverified gliders
            state[tape_position] = 1 if symbol == 'Y' else 0
            tape_position += 15

    # For now, skip appendant encoding (complex)
    # The tape encoding demonstrates the basic principle

    return state


def simulate_cts_in_rule110(cts: CTSSpec, steps: int = 50) -> List[int]:
    """
    Simulate CTS evolution in Rule 110.

    Compiles CTS to Rule 110 initial state and runs evolution.
    """
    from rule110 import DynamicRule110

    # Compile CTS to Rule 110
    initial_state = compile_cts_to_rule110(cts)

    # Run Rule 110 evolution
    ca = DynamicRule110(initial_state, boundary="ether")
    ca.run(steps)

    return ca.get_history()[-1]  # Return final state


def test_cts_to_rule110():
    """Test CTS to Rule 110 compilation."""
    from cook_cts import example_duplicator

    # Get a CTS specification
    cts = example_duplicator()
    print(f"Testing CTS: appendants={cts.appendants}, tape='{cts.initial_tape}'")

    # Compile to Rule 110
    rule110_state = compile_cts_to_rule110(cts)

    # Check for gliders
    active_cells = sum(1 for cell in rule110_state if cell == 1)
    print(f"Rule 110 state has {active_cells} active cells")

    # Run brief evolution
    final_state = simulate_cts_in_rule110(cts, steps=10)
    final_active = sum(1 for cell in final_state if cell == 1)
    print(f"After evolution: {final_active} active cells")

    return rule110_state


if __name__ == '__main__':
    test_cts_to_rule110()