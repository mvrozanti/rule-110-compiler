#!/usr/bin/env python3
"""
Rule 110 Compiler - Main entry point

This compiler takes programs and converts them to Rule 110 initial states,
then executes and visualizes the result.
"""

import argparse
import sys
import re
from rule110 import Rule110, Rule110Compiler, visualize
from operations import OperationLanguage, OperationExecutor


def main():
    parser = argparse.ArgumentParser(
        description='Rule 110 Compiler - Compile programs to Rule 110 automaton'
    )
    parser.add_argument('program', nargs='?', help='Program to compile (pattern name, binary string, or code)')
    parser.add_argument('-s', '--steps', type=int, default=50, help='Number of steps to run (default: 50)')
    parser.add_argument('-w', '--width', type=int, help='Width of the initial state')
    parser.add_argument('-v', '--visualize', action='store_true', default=True, help='Visualize the evolution')
    parser.add_argument('-o', '--output', help='Output file for the evolution history')
    parser.add_argument('-l', '--list-patterns', action='store_true', help='List available patterns')
    parser.add_argument('--char-alive', default='█', help='Character for alive cells (default: █)')
    parser.add_argument('--char-dead', default=' ', help='Character for dead cells (default: space)')
    parser.add_argument('--op', action='store_true', help='Treat program as operation code (bool: or arith:)')
    parser.add_argument('--op-steps', type=int, default=50, help='Steps for operation execution (default: 50)')
    
    args = parser.parse_args()
    
    compiler = Rule110Compiler()
    
    if args.list_patterns:
        print("Available patterns:")
        for name in sorted(compiler.patterns.keys()):
            pattern = compiler.patterns[name]
            print(f"  {name:15s} : {' '.join(map(str, pattern))}")
        return 0
    
    if not args.program:
        print("Error: Program required. Use -h for help or -l to list patterns.")
        return 1
    
    # Handle operation mode
    if args.op or args.program.startswith('bool:') or args.program.startswith('arith:'):
        try:
            op_lang = OperationLanguage()
            result = op_lang.parse_and_execute(args.program, steps=args.op_steps)
            print(f"Operation: {args.program}")
            print(f"Result: {result}")
            print(f"Result type: {type(result).__name__}")
            
            # Show visualization if requested
            if args.visualize:
                # Get the operation executor to show the evolution
                executor = op_lang.executor
                if args.program.startswith('bool:'):
                    op_match = re.match(r'bool:(\w+)\((.*?)\)', args.program)
                    if op_match:
                        op = op_match.group(1).lower()
                        args_list = op_match.group(2).split(',')
                        args_list = [x.strip() for x in args_list]
                        a = True if args_list[0].lower() in ('true', '1') else False
                        b = None if len(args_list) == 1 else (True if args_list[1].lower() in ('true', '1') else False)
                        
                        initial_state, _, _ = executor.op_compiler.compile_boolean_op(op, a, b)
                        ca = Rule110(initial_state)
                        ca.run(args.op_steps)
                        visualize(ca.get_history(), char_alive=args.char_alive, char_dead=args.char_dead)
                elif args.program.startswith('arith:'):
                    arith_match = re.match(r'arith:(\w+)\((.*?)\)', args.program)
                    if arith_match:
                        op = arith_match.group(1).lower()
                        args_list = [int(x.strip()) for x in arith_match.group(2).split(',')]
                        initial_state, _, _ = executor.op_compiler.compile_arithmetic_op(op, args_list[0], args_list[1])
                        ca = Rule110(initial_state)
                        ca.run(args.op_steps)
                        visualize(ca.get_history(), char_alive=args.char_alive, char_dead=args.char_dead)
            
            return 0
        except Exception as e:
            print(f"Error executing operation: {e}", file=sys.stderr)
            return 1
    
    try:
        # Compile the program
        # First check if it's a direct pattern name
        if args.program in compiler.patterns:
            initial_state = compiler.compile_pattern(args.program, width=args.width)
        elif args.width:
            if ':' in args.program:
                # It's a code, compile normally then adjust width
                initial_state = compiler.compile_from_code(args.program)
                if len(initial_state) != args.width:
                    padding = (args.width - len(initial_state)) // 2
                    initial_state = [0] * padding + initial_state + [0] * (args.width - len(initial_state) - padding)
            else:
                # Try as pattern name
                initial_state = compiler.compile_pattern(args.program, width=args.width)
        else:
            initial_state = compiler.compile_from_code(args.program)
        
        print(f"Compiled initial state: {' '.join(map(str, initial_state))}")
        print(f"Length: {len(initial_state)} cells")
        print(f"Running for {args.steps} steps...\n")
        
        # Create and run Rule 110
        ca = Rule110(initial_state)
        ca.run(args.steps)
        history = ca.get_history()
        
        # Visualize
        if args.visualize:
            visualize(history, char_alive=args.char_alive, char_dead=args.char_dead)
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                for i, state in enumerate(history):
                    line = ''.join(args.char_alive if cell else args.char_dead for cell in state)
                    f.write(f"Step {i:3d}: {line}\n")
            print(f"\nOutput saved to {args.output}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

