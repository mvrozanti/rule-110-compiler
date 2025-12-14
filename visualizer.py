#!/usr/bin/env python3
"""
Visualizer for Rule 110 operations
Shows operations as cellular automaton evolution with cells
"""

import sys
import argparse
from rule110 import Rule110
from operations import OperationCompiler, OperationExecutor


class Rule110Visualizer:
    """Visualize Rule 110 operations as cell grids"""
    
    def __init__(self, cell_alive='█', cell_dead=' ', separator='│'):
        """
        Initialize visualizer
        
        Args:
            cell_alive: Character for alive cells (1)
            cell_dead: Character for dead cells (0)
            separator: Character for separating columns
        """
        self.cell_alive = cell_alive
        self.cell_dead = cell_dead
        self.separator = separator
    
    def visualize_state(self, state, step_num=None, label=None):
        """
        Visualize a single state as a row of cells
        
        Args:
            state: List of 0s and 1s
            step_num: Step number (optional)
            label: Label for the row (optional)
        """
        cells = ''.join(self.cell_alive if cell else self.cell_dead for cell in state)
        
        prefix = ''
        if step_num is not None:
            prefix = f"Step {step_num:3d}: "
        if label:
            prefix = f"{label:12s}: "
        
        return f"{prefix}{cells}"
    
    def visualize_operation(self, operation_code, steps=50, show_all_steps=True, 
                          highlight_regions=None):
        """
        Visualize a complete operation evolution
        
        Args:
            operation_code: Operation code (e.g., 'arith:add(15, 31)')
            steps: Number of steps to run
            show_all_steps: Whether to show all steps or just key ones
            highlight_regions: List of (start, end) tuples to highlight
        
        Returns:
            List of visualization strings
        """
        from operations import OperationLanguage
        
        op_lang = OperationLanguage()
        executor = op_lang.executor
        
        # Determine operation type and get initial state
        if operation_code.startswith('bool:'):
            # Parse boolean operation
            import re
            match = re.match(r'bool:(\w+)\((.*?)\)', operation_code)
            if not match:
                raise ValueError(f"Invalid boolean operation: {operation_code}")
            
            op = match.group(1).lower()
            args_str = match.group(2)
            args = []
            for arg in args_str.split(','):
                arg = arg.strip()
                if arg.lower() in ('true', '1'):
                    args.append(True)
                elif arg.lower() in ('false', '0'):
                    args.append(False)
                else:
                    args.append(bool(int(arg)))
            
            if op == 'not':
                initial_state, offset, bits = executor.op_compiler.compile_boolean_op(op, args[0])
            else:
                initial_state, offset, bits = executor.op_compiler.compile_boolean_op(op, args[0], args[1])
        
        elif operation_code.startswith('arith:'):
            # Parse arithmetic operation
            import re
            match = re.match(r'arith:(\w+)\((.*?)\)', operation_code)
            if not match:
                raise ValueError(f"Invalid arithmetic operation: {operation_code}")
            
            op = match.group(1).lower()
            args = [int(x.strip()) for x in match.group(2).split(',')]
            
            initial_state, offset, bits = executor.op_compiler.compile_arithmetic_op(op, args[0], args[1])
            
            # Store input info for display
            highlight_regions = [
                (0, len(executor.op_compiler.encode_binary(args[0], 8))),
                (len(executor.op_compiler.encode_binary(args[0], 8)) + 4,
                 len(executor.op_compiler.encode_binary(args[0], 8)) + 4 + len(executor.op_compiler.encode_binary(args[1], 8))),
                (offset, offset + bits)
            ]
        else:
            raise ValueError(f"Unknown operation type: {operation_code}")
        
        # Create and run Rule 110
        ca = Rule110(initial_state)
        ca.run(steps)
        history = ca.get_history()
        
        # Generate visualization
        visualizations = []
        
        # Header
        visualizations.append("=" * 80)
        visualizations.append(f"Operation: {operation_code}")
        visualizations.append(f"Initial state length: {len(initial_state)} cells")
        visualizations.append(f"Steps: {steps}")
        
        # Show binary representations for arithmetic operations
        if operation_code.startswith('arith:'):
            import re
            match = re.match(r'arith:(\w+)\((.*?)\)', operation_code)
            if match:
                args = [int(x.strip()) for x in match.group(2).split(',')]
                compiler = OperationCompiler()
                bin_a = compiler.encode_binary(args[0], 8)
                bin_b = compiler.encode_binary(args[1], 8)
                bin_a_str = ''.join(str(b) for b in bin_a)
                bin_b_str = ''.join(str(b) for b in bin_b)
                visualizations.append(f"Input A: {args[0]} = {bin_a_str} (binary)")
                visualizations.append(f"Input B: {args[1]} = {bin_b_str} (binary)")
                if operation_code.startswith('arith:add'):
                    expected = args[0] + args[1]
                    visualizations.append(f"Expected result: {expected}")
        
        if highlight_regions:
            visualizations.append("Regions: [Input A] │ [Input B] │ ... │ [Output]")
        visualizations.append("=" * 80)
        visualizations.append("")
        
        # Show initial state with annotation
        visualizations.append("Initial Configuration:")
        if highlight_regions:
            annotated = self._annotate_regions(initial_state, highlight_regions)
            visualizations.append(annotated)
        else:
            visualizations.append(self.visualize_state(initial_state, label="Initial"))
        
        # Show binary representation of initial state
        if operation_code.startswith('arith:'):
            bin_str = ''.join(str(b) for b in initial_state)
            visualizations.append(f"Binary:  {bin_str}")
        visualizations.append("")
        
        # Show evolution
        visualizations.append("Evolution:")
        if show_all_steps:
            step_indices = range(len(history))
        else:
            # Show first few, middle, and last steps
            if len(history) <= 20:
                step_indices = range(len(history))
            else:
                step_indices = list(range(min(5, len(history)))) + \
                              [len(history) // 2] + \
                              list(range(max(len(history) - 5, 0), len(history)))
        
        for step_idx in step_indices:
            state = history[step_idx]
            vis_line = self.visualize_state(state, step_num=step_idx)
            visualizations.append(vis_line)
        
        # Show final state with result
        visualizations.append("")
        visualizations.append("Final State:")
        if highlight_regions:
            annotated = self._annotate_regions(history[-1], highlight_regions)
            visualizations.append(annotated)
        else:
            visualizations.append(self.visualize_state(history[-1], label="Final"))
        
        # Extract and show result
        try:
            result = op_lang.parse_and_execute(operation_code, steps=steps)
            visualizations.append("")
            visualizations.append(f"Result: {result}")
        except:
            pass
        
        visualizations.append("")
        visualizations.append("=" * 80)
        
        return visualizations
    
    def _annotate_regions(self, state, regions):
        """Annotate regions in the state with labels"""
        # Create a visual representation with region markers
        cells = []
        for i, cell in enumerate(state):
            cells.append(self.cell_alive if cell else self.cell_dead)
        
        # Build annotated string with separators
        result = []
        last_pos = 0
        
        for region_idx, (start, end) in enumerate(regions):
            # Add cells before this region
            if start > last_pos:
                result.extend(cells[last_pos:start])
            
            # Add separator before region (except first)
            if region_idx > 0 or start > 0:
                result.append(self.separator)
            
            # Add cells in this region
            result.extend(cells[start:end])
            last_pos = end
        
        # Add remaining cells
        if last_pos < len(state):
            result.extend(cells[last_pos:])
        
        return f"{''.join(result)}"
    
    def print_visualization(self, operation_code, steps=50, **kwargs):
        """Print visualization to stdout"""
        visualizations = self.visualize_operation(operation_code, steps, **kwargs)
        for line in visualizations:
            print(line)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Visualize Rule 110 operations as cellular automaton evolution'
    )
    parser.add_argument('operation', help='Operation to visualize (e.g., arith:add(15, 31))')
    parser.add_argument('-s', '--steps', type=int, default=50, 
                       help='Number of steps to run (default: 50)')
    parser.add_argument('--cell-alive', default='█', 
                       help='Character for alive cells (default: █)')
    parser.add_argument('--cell-dead', default=' ', 
                       help='Character for dead cells (default: space)')
    parser.add_argument('--separator', default='│', 
                       help='Character for separating regions (default: │)')
    parser.add_argument('--key-steps-only', action='store_true',
                       help='Show only key steps (first, middle, last)')
    
    args = parser.parse_args()
    
    visualizer = Rule110Visualizer(
        cell_alive=args.cell_alive,
        cell_dead=args.cell_dead,
        separator=args.separator
    )
    
    try:
        visualizer.print_visualization(
            args.operation,
            steps=args.steps,
            show_all_steps=not args.key_steps_only
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

