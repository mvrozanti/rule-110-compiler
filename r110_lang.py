"""
R110 Language - A simple language that compiles to Rule 110 CPU

Syntax:
    x = 5               # Variable assignment
    x = a + b           # Arithmetic (+, -, *, /)
    x = a & b           # Bitwise (& | ^ ~)
    x = a < b           # Comparison (< > == != <= >=)
    
    if condition:       # Conditional
        ...
    else:
        ...
    
    while condition:    # Loop
        ...
    
    def name(a, b):     # Function
        ...
        return x
    
    result = func(1, 2) # Function call
    print x             # Output

All operations are 8-bit unsigned integers.
"""

import re
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from r110_cpu import R110CPU, ALU, Gate


@dataclass
class Instruction:
    op: str
    args: Tuple
    
    def __repr__(self):
        return f"{self.op} {self.args}"


class R110Compiler:
    """Compiles R110 language to CPU instructions with control flow"""
    
    def __init__(self):
        self.variables: Dict[str, int] = {}
        self.functions: Dict[str, 'Function'] = {}
        self.next_reg = 0
        self.instructions: List[Instruction] = []
        self.label_counter = 0
    
    def new_label(self, prefix: str = "L") -> str:
        self.label_counter += 1
        return f"{prefix}{self.label_counter}"
    
    def alloc_reg(self, name: str) -> int:
        if name not in self.variables:
            if self.next_reg >= 13:
                raise RuntimeError(f"Out of registers! (allocating {name})")
            self.variables[name] = self.next_reg
            self.next_reg += 1
        return self.variables[name]
    
    def get_reg(self, name: str) -> int:
        if name not in self.variables:
            raise RuntimeError(f"Undefined variable: {name}")
        return self.variables[name]
    
    def emit(self, op: str, *args):
        self.instructions.append(Instruction(op, args))
    
    def ensure_in_reg(self, val: str) -> int:
        val = val.strip()
        if val.isdigit():
            reg = 14  # Temp register
            self.emit('LOAD', reg, int(val))
            return reg
        elif val in self.variables:
            return self.variables[val]
        else:
            raise RuntimeError(f"Unknown value: {val}")
    
    def parse_expr(self, expr: str, dest: int):
        """Parse and compile an expression into dest register"""
        expr = expr.strip()
        
        # Literal
        if expr.isdigit():
            self.emit('LOAD', dest, int(expr))
            return
        
        # Variable
        if expr.isidentifier() and expr in self.variables:
            if self.variables[expr] != dest:
                self.emit('MOV', dest, self.variables[expr])
            return
        
        # NOT
        if expr.startswith('~'):
            src = self.ensure_in_reg(expr[1:].strip())
            self.emit('NOT', dest, src)
            return
        
        # Function call: func(args)
        match = re.match(r'(\w+)\((.*)\)', expr)
        if match and match.group(1) in self.functions:
            func_name = match.group(1)
            args_str = match.group(2)
            args = [a.strip() for a in args_str.split(',')] if args_str.strip() else []
            self.compile_call(func_name, args, dest)
            return
        
        # Binary operations (order matters for multi-char ops)
        ops = [
            ('==', 'EQ'), ('!=', 'NE'), ('<=', 'LE'), ('>=', 'GE'),
            ('<', 'LT'), ('>', 'GT'),
            ('+', 'ADD'), ('-', 'SUB'), ('*', 'MUL'), ('/', 'DIV'),
            ('&', 'AND'), ('|', 'OR'), ('^', 'XOR'),
        ]
        
        for op_str, op_name in ops:
            if op_str in expr:
                # Split on first occurrence only
                idx = expr.find(op_str)
                left_str = expr[:idx].strip()
                right_str = expr[idx + len(op_str):].strip()
                
                left = self.ensure_in_reg(left_str)
                right = self.ensure_in_reg(right_str)
                self.emit(op_name, dest, left, right)
                return
        
        raise RuntimeError(f"Cannot parse expression: {expr}")
    
    def compile_call(self, func_name: str, args: List[str], dest: int):
        """Compile a function call"""
        func = self.functions[func_name]
        
        # Push arguments into registers R8-R11
        for i, arg in enumerate(args):
            arg_reg = 8 + i
            src = self.ensure_in_reg(arg)
            if src != arg_reg:
                self.emit('MOV', arg_reg, src)
        
        self.emit('CALL', func_name)
        
        # Result is in R15
        if dest != 15:
            self.emit('MOV', dest, 15)
    
    def parse_block(self, lines: List[str], start: int, base_indent: int) -> Tuple[List[str], int]:
        """Extract a block of lines with greater indentation"""
        block = []
        i = start
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
                continue
            
            indent = len(line) - len(line.lstrip())
            if indent <= base_indent and line.strip():
                break
            block.append(line)
            i += 1
        return block, i
    
    def compile_block(self, lines: List[str]):
        """Compile a block of lines"""
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            if not stripped or stripped.startswith('#'):
                i += 1
                continue
            
            indent = len(line) - len(line.lstrip())
            
            # While loop
            if stripped.startswith('while ') and stripped.endswith(':'):
                cond = stripped[6:-1].strip()
                block, new_i = self.parse_block(lines, i + 1, indent)
                self.compile_while(cond, block)
                i = new_i
                continue
            
            # If statement
            if stripped.startswith('if ') and stripped.endswith(':'):
                cond = stripped[3:-1].strip()
                if_block, new_i = self.parse_block(lines, i + 1, indent)
                
                # Check for else
                else_block = []
                if new_i < len(lines) and lines[new_i].strip() == 'else:':
                    else_block, new_i = self.parse_block(lines, new_i + 1, indent)
                
                self.compile_if(cond, if_block, else_block)
                i = new_i
                continue
            
            # Function definition
            if stripped.startswith('def ') and stripped.endswith(':'):
                match = re.match(r'def (\w+)\((.*)\):', stripped)
                if match:
                    func_name = match.group(1)
                    params = [p.strip() for p in match.group(2).split(',')] if match.group(2).strip() else []
                    body, new_i = self.parse_block(lines, i + 1, indent)
                    self.compile_function(func_name, params, body)
                    i = new_i
                    continue
            
            # Single line statements
            self.compile_line(stripped)
            i += 1
    
    def compile_while(self, cond: str, body: List[str]):
        """Compile a while loop"""
        loop_start = self.new_label("WHILE")
        loop_end = self.new_label("ENDWHILE")
        
        self.emit('LABEL', loop_start)
        
        # Evaluate condition
        self.compile_condition(cond, loop_end)
        
        # Body
        self.compile_block(body)
        
        # Jump back to start
        self.emit('JUMP', loop_start)
        self.emit('LABEL', loop_end)
    
    def compile_if(self, cond: str, if_block: List[str], else_block: List[str]):
        """Compile an if/else statement"""
        else_label = self.new_label("ELSE")
        end_label = self.new_label("ENDIF")
        
        # Evaluate condition, jump to else if false
        self.compile_condition(cond, else_label)
        
        # If block
        self.compile_block(if_block)
        
        if else_block:
            self.emit('JUMP', end_label)
        
        self.emit('LABEL', else_label)
        
        if else_block:
            self.compile_block(else_block)
            self.emit('LABEL', end_label)
    
    def compile_condition(self, cond: str, jump_if_false: str):
        """Compile a condition and jump if false"""
        # Parse condition
        for op_str, op_name in [('==', 'EQ'), ('!=', 'NE'), ('<=', 'LE'), 
                                 ('>=', 'GE'), ('<', 'LT'), ('>', 'GT')]:
            if op_str in cond:
                idx = cond.find(op_str)
                left = self.ensure_in_reg(cond[:idx].strip())
                right = self.ensure_in_reg(cond[idx + len(op_str):].strip())
                self.emit(op_name, 15, left, right)
                self.emit('JUMP_IF_ZERO', 15, jump_if_false)
                return
        
        # Single variable/value as condition
        val = self.ensure_in_reg(cond)
        self.emit('JUMP_IF_ZERO', val, jump_if_false)
    
    def compile_function(self, name: str, params: List[str], body: List[str]):
        """Compile a function definition"""
        self.functions[name] = Function(name, params, body, self)
    
    def compile_line(self, line: str):
        """Compile a single line"""
        line = line.strip()
        if not line or line.startswith('#'):
            return
        
        # Print
        if line.startswith('print '):
            var = line[6:].strip()
            if var.isdigit():
                self.emit('PRINT_LIT', int(var))
            else:
                self.emit('PRINT', self.get_reg(var))
            return
        
        # Return
        if line.startswith('return '):
            expr = line[7:].strip()
            self.parse_expr(expr, 15)  # Return value in R15
            self.emit('RETURN')
            return
        
        # Assignment
        if '=' in line:
            parts = line.split('=', 1)
            dest_name = parts[0].strip()
            expr = parts[1].strip()
            dest = self.alloc_reg(dest_name)
            self.parse_expr(expr, dest)
            return
        
        raise RuntimeError(f"Cannot parse: {line}")
    
    def compile(self, source: str) -> List[Instruction]:
        """Compile source code"""
        self.variables = {}
        self.functions = {}
        self.next_reg = 0
        self.instructions = []
        self.label_counter = 0
        
        lines = source.split('\n')
        self.compile_block(lines)
        
        return self.instructions


class Function:
    """A compiled function"""
    def __init__(self, name: str, params: List[str], body: List[str], compiler: R110Compiler):
        self.name = name
        self.params = params
        self.body = body
        self.compiler = compiler
        self.instructions: List[Instruction] = []
        self._compile()
    
    def _compile(self):
        # Create a sub-compiler for the function
        func_compiler = R110Compiler()
        func_compiler.functions = self.compiler.functions
        
        # Parameters are in R8-R11
        for i, param in enumerate(self.params):
            func_compiler.variables[param] = 8 + i
        func_compiler.next_reg = 0  # Local variables start at R0
        
        func_compiler.compile_block(self.body)
        self.instructions = func_compiler.instructions


class R110VM:
    """Virtual machine that runs R110 programs"""
    
    def __init__(self):
        self.cpu = R110CPU()
        self.output: List[int] = []
        self.labels: Dict[str, int] = {}
        self.call_stack: List[int] = []
    
    def run(self, instructions: List[Instruction], functions: Dict[str, Function]):
        """Run compiled instructions"""
        self.cpu.reset()
        self.output = []
        self.labels = {}
        self.call_stack = []
        
        # First pass: collect labels
        for i, inst in enumerate(instructions):
            if inst.op == 'LABEL':
                self.labels[inst.args[0]] = i
        
        # Execute
        pc = 0
        while pc < len(instructions):
            inst = instructions[pc]
            pc = self.execute_instruction(inst, pc, instructions, functions)
        
        return self.output
    
    def execute_instruction(self, inst: Instruction, pc: int, 
                           instructions: List[Instruction],
                           functions: Dict[str, Function]) -> int:
        op = inst.op
        args = inst.args
        
        if op == 'LABEL':
            return pc + 1
        
        elif op == 'LOAD':
            self.cpu.load(args[0], args[1])
        
        elif op == 'MOV':
            self.cpu.registers[args[0]] = self.cpu.registers[args[1]]
        
        elif op == 'ADD':
            self.cpu.add(args[0], args[1], args[2])
        
        elif op == 'SUB':
            self.cpu.sub(args[0], args[1], args[2])
        
        elif op == 'MUL':
            # Multiply using repeated addition
            a = self.cpu.registers[args[1]]
            b = self.cpu.registers[args[2]]
            result = 0
            for _ in range(b):
                result = ALU.add(result, a)
            self.cpu.registers[args[0]] = result & 0xFF
        
        elif op == 'DIV':
            # Divide using repeated subtraction
            a = self.cpu.registers[args[1]]
            b = self.cpu.registers[args[2]]
            if b == 0:
                self.cpu.registers[args[0]] = 0
            else:
                result = 0
                while a >= b:
                    a = ALU.sub(a, b)
                    result += 1
                self.cpu.registers[args[0]] = result
        
        elif op == 'AND':
            self.cpu.and_(args[0], args[1], args[2])
        
        elif op == 'OR':
            self.cpu.or_(args[0], args[1], args[2])
        
        elif op == 'XOR':
            self.cpu.xor_(args[0], args[1], args[2])
        
        elif op == 'NOT':
            self.cpu.not_(args[0], args[1])
        
        elif op == 'EQ':
            self.cpu.cmp_eq(args[0], args[1], args[2])
        
        elif op == 'NE':
            eq = ALU.eq(self.cpu.registers[args[1]], self.cpu.registers[args[2]])
            self.cpu.registers[args[0]] = Gate.not_(eq)
        
        elif op == 'LT':
            self.cpu.cmp_lt(args[0], args[1], args[2])
        
        elif op == 'GT':
            self.cpu.cmp_gt(args[0], args[1], args[2])
        
        elif op == 'LE':
            gt = ALU.gt(self.cpu.registers[args[1]], self.cpu.registers[args[2]])
            self.cpu.registers[args[0]] = Gate.not_(gt)
        
        elif op == 'GE':
            lt = ALU.lt(self.cpu.registers[args[1]], self.cpu.registers[args[2]])
            self.cpu.registers[args[0]] = Gate.not_(lt)
        
        elif op == 'JUMP':
            return self.labels[args[0]]
        
        elif op == 'JUMP_IF_ZERO':
            if self.cpu.registers[args[0]] == 0:
                return self.labels[args[1]]
        
        elif op == 'CALL':
            func = functions[args[0]]
            self.call_stack.append(pc + 1)
            # Build function labels
            func_labels = {}
            for i, f_inst in enumerate(func.instructions):
                if f_inst.op == 'LABEL':
                    func_labels[f_inst.args[0]] = i
            # Execute function instructions
            func_pc = 0
            while func_pc < len(func.instructions):
                f_inst = func.instructions[func_pc]
                if f_inst.op == 'RETURN':
                    break
                elif f_inst.op == 'LABEL':
                    func_pc += 1
                elif f_inst.op == 'JUMP':
                    func_pc = func_labels[f_inst.args[0]]
                elif f_inst.op == 'JUMP_IF_ZERO':
                    if self.cpu.registers[f_inst.args[0]] == 0:
                        func_pc = func_labels[f_inst.args[1]]
                    else:
                        func_pc += 1
                else:
                    func_pc = self.execute_instruction(f_inst, func_pc, func.instructions, functions)
            return self.call_stack.pop()
        
        elif op == 'RETURN':
            return len(instructions)  # Exit
        
        elif op == 'PRINT':
            self.output.append(self.cpu.registers[args[0]])
        
        elif op == 'PRINT_LIT':
            self.output.append(args[0])
        
        return pc + 1


def run_program(source: str, show_instructions: bool = True) -> List[int]:
    """Compile and run a program"""
    compiler = R110Compiler()
    instructions = compiler.compile(source)
    
    if show_instructions:
        print("Instructions:")
        for i, inst in enumerate(instructions):
            print(f"  {i:3d}: {inst}")
        print()
        if compiler.functions:
            print("Functions:")
            for name, func in compiler.functions.items():
                print(f"  {name}({', '.join(func.params)}):")
                for inst in func.instructions:
                    print(f"      {inst}")
            print()
    
    vm = R110VM()
    output = vm.run(instructions, compiler.functions)
    
    print(f"Output: {output}")
    return output


# Example programs
EXAMPLES = {
    "factorial": '''
# Factorial using a loop
n = 5
result = 1
i = 1
while i <= n:
    result = result * i
    i = i + 1
print result
''',

    "fibonacci": '''
# Fibonacci sequence
n = 10
a = 0
b = 1
i = 0
while i < n:
    print a
    temp = a + b
    a = b
    b = temp
    i = i + 1
''',

    "max_function": '''
# Function to find maximum
def max(a, b):
    if a > b:
        return a
    else:
        return b

x = 15
y = 23
result = max(x, y)
print result
''',

    "gcd": '''
# Greatest common divisor (subtraction-based)
a = 48
b = 18
while a != b:
    if a > b:
        a = a - b
    else:
        b = b - a
print a
''',

    "conditionals": '''
# Test conditionals
x = 10
y = 20

if x < y:
    print x
else:
    print y

if x == 10:
    z = 100
    print z
''',

    "loop_sum": '''
# Sum 1 to 10
sum = 0
i = 1
while i <= 10:
    sum = sum + i
    i = i + 1
print sum
''',
}


def main():
    print("R110 Language - Extended with Loops & Functions")
    print("=" * 60)
    print("All operations computed via Rule 110 cellular automaton")
    print()
    
    for name, source in EXAMPLES.items():
        print(f"### {name} ###")
        print(f"```")
        print(source.strip())
        print(f"```")
        print()
        try:
            run_program(source, show_instructions=False)
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 60)
        print()


if __name__ == "__main__":
    main()
