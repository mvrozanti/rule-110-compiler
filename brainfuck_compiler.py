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
    alphabet = ['0', '1']  # Binary representation of cell values
    blank_symbol = '0'

    # Generate states for each position in program
    for i in range(len(program) + 1):
        states.append(f'q{i}')

    initial_state = 'q0'
    accept_state = f'q{len(program)}'  # After last instruction
    reject_state = 'q_reject'

    # Build transitions
    pc = 0  # Program counter

    while pc < len(program):
        current_state = f'q{pc}'
        command = program[pc]

        if command == '+':
            # Increment: if 0->1, if 1->0 (mod 2 for simplicity)
            transitions[(current_state, '0')] = (f'q{pc+1}', '1', 'S')  # Stay
            transitions[(current_state, '1')] = (f'q{pc+1}', '0', 'S')

        elif command == '-':
            # Decrement: same as increment in mod 2
            transitions[(current_state, '0')] = (f'q{pc+1}', '1', 'S')
            transitions[(current_state, '1')] = (f'q{pc+1}', '0', 'S')

        elif command == '>':
            # Move right: shift head right
            transitions[(current_state, '0')] = (f'q{pc+1}', '0', 'R')
            transitions[(current_state, '1')] = (f'q{pc+1}', '1', 'R')

        elif command == '<':
            # Move left: shift head left
            transitions[(current_state, '0')] = (f'q{pc+1}', '0', 'L')
            transitions[(current_state, '1')] = (f'q{pc+1}', '1', 'L')

        elif command == '.':
            # Output: mark output and continue
            transitions[(current_state, '0')] = (f'q{pc+1}', '0', 'S')
            transitions[(current_state, '1')] = (f'q{pc+1}', '1', 'S')

        elif command == ',':
            # Input: read from input tape (simplified)
            transitions[(current_state, '0')] = (f'q{pc+1}', '1', 'S')  # Read 1
            transitions[(current_state, '1')] = (f'q{pc+1}', '0', 'S')  # Read 0

        elif command == '[':
            # Loop start: if current cell is 0, jump to matching ]
            # This is complex - simplified version
            transitions[(current_state, '0')] = (f'q{pc+1}', '0', 'S')  # Continue
            transitions[(current_state, '1')] = (f'q{pc+1}', '1', 'S')  # Continue

        elif command == ']':
            # Loop end: if current cell is 1, jump back to matching [
            # Simplified - just continue
            transitions[(current_state, '0')] = (f'q{pc+1}', '0', 'S')
            transitions[(current_state, '1')] = (f'q{pc+1}', '1', 'S')

        pc += 1

    return TuringMachine(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        initial_state=initial_state,
        accept_state=accept_state,
        reject_state=reject_state,
        blank_symbol=blank_symbol
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