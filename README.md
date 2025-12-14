# Rule 110 Compiler

A compiler and simulator for Elementary Cellular Automaton Rule 110, which is Turing complete and can theoretically compute anything a Turing machine can.

## Overview

Rule 110 is a one-dimensional cellular automaton where each cell's next state depends on its current state and the states of its two neighbors. Despite its simplicity, Rule 110 is proven to be Turing complete.

This project provides:
- A Rule 110 simulator
- A compiler that converts programs/patterns to initial Rule 110 configurations
- **Abstraction layer for boolean and arithmetic operations**
- Visualization tools
- Example patterns and programs

## Installation

No external dependencies required! Just Python 3.

```bash
python3 compiler.py -h
```

## Usage

### List Available Patterns

```bash
python3 compiler.py -l
```

### Compile and Run a Pattern

```bash
# Use a named pattern
python3 compiler.py glider -s 100

# Use a binary string
python3 compiler.py binary:1010101010 -s 50

# Use code syntax
python3 compiler.py pattern:glider -s 100 -w 80
```

### Boolean and Arithmetic Operations

The compiler supports high-level boolean and arithmetic operations:

```bash
# Boolean operations
python3 compiler.py "bool:and(1, 1)" --op
python3 compiler.py "bool:or(1, 0)" --op
python3 compiler.py "bool:not(1)" --op
python3 compiler.py "bool:xor(1, 0)" --op

# Arithmetic operations
python3 compiler.py "arith:add(5, 3)" --op
python3 compiler.py "arith:subtract(10, 4)" --op
python3 compiler.py "arith:multiply(6, 7)" --op
```

Operation syntax:
- `bool:operation(operand1, operand2)` - Boolean operations (and, or, xor)
- `bool:not(operand)` - Boolean NOT (single operand)
- `arith:operation(operand1, operand2)` - Arithmetic operations (add, subtract, multiply)

### Command Line Options

- `program`: The program to compile (pattern name, binary string, or code)
- `-s, --steps`: Number of steps to run (default: 50)
- `-w, --width`: Width of the initial state
- `-v, --visualize`: Visualize the evolution (default: True)
- `-o, --output`: Output file for the evolution history
- `-l, --list-patterns`: List available patterns
- `--op`: Treat program as operation code (bool: or arith:)
- `--op-steps`: Steps for operation execution (default: 50)
- `--char-alive`: Character for alive cells (default: █)
- `--char-dead`: Character for dead cells (default: space)

## Program Syntax

The compiler supports several program formats:

1. **Pattern Names**: Direct pattern names like `glider`, `block`, `single`
   ```bash
   python3 compiler.py glider
   ```

2. **Binary Strings**: Direct binary strings
   ```bash
   python3 compiler.py binary:101010
   ```

3. **Code Syntax**:
   - `pattern:pattern_name` - Use a named pattern
   - `binary:101010` - Use a binary string
   - `repeat:pattern_name:count` - Repeat a pattern multiple times

## Examples

```bash
# Run a glider pattern
python3 compiler.py pattern:glider -s 100

# Create a repeating pattern
python3 compiler.py repeat:block:5 -s 50

# Use a custom binary configuration
python3 compiler.py binary:111000111 -s 75 -w 100

# Save output to file
python3 compiler.py glider -s 200 -o output.txt
```

## Rule 110 Transition Table

Rule 110 is defined by the following transitions:

| Neighborhood | Next State |
|-------------|------------|
| 111 → 0     |            |
| 110 → 1     |            |
| 101 → 1     |            |
| 100 → 0     |            |
| 011 → 1     |            |
| 010 → 1     |            |
| 001 → 1     |            |
| 000 → 0     |            |

The binary pattern `01101110` represents this rule (hence "Rule 110").

## Programming with Rule 110

Rule 110 is Turing complete, meaning theoretically any computation can be encoded as a Rule 110 initial configuration. However, creating arbitrary programs requires understanding complex encodings (see Cook's proof). 

This compiler provides:
1. **Basic pattern compilation** - Convert simple patterns to Rule 110 initial states
2. **Operations abstraction layer** - High-level boolean and arithmetic operations that compile to Rule 110 configurations
3. **Visualization** - See how Rule 110 evolves over time

The operations abstraction layer provides a practical interface for performing computations using Rule 110 as the execution engine. While full arbitrary computation requires complex encodings (as proven by Cook), the abstraction layer makes common operations accessible.

## Python API

### Basic Usage

```python
from rule110 import Rule110, Rule110Compiler, visualize

# Compile a program
compiler = Rule110Compiler()
initial_state = compiler.compile_pattern('glider', width=80)

# Run Rule 110
ca = Rule110(initial_state)
ca.run(50)

# Visualize
visualize(ca.get_history())
```

### Operations Abstraction Layer

```python
from operations import OperationLanguage, OperationExecutor

# High-level operation language
op_lang = OperationLanguage()

# Execute boolean operations
result = op_lang.parse_and_execute("bool:and(1, 1)")  # True
result = op_lang.parse_and_execute("bool:or(1, 0)")   # True
result = op_lang.parse_and_execute("bool:not(1)")     # False
result = op_lang.parse_and_execute("bool:xor(1, 0)")  # True

# Execute arithmetic operations
result = op_lang.parse_and_execute("arith:add(5, 3)")       # 8
result = op_lang.parse_and_execute("arith:subtract(10, 4)") # 6
result = op_lang.parse_and_execute("arith:multiply(6, 7)")  # 42

# Direct executor interface
executor = OperationExecutor()
result = executor.execute_boolean('and', True, False)      # False
result = executor.execute_arithmetic('add', 15, 27)        # 42
```

### Operations Compiler

```python
from operations import OperationCompiler

compiler = OperationCompiler()

# Compile boolean operations
state, offset, bits = compiler.compile_boolean_op('and', True, False)

# Compile arithmetic operations
state, offset, bits = compiler.compile_arithmetic_op('add', 10, 20)

# Encode values
binary_pattern = compiler.encode_binary(42, bits=8)  # [0,0,1,0,1,0,1,0]
boolean_pattern = compiler.encode_boolean(True)      # [1]
```

## References

- Rule 110 was proven Turing complete by Matthew Cook
- "A New Kind of Science" by Stephen Wolfram discusses Rule 110 extensively
- Cook's paper: "A Concrete View of Rule 110 Computation"

## Testing

The project includes comprehensive unit tests. Run tests with:

```bash
# Run all tests
python3 test_all.py

# Run specific test modules
python3 -m unittest test_rule110 -v
python3 -m unittest test_operations -v

# Run with pytest (if installed)
pytest test_*.py -v
```

Test coverage includes:
- Rule110 simulator (initialization, transitions, execution, history)
- Rule110Compiler (pattern compilation, binary encoding, code parsing)
- Operations abstraction layer (boolean and arithmetic operations)
- OperationLanguage (parsing and execution)

## License

This project is provided as-is for educational and research purposes.

