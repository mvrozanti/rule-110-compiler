"""
Rule 110 Elementary Cellular Automaton Simulator

Rule 110 is Turing complete and defined by the following transition table:
  111 -> 0
  110 -> 1
  101 -> 1
  100 -> 0
  011 -> 1
  010 -> 1
  001 -> 1
  000 -> 0
"""

from typing import List

try:
    from cook_gliders import ETHER_BASE
except Exception:
    ETHER_BASE = [0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1]


class Rule110:
    """Simulator for Rule 110 Elementary Cellular Automaton"""
    
    def __init__(self, initial_state, boundary='zero', ether_pattern=None, pad=0):
        """
        Initialize Rule 110 with an initial state.
        
        Args:
            initial_state: List of 0s and 1s representing the initial cell states
            boundary: Boundary condition ('zero' or 'ether')
            ether_pattern: Pattern to use when boundary='ether'
            pad: Optional extra padding to add once at start
        """
        self.boundary = boundary
        self.ether_pattern = ether_pattern or [1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0]
        self.pad = pad
        self.state = (list(initial_state) if pad == 0
                      else [0] * pad + list(initial_state) + [0] * pad)
        self.history = [list(self.state)]
    
    def step(self):
        """Execute one step of Rule 110"""
        next_state = []
        pad = 3  # small halo for expansion
        n = len(self.state)
        
        # Build working state with optional ether padding (non-wrapping)
        if self.boundary == 'ether':
            ether = self.ether_pattern
            left_pad = [ether[(i % len(ether))] for i in range(pad, 0, -1)]
            right_pad = [ether[(i % len(ether))] for i in range(pad)]
        else:
            left_pad = [0] * pad
            right_pad = [0] * pad
        
        working = left_pad + self.state + right_pad
        wn = len(working)
        
        for i in range(wn):
            left = working[i - 1] if i > 0 else 0
            center = working[i]
            right = working[i + 1] if i < wn - 1 else 0
            next_cell = self._rule110(left, center, right)
            next_state.append(next_cell)
        
        self.state = next_state
        self.history.append(list(self.state))
    
    def _rule110(self, left, center, right):
        """Apply Rule 110 transition rule"""
        # Rule 110 pattern: 01101110 in binary
        pattern = (left << 2) | (center << 1) | right
        
        # Rule 110 mapping
        rules = {
            0b111: 0,  # 7 -> 0
            0b110: 1,  # 6 -> 1
            0b101: 1,  # 5 -> 1
            0b100: 0,  # 4 -> 0
            0b011: 1,  # 3 -> 1
            0b010: 1,  # 2 -> 1
            0b001: 1,  # 1 -> 1
            0b000: 0,  # 0 -> 0
        }
        
        return rules[pattern]
    
    def run(self, steps):
        """Run Rule 110 for a specified number of steps"""
        for _ in range(steps):
            self.step()
        return self.history
    
    def get_state(self):
        """Get current state"""
        return self.state
    
    def get_history(self):
        """Get entire evolution history"""
        return self.history


class DynamicRule110(Rule110):
    """
    Rule 110 with dynamic growth and ether boundaries to reduce edge artifacts.
    """

    def __init__(self, initial_state, boundary: str = "ether", grow_margin: int = 8, grow_chunk: int = None):
        super().__init__(initial_state, boundary=boundary)
        self.boundary = boundary
        self.grow_margin = max(grow_margin, 1)
        self.grow_chunk = grow_chunk or len(ETHER_BASE) * 2

    def _boundary_value(self, idx: int) -> int:
        if self.boundary == "ether":
            return ETHER_BASE[idx % len(ETHER_BASE)]
        return 0

    def _maybe_grow(self):
        # Prepend/append ether chunks if activity approaches edges
        chunk_bits = self._ether_chunk(self.grow_chunk)
        grew = False
        if any(self.state[: self.grow_margin]):
            self.state = chunk_bits + self.state
            grew = True
        if any(self.state[-self.grow_margin :]):
            self.state = self.state + chunk_bits
            grew = True
        if grew:
            # Extend last history entry to keep lengths aligned
            self.history[-1] = self.state.copy()

    def _ether_chunk(self, width: int) -> List[int]:
        if width <= 0:
            return []
        base = ETHER_BASE * ((width // len(ETHER_BASE)) + 1)
        return base[:width]

    def step(self):
        """Execute one step with dynamic growth."""
        self._maybe_grow()
        next_state = []
        n = len(self.state)
        for i in range(n):
            left = self.state[i - 1] if i > 0 else self._boundary_value(-1)
            center = self.state[i]
            right = self.state[i + 1] if i < n - 1 else self._boundary_value(n)
            next_state.append(self._rule110(left, center, right))
        self.state = next_state
        self.history.append(list(self.state))


class Rule110Compiler:
    """Compiler that converts programs to Rule 110 initial configurations"""
    
    def __init__(self):
        self.patterns = {
            'blank': [0] * 100,
            'single': [0] * 50 + [1] + [0] * 49,
            'glider': [1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0],
            'periodic': [0, 1, 0, 1, 0, 1, 0, 1],
            'block': [1, 1, 1, 1],
            'sparse': [1, 0, 0, 0, 1, 0, 0, 0, 1],
        }
    
    def compile_pattern(self, pattern_name, width=None):
        """
        Compile a named pattern into a Rule 110 initial state.
        
        Args:
            pattern_name: Name of the pattern to compile
            width: Optional width to pad/truncate the pattern
        
        Returns:
            List of 0s and 1s representing the initial state
        """
        if pattern_name not in self.patterns:
            raise ValueError(f"Unknown pattern: {pattern_name}")
        
        state = self.patterns[pattern_name].copy()
        
        if width:
            if len(state) < width:
                # Center the pattern
                padding = (width - len(state)) // 2
                state = [0] * padding + state + [0] * (width - len(state) - padding)
            else:
                state = state[:width]
        
        return state
    
    def compile_binary(self, binary_string):
        """
        Compile a binary string into a Rule 110 initial state.
        
        Args:
            binary_string: String of 0s and 1s
        
        Returns:
            List of 0s and 1s
        """
        return [int(bit) for bit in binary_string if bit in '01']
    
    def compile_from_code(self, code):
        """
        Compile a simple program into Rule 110 initial state.
        
        Syntax examples:
        - pattern:glider -> uses glider pattern
        - binary:101010 -> uses binary string
        - repeat:pattern_name:10 -> repeats pattern 10 times
        
        Args:
            code: Program code string
        
        Returns:
            List of 0s and 1s representing the initial state
        """
        code = code.strip()
        
        if code.startswith('pattern:'):
            pattern_name = code.split(':', 1)[1]
            return self.compile_pattern(pattern_name)
        
        elif code.startswith('binary:'):
            binary_string = code.split(':', 1)[1]
            return self.compile_binary(binary_string)
        
        elif code.startswith('repeat:'):
            parts = code.split(':')
            if len(parts) == 3:
                pattern_name = parts[1]
                count = int(parts[2])
                base_pattern = self.compile_pattern(pattern_name)
                return base_pattern * count
            else:
                raise ValueError("Invalid repeat syntax: repeat:pattern_name:count")
        
        else:
            # Try as direct binary string
            try:
                return self.compile_binary(code)
            except:
                raise ValueError(f"Unknown code format: {code}")
    
    def add_pattern(self, name, pattern):
        """Add a custom pattern to the compiler"""
        self.patterns[name] = pattern


def visualize(history, char_alive='█', char_dead=' '):
    """
    Visualize Rule 110 evolution history.
    
    Args:
        history: List of state lists from Rule110.run()
        char_alive: Character to represent alive cell (1)
        char_dead: Character to represent dead cell (0)
    """
    for i, state in enumerate(history):
        line = ''.join(char_alive if cell else char_dead for cell in state)
        print(f"Step {i:3d}: {line}")


if __name__ == '__main__':
    # Example usage
    compiler = Rule110Compiler()
    
    # Compile a simple pattern
    initial_state = compiler.compile_pattern('glider', width=80)
    
    # Create and run Rule 110
    ca = Rule110(initial_state)
    ca.run(50)
    
    # Visualize
    print("Rule 110 Evolution:")
    visualize(ca.get_history())

