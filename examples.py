#!/usr/bin/env python3
"""
Example programs demonstrating Rule 110 compiler capabilities
"""

from rule110 import Rule110, Rule110Compiler, visualize


def example_glider():
    """Example: Run a glider pattern"""
    print("=== Example: Glider Pattern ===\n")
    compiler = Rule110Compiler()
    initial_state = compiler.compile_pattern('glider', width=80)
    
    ca = Rule110(initial_state)
    ca.run(50)
    visualize(ca.get_history())


def example_binary():
    """Example: Run with binary string"""
    print("=== Example: Binary String ===\n")
    compiler = Rule110Compiler()
    initial_state = compiler.compile_binary('111000111000111')
    
    ca = Rule110(initial_state)
    ca.run(30)
    visualize(ca.get_history())


def example_custom_pattern():
    """Example: Create and use a custom pattern"""
    print("=== Example: Custom Pattern ===\n")
    compiler = Rule110Compiler()
    
    # Add a custom pattern
    compiler.add_pattern('custom', [1, 0, 1, 0, 1, 1, 1, 0, 0, 1])
    initial_state = compiler.compile_pattern('custom', width=60)
    
    ca = Rule110(initial_state)
    ca.run(40)
    visualize(ca.get_history())


def example_repeat():
    """Example: Repeat a pattern"""
    print("=== Example: Repeating Pattern ===\n")
    compiler = Rule110Compiler()
    initial_state = compiler.compile_from_code('repeat:block:8')
    
    ca = Rule110(initial_state)
    ca.run(35)
    visualize(ca.get_history())


def example_periodic():
    """Example: Periodic pattern"""
    print("=== Example: Periodic Pattern ===\n")
    compiler = Rule110Compiler()
    initial_state = compiler.compile_pattern('periodic', width=80)
    
    ca = Rule110(initial_state)
    ca.run(60)
    visualize(ca.get_history())


if __name__ == '__main__':
    import sys
    
    examples = {
        'glider': example_glider,
        'binary': example_binary,
        'custom': example_custom_pattern,
        'repeat': example_repeat,
        'periodic': example_periodic,
    }
    
    if len(sys.argv) > 1 and sys.argv[1] in examples:
        examples[sys.argv[1]]()
    else:
        print("Available examples:")
        for name in examples:
            print(f"  {name}")
        print("\nUsage: python3 examples.py <example_name>")
        print("\nRunning default example (glider)...\n")
        example_glider()

