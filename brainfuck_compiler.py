#!/usr/bin/env python3
"""
Brainfuck to Turing Machine Compiler.

Compiles Brainfuck programs into Turing machine descriptions that can
then be compiled to Rule 110 initial states via Cook's CTS construction.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import re


@dataclass
class TuringMachine:
    """Turing machine description."""
    states: List[str]
    alphabet: List[str]
    transitions: Dict[Tuple[str, str], Tuple[str, str, str]]  # (state, symbol) -> (new_state, new_symbol, move)
    initial_state: str
    accept_state: str
    reject_state: str
    blank_symbol: str
    output_states: List[str]  # States that should output when entered


@dataclass
class TuringTape:
    """Turing machine tape."""
    left: List[str]  # Symbols to the left of head (reversed)
    head: str        # Symbol under head
    right: List[str] # Symbols to the right of head


def parse_brainfuck(program: str) -> TuringMachine:
    """
    Parse Brainfuck program into Turing machine.

    Brainfuck instructions:
    + increment, - decrement, > move right, < move left
    [ start loop, ] end loop, . output, , input
    """
    # Clean program (remove non-BF characters)
    bf_commands = re.findall(r'[+\-<>[\].,]', program)
    program = ''.join(bf_commands)

    # Turing machine components
    states = []
    transitions = {}
    output_states = []  # Track states that should output when entered
    # Use unary encoding: blank/0 = 0, '1' = 1, '11' = 2, '111' = 3, etc.
    # For simplicity in TM representation, we'll use a marker-based approach
    # Each cell value N is represented as N consecutive '1's followed by '0' delimiter
    # But actually, let's use direct digit representation for simplicity (0-9)
    alphabet = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    blank_symbol = '0'

    # Generate states for each position in program
    for i in range(len(program) + 1):
        states.append(f'q{i}')

    initial_state = 'q0'
    accept_state = f'q{len(program)}'  # After last instruction
    reject_state = 'q_reject'

    # Find matching brackets for loops
    bracket_pairs = {}
    bracket_stack = []
    for i, cmd in enumerate(program):
        if cmd == '[':
            bracket_stack.append(i)
        elif cmd == ']':
            if bracket_stack:
                start = bracket_stack.pop()
                bracket_pairs[start] = i
                bracket_pairs[i] = start

    # Build transitions
    pc = 0  # Program counter

    while pc < len(program):
        current_state = f'q{pc}'
        command = program[pc]

        if command == '+':
            # Increment: properly increment digit value
            # 0->1, 1->2, ..., 8->9, 9->0 (wrap around, Brainfuck cells are bytes)
            for digit in range(10):
                digit_char = str(digit)
                next_digit = (digit + 1) % 10
                transitions[(current_state, digit_char)] = (f'q{pc+1}', str(next_digit), 'S')

        elif command == '-':
            # Decrement: properly decrement digit value
            # 0->9 (wrap), 1->0, 2->1, ..., 9->8
            for digit in range(10):
                digit_char = str(digit)
                next_digit = (digit - 1) % 10
                transitions[(current_state, digit_char)] = (f'q{pc+1}', str(next_digit), 'S')

        elif command == '>':
            # Move right: shift head right (works for all digits)
            for digit_char in alphabet:
                transitions[(current_state, digit_char)] = (f'q{pc+1}', digit_char, 'R')

        elif command == '<':
            # Move left: shift head left (works for all digits)
            for digit_char in alphabet:
                transitions[(current_state, digit_char)] = (f'q{pc+1}', digit_char, 'L')

        elif command == '.':
            # Output: mark next state as output state and continue (works for all digits)
            output_states.append(f'q{pc+1}')  # The state we transition TO should output
            for digit_char in alphabet:
                transitions[(current_state, digit_char)] = (f'q{pc+1}', digit_char, 'S')

        elif command == ',':
            # Input: read from input tape (simplified - read first char)
            for digit_char in alphabet:
                transitions[(current_state, digit_char)] = (f'q{pc+1}', '0', 'S')  # Simplified

        elif command == '[':
            # Loop start: if current cell is 0, jump to matching ]
            # Otherwise continue into loop
            if pc in bracket_pairs:
                loop_end = bracket_pairs[pc]
                # If cell is 0, jump to after the loop
                transitions[(current_state, '0')] = (f'q{loop_end+1}', '0', 'S')
                # If cell is non-zero, continue into loop
                for digit_char in alphabet[1:]:  # All digits except '0'
                    transitions[(current_state, digit_char)] = (f'q{pc+1}', digit_char, 'S')
            else:
                # Unmatched bracket - just continue
                for digit_char in alphabet:
                    transitions[(current_state, digit_char)] = (f'q{pc+1}', digit_char, 'S')

        elif command == ']':
            # Loop end: if current cell is non-zero, jump back to matching [
            # Otherwise continue after loop
            if pc in bracket_pairs:
                loop_start = bracket_pairs[pc]
                # If cell is 0, exit loop (continue to next instruction)
                transitions[(current_state, '0')] = (f'q{pc+1}', '0', 'S')
                # If cell is non-zero, jump back to loop start
                for digit_char in alphabet[1:]:  # All digits except '0'
                    transitions[(current_state, digit_char)] = (f'q{loop_start+1}', digit_char, 'S')
            else:
                # Unmatched bracket - just continue
                for digit_char in alphabet:
                    transitions[(current_state, digit_char)] = (f'q{pc+1}', digit_char, 'S')

        pc += 1

    return TuringMachine(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        initial_state=initial_state,
        accept_state=accept_state,
        reject_state=reject_state,
        blank_symbol=blank_symbol,
        output_states=output_states
    )


def execute_turing_machine(tm: TuringMachine, input_tape: str = "",
                          max_steps: int = 1000) -> Tuple[str, str]:
    """
    Execute Turing machine and return final tape and output.

    Returns (final_tape, output_string)
    """
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

        # Check if we're transitioning TO a state that should output
        if hasattr(tm, 'output_states') and new_state in tm.output_states:
            # Output the current cell value before transition
            output.append(current_symbol)

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

        steps += 1

    # Convert tape back to string
    final_tape = ''.join(reversed(tape.left)) + tape.head + ''.join(tape.right)

    return final_tape, ''.join(output)


def compile_brainfuck_to_turing(program: str) -> TuringMachine:
    """Complete Brainfuck to Turing machine compilation."""
    return parse_brainfuck(program)


# Example Brainfuck programs
HELLO_WORLD = """
++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.
"""

SIMPLE_LOOP = """
+++[>++++++<-]>.  # Add 3*6=18, output 18
"""

def test_compilation():
    """Test the Brainfuck compilation."""
    print("Testing Brainfuck → Turing Machine compilation...")

    # Test simple program
    bf_program = "++>+"  # Increment twice, move right, increment
    tm = compile_brainfuck_to_turing(bf_program)

    print(f"Brainfuck: {bf_program}")
    print(f"States: {len(tm.states)}")
    print(f"Transitions: {len(tm.transitions)}")

    # Execute
    final_tape, output = execute_turing_machine(tm, "")
    print(f"Final tape: {final_tape}")
    print(f"Output: {output}")

    return tm


if __name__ == '__main__':
    test_compilation()

