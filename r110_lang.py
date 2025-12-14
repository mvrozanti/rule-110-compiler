"""
R110 Language - A simple language that compiles to Rule 110 CPU instructions

Syntax:
    x = 5           # Variable assignment
    x = a + b       # Addition
    x = a - b       # Subtraction  
    x = a & b       # Bitwise AND
    x = a | b       # Bitwise OR
    x = a ^ b       # Bitwise XOR
    x = ~a          # Bitwise NOT
    if a == b:      # Conditional (single statement)
    if a < b:
    if a > b:
    print x         # Output value

All operations are 8-bit unsigned integers.
"""

import re
from typing import List, Dict, Tuple
from r110_cpu import R110CPU


class R110Compiler:
    """Compiles R110 language to CPU instructions"""
    
    def __init__(self):
        self.variables: Dict[str, int] = {}  # var_name -> register
        self.next_reg = 0
        self.instructions: List[Tuple] = []
        self.temp_reg = 14  # R14-R15 for temps
    
    def alloc_reg(self, name: str) -> int:
        """Allocate a register for a variable"""
        if name not in self.variables:
            if self.next_reg >= 14:
                raise RuntimeError("Out of registers!")
            self.variables[name] = self.next_reg
            self.next_reg += 1
        return self.variables[name]
    
    def get_reg(self, name: str) -> int:
        """Get register for existing variable"""
        if name not in self.variables:
            raise RuntimeError(f"Undefined variable: {name}")
        return self.variables[name]
    
    def parse_value(self, val: str) -> Tuple[str, int]:
        """Parse a value, returns ('literal', num) or ('var', reg)"""
        val = val.strip()
        if val.isdigit():
            return ('literal', int(val))
        else:
            return ('var', self.get_reg(val))
    
    def ensure_in_reg(self, val: str) -> int:
        """Ensure value is in a register, return register number"""
        kind, v = self.parse_value(val)
        if kind == 'literal':
            reg = self.temp_reg
            self.temp_reg = 15 if self.temp_reg == 14 else 14
            self.instructions.append(('LOAD', reg, v))
            return reg
        else:
            return v
    
    def compile_line(self, line: str):
        """Compile a single line"""
        line = line.strip()
        if not line or line.startswith('#'):
            return
        
        # Print statement
        if line.startswith('print '):
            var = line[6:].strip()
            reg = self.get_reg(var)
            self.instructions.append(('PRINT', reg))
            return
        
        # Assignment
        if '=' in line and not line.startswith('if'):
            parts = line.split('=', 1)
            dest_name = parts[0].strip()
            expr = parts[1].strip()
            
            dest = self.alloc_reg(dest_name)
            
            # Simple literal assignment
            if expr.isdigit():
                self.instructions.append(('LOAD', dest, int(expr)))
                return
            
            # NOT operation: ~x
            if expr.startswith('~'):
                src = self.ensure_in_reg(expr[1:].strip())
                self.instructions.append(('NOT', dest, src))
                return
            
            # Comparison operations (must check before binary ops due to < >)
            for op, inst in [('==', 'EQ'), ('<=', 'LE'), ('>=', 'GE'), 
                            ('<', 'LT'), ('>', 'GT')]:
                if op in expr:
                    parts = expr.split(op)
                    left = self.ensure_in_reg(parts[0])
                    right = self.ensure_in_reg(parts[1])
                    self.instructions.append((inst, dest, left, right))
                    return
            
            # Binary operations
            for op, inst in [('+', 'ADD'), ('-', 'SUB'), ('&', 'AND'), 
                            ('|', 'OR'), ('^', 'XOR')]:
                if op in expr:
                    parts = expr.split(op)
                    left = self.ensure_in_reg(parts[0])
                    right = self.ensure_in_reg(parts[1])
                    self.instructions.append((inst, dest, left, right))
                    return
            
            # Variable copy
            if expr in self.variables:
                self.instructions.append(('MOV', dest, self.get_reg(expr)))
                return
            
            raise RuntimeError(f"Cannot parse expression: {expr}")
        
        # Conditional
        if line.startswith('if '):
            # Extract condition
            cond = line[3:].rstrip(':').strip()
            
            for op, inst in [('==', 'EQ'), ('<', 'LT'), ('>', 'GT')]:
                if op in cond:
                    parts = cond.split(op)
                    left = self.ensure_in_reg(parts[0])
                    right = self.ensure_in_reg(parts[1])
                    # Store condition result
                    self.instructions.append((inst, 15, left, right))
                    self.instructions.append(('IF', 15))  # Conditional marker
                    return
            
            raise RuntimeError(f"Cannot parse condition: {cond}")
    
    def compile(self, source: str) -> List[Tuple]:
        """Compile source code to instructions"""
        self.variables = {}
        self.next_reg = 0
        self.instructions = []
        self.temp_reg = 14
        
        for line in source.strip().split('\n'):
            self.compile_line(line)
        
        return self.instructions


class R110VM:
    """Virtual machine that runs R110 programs using the Rule 110 CPU"""
    
    def __init__(self):
        self.cpu = R110CPU()
        self.output: List[int] = []
    
    def run(self, instructions: List[Tuple], variables: Dict[str, int]):
        """Run compiled instructions"""
        self.cpu.reset()
        self.output = []
        
        skip_next = False
        
        for inst in instructions:
            if skip_next:
                skip_next = False
                continue
            
            op = inst[0]
            
            if op == 'PRINT':
                self.output.append(self.cpu.registers[inst[1]])
            elif op == 'IF':
                # If condition is false, skip next instruction
                if self.cpu.registers[inst[1]] == 0:
                    skip_next = True
            elif op == 'LOAD':
                self.cpu.load(inst[1], inst[2])
            elif op == 'ADD':
                self.cpu.add(inst[1], inst[2], inst[3])
            elif op == 'SUB':
                self.cpu.sub(inst[1], inst[2], inst[3])
            elif op == 'AND':
                self.cpu.and_(inst[1], inst[2], inst[3])
            elif op == 'OR':
                self.cpu.or_(inst[1], inst[2], inst[3])
            elif op == 'XOR':
                self.cpu.xor_(inst[1], inst[2], inst[3])
            elif op == 'NOT':
                self.cpu.not_(inst[1], inst[2])
            elif op == 'EQ':
                self.cpu.cmp_eq(inst[1], inst[2], inst[3])
            elif op == 'LT':
                self.cpu.cmp_lt(inst[1], inst[2], inst[3])
            elif op == 'GT':
                self.cpu.cmp_gt(inst[1], inst[2], inst[3])
            elif op == 'MOV':
                self.cpu.mov(inst[1], inst[2])
        
        return self.output


def run_program(source: str, show_instructions: bool = True):
    """Compile and run a program"""
    compiler = R110Compiler()
    instructions = compiler.compile(source)
    
    if show_instructions:
        print("Compiled instructions:")
        for i, inst in enumerate(instructions):
            print(f"  {i:3d}: {inst}")
        print()
        print("Variables:", compiler.variables)
        print()
    
    vm = R110VM()
    output = vm.run(instructions, compiler.variables)
    
    print("Output:", output)
    print()
    print("Final registers:")
    vm.cpu.dump()
    
    return output


# Example programs
EXAMPLES = {
    "simple_add": """
# Add two numbers
a = 10
b = 25
c = a + b
print c
""",

    "arithmetic": """
# Test various operations
x = 100
y = 30
sum = x + y
diff = x - y
print sum
print diff
""",

    "comparison": """
# Compare two numbers
a = 15
b = 20
less = a < b
print less
""",

    "bitwise": """
# Bitwise operations
a = 12
b = 10
c = a & b
d = a | b
e = a ^ b
print c
print d
print e
""",

    "expression": """
# Complex expression: (a + b) - c
a = 50
b = 30
c = 15
temp = a + b
result = temp - c
print result
""",
}


def main():
    print("R110 Language - Compiles to Rule 110 CPU")
    print("=" * 60)
    print()
    
    for name, source in EXAMPLES.items():
        print(f"### {name} ###")
        print(f"Source:{source}")
        run_program(source)
        print("-" * 60)
        print()


if __name__ == "__main__":
    main()

