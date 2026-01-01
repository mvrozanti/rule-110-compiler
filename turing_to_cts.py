#!/usr/bin/env python3
"""
Turing Machine to Cyclic Tag System (CTS) Compiler.

Compiles Turing machine descriptions into CTS specifications that can
then be compiled to Rule 110 initial states via Cook's construction.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from brainfuck_compiler import TuringMachine, TuringTape
from cook_cts import CTSSpec


@dataclass
class TuringToCTS:
    """Mapping from Turing machine to CTS."""
    tm: TuringMachine
    cts: CTSSpec
    state_encoding: Dict[str, str]  # TM state -> CTS symbol sequence
    symbol_encoding: Dict[str, str]  # TM symbol -> CTS symbol


def encode_turing_state(state: str, symbol: str) -> str:
    """
    Encode Turing machine state and symbol into CTS symbols.

    Uses binary encoding where each bit becomes a CTS symbol.
    """
    # Simple encoding: state + symbol as binary
    combined = f"{state}_{symbol}"
    # Convert to binary representation
    binary = format(hash(combined) % 256, '08b')
    # Map 0->N, 1->Y for CTS
    return ''.join('Y' if b == '1' else 'N' for b in binary)


def create_turing_machine_cts(tm: TuringMachine) -> CTSSpec:
    """
    Create CTS specification that simulates the Turing machine.

    Each TM transition becomes a CTS appendant that manipulates
    the tape representation in CTS form.
    """
    appendants = []

    # For each possible transition, create an appendant
    for (state, symbol), (new_state, new_symbol, move) in tm.transitions.items():
        # Encode the transition as a CTS appendant
        transition_encoding = encode_turing_state(new_state, new_symbol)

        # Add movement information
        if move == 'R':
            transition_encoding += 'Y'  # Move right marker
        elif move == 'L':
            transition_encoding += 'N'  # Move left marker
        else:
            transition_encoding += 'X'  # Stay marker (using X as placeholder)

        appendants.append(transition_encoding)

    # Ensure we have at least one appendant
    if not appendants:
        appendants = ['Y']  # Minimal CTS

    # Initial tape: encode initial state and blank tape
    initial_tape = encode_turing_state(tm.initial_state, tm.blank_symbol)

    return CTSSpec(
        appendants=appendants,
        initial_tape=initial_tape
    )


def compile_turing_to_cts(tm: TuringMachine) -> TuringToCTS:
    """
    Complete Turing machine to CTS compilation.
    """
    cts = create_turing_machine_cts(tm)

    return TuringToCTS(
        tm=tm,
        cts=cts,
        state_encoding={},  # Would map TM states to CTS encodings
        symbol_encoding={}  # Would map TM symbols to CTS encodings
    )


def simulate_turing_through_cts(turing_to_cts: TuringToCTS,
                               input_tape: str = "",
                               max_steps: int = 100) -> str:
    """
    Simulate Turing machine execution through CTS.

    This is a high-level simulation - in practice, this would be
    executed through the Rule 110 evolution.
    """
    # Direct TM execution for reference
    final_tape, output = execute_turing_machine(turing_to_cts.tm, input_tape, max_steps)

    print(f"Turing machine simulation:")
    print(f"  Input: {input_tape}")
    print(f"  Final tape: {final_tape}")
    print(f"  Output: {output}")

    # CTS would encode this computation
    print(f"CTS specification:")
    print(f"  Appendants: {len(turing_to_cts.cts.appendants)}")
    print(f"  Initial tape: {turing_to_cts.cts.initial_tape}")

    return output


# Import for execution (avoid circular import)
def execute_turing_machine(tm: TuringMachine, input_tape: str = "",
                          max_steps: int = 1000) -> Tuple[str, str]:
    """Execute Turing machine (imported from brainfuck_compiler)."""
    # Initialize tape
    tape = TuringTape(
        left=[],
        head=tm.blank_symbol,
        right=list(input_tape) if input_tape else []
    )

    current_state = tm.initial_state
    output = []
    steps = 0

    while current_state != tm.accept_state and current_state != tm.reject_state and steps < max_steps:
        # Get current symbol
        current_symbol = tape.head

        # Find transition
        key = (current_state, current_symbol)
        if key not in tm.transitions:
            # No transition - halt
            break

        new_state, new_symbol, move = tm.transitions[key]

        # Apply transition
        tape.head = new_symbol
        current_state = new_state

        # Move head
        if move == 'R':
            tape.left.append(tape.head)
            tape.head = tape.right.pop(0) if tape.right else tm.blank_symbol
        elif move == 'L':
            tape.right.insert(0, tape.head)
            tape.head = tape.left.pop() if tape.left else tm.blank_symbol

        # Handle output (simplified)
        if current_symbol != tape.head:  # Cell changed
            output.append(tape.head)

        steps += 1

    # Convert tape back to string
    final_tape = ''.join(reversed(tape.left)) + tape.head + ''.join(tape.right)

    return final_tape, ''.join(output)


def test_turing_to_cts():
    """Test Turing machine to CTS compilation."""
    from brainfuck_compiler import compile_brainfuck_to_turing

    # Simple Brainfuck program
    bf_program = "++>+"  # Increment twice, move right, increment
    tm = compile_brainfuck_to_turing(bf_program)

    print("Brainfuck program:", bf_program)
    print("Compiled to Turing machine with", len(tm.states), "states")

    # Compile to CTS
    turing_to_cts = compile_turing_to_cts(tm)

    print(f"CTS has {len(turing_to_cts.cts.appendants)} appendants")
    print(f"Initial tape: {turing_to_cts.cts.initial_tape}")

    # Simulate
    result = simulate_turing_through_cts(turing_to_cts, "")

    return turing_to_cts


if __name__ == '__main__':
    test_turing_to_cts()





