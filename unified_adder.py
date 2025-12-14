"""
Rule 110 Unified Adder - All computation on a single tape

Key insight: Rule 110 information flows LEFT. So we place:
- Bit 0 (LSB) on the RIGHT
- Bit 3 (MSB) on the LEFT
- Carries flow leftward naturally

Each bit position needs:
- XOR(A, B) -> partial sum
- XOR(partial_sum, carry_in) -> final sum
- AND(A, B) -> partial carry
- AND(partial_sum, carry_in) -> carry contribution  
- OR(partial_carry, carry_contribution) -> carry_out

We'll use the verified gates from gates.py.
"""

from rule110 import Rule110


def step(state):
    """Single Rule 110 step"""
    RULE = {
        (1, 1, 1): 0, (1, 1, 0): 1, (1, 0, 1): 1, (1, 0, 0): 0,
        (0, 1, 1): 1, (0, 1, 0): 1, (0, 0, 1): 1, (0, 0, 0): 0
    }
    n = len(state)
    return [RULE[(state[(i-1)%n], state[i], state[(i+1)%n])] for i in range(n)]


def run(state, steps):
    """Run Rule 110 for given steps, return history"""
    history = [state[:]]
    for _ in range(steps):
        state = step(state)
        history.append(state[:])
    return history


class UnifiedFullAdder:
    """
    A full adder implemented on a unified Rule 110 tape.
    
    For a 4-bit adder, we need to compute:
    - For each bit i: Sum[i] = A[i] XOR B[i] XOR Carry[i]
                      Carry[i+1] = (A[i] AND B[i]) OR ((A[i] XOR B[i]) AND Carry[i])
    
    The trick is spatial and temporal layout so carries arrive at the right time.
    """
    
    def __init__(self, bits=4):
        self.bits = bits
        # Each bit lane needs space for inputs and intermediate results
        self.lane_width = 100
        self.total_width = (bits + 2) * self.lane_width
        
        # Timing: how many steps between bit computations
        self.bit_delay = 30
        self.total_steps = self.bit_delay * (bits + 1) + 50
        
    def add(self, a, b):
        """Add two numbers using Rule 110"""
        # Build initial state with inputs placed
        state = [0] * self.total_width
        
        # Place inputs for each bit
        # Bit i is at position: (bits - i) * lane_width + offset
        input_positions = []
        
        for i in range(self.bits):
            bit_a = (a >> i) & 1
            bit_b = (b >> i) & 1
            
            # Position this bit's inputs (rightmost bit = highest position)
            base_pos = (self.bits - i) * self.lane_width
            
            # A input
            pos_a = base_pos + 50
            state[pos_a] = bit_a
            
            # B input  
            pos_b = base_pos + 52
            state[pos_b] = bit_b
            
            input_positions.append({
                'bit': i,
                'a_pos': pos_a,
                'b_pos': pos_b,
                'a_val': bit_a,
                'b_val': bit_b,
            })
        
        # Run the computation
        history = run(state, self.total_steps)
        final_state = history[-1]
        
        # Extract result
        # The sum bits should appear at predictable positions after computation
        result = 0
        for i in range(self.bits + 1):  # +1 for possible overflow
            base_pos = (self.bits - i) * self.lane_width
            # The sum output should be around here after sufficient evolution
            output_region = base_pos + 10
            
            # Read the output (simplified: just check if there's activity)
            if output_region < len(final_state):
                result |= (final_state[output_region] << i)
        
        return result, history, input_positions


def test_basic():
    """Test basic additions"""
    adder = UnifiedFullAdder(bits=4)
    
    # The truth is: this simple approach won't work for real carry propagation
    # because we're just placing bits, not implementing actual gate logic
    
    # Let's be honest about what we can verify
    print("Testing unified adder:")
    print()
    
    for a, b in [(0, 0), (1, 0), (0, 1), (1, 1), (3, 5), (7, 8), (15, 0)]:
        expected = a + b
        result, history, inputs = adder.add(a, b)
        
        # Show what we placed
        print(f"{a} + {b} = {expected} (expected)")
        print(f"  Inputs placed:")
        for inp in inputs:
            print(f"    Bit {inp['bit']}: A={inp['a_val']} @ {inp['a_pos']}, B={inp['b_val']} @ {inp['b_pos']}")
        print(f"  Grid: {adder.total_width} x {len(history)} steps")
        print()


def build_real_adder():
    """
    Build a real working adder by composing individual gates.
    
    The key insight: instead of trying to do everything in parallel,
    we compute each gate sequentially and feed outputs to inputs.
    
    For a REAL unified tape computation, we need:
    1. Precise patterns that implement XOR, AND, OR
    2. Careful positioning so outputs appear where inputs are needed
    3. Proper timing so computations happen in the right order
    
    This is what Cook's proof does - it's extremely intricate.
    """
    
    # For now, let's implement a staged adder that uses the verified gates
    from gates import XorGate, AndGate, OrGate
    
    def full_adder_bit(a, b, carry_in):
        """Compute one bit of addition using Rule 110 gates"""
        xor = XorGate()
        and_gate = AndGate()
        or_gate = OrGate()
        
        # sum = a XOR b XOR carry_in
        partial_sum = xor.compute(a, b)
        sum_bit = xor.compute(partial_sum, carry_in)
        
        # carry_out = (a AND b) OR ((a XOR b) AND carry_in)
        partial_carry = and_gate.compute(a, b)
        carry_contrib = and_gate.compute(partial_sum, carry_in)
        carry_out = or_gate.compute(partial_carry, carry_contrib)
        
        return sum_bit, carry_out
    
    print("Real adder using composed Rule 110 gates:")
    print("=" * 50)
    print()
    
    test_cases = [
        (0, 0), (1, 0), (0, 1), (1, 1),
        (2, 1), (3, 1), (5, 3), (7, 8),
        (15, 1), (15, 15)
    ]
    
    correct = 0
    total = len(test_cases)
    
    for a, b in test_cases:
        expected = a + b
        
        # Compute using real gates
        result = 0
        carry = 0
        
        for i in range(5):  # 5 bits for up to 30
            bit_a = (a >> i) & 1
            bit_b = (b >> i) & 1
            
            sum_bit, carry = full_adder_bit(bit_a, bit_b, carry)
            result |= (sum_bit << i)
        
        status = "✓" if result == expected else "✗"
        print(f"  {a:2d} + {b:2d} = {result:2d} (expected {expected:2d}) {status}")
        
        if result == expected:
            correct += 1
    
    print()
    print(f"Accuracy: {correct}/{total} = {100*correct/total:.0f}%")
    print()
    print("Each gate operation is a REAL Rule 110 computation!")
    print("The gates are composed sequentially, not on a single unified tape.")
    
    return correct == total


if __name__ == "__main__":
    print("=" * 60)
    print("Rule 110 Adder Implementation")
    print("=" * 60)
    print()
    
    success = build_real_adder()
    
    if success:
        print("\n✓ All additions computed correctly via Rule 110!")
    else:
        print("\n✗ Some additions failed")

