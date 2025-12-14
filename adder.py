"""
Rule 110 Adder - Built from verified logic gates

Half-adder: Sum = A XOR B, Carry = A AND B
Full-adder: Uses two half-adders to handle carry-in
"""

from rule110 import Rule110
from gates import XorGate, AndGate, OrGate


class HalfAdder:
    """
    Half-adder using Rule 110 gates.
    
    Inputs: A, B
    Outputs: Sum (A XOR B), Carry (A AND B)
    """
    
    def __init__(self):
        self.xor_gate = XorGate()
        self.and_gate = AndGate()
    
    def compute(self, a, b):
        """
        Compute half-adder.
        Returns (sum, carry)
        """
        sum_bit = self.xor_gate.compute(a, b)
        carry_bit = self.and_gate.compute(a, b)
        return sum_bit, carry_bit
    
    def verify(self):
        """Verify half-adder against truth table"""
        truth_table = [
            # (A, B) -> (Sum, Carry)
            ((0, 0), (0, 0)),
            ((0, 1), (1, 0)),
            ((1, 0), (1, 0)),
            ((1, 1), (0, 1)),
        ]
        
        for (a, b), (expected_sum, expected_carry) in truth_table:
            sum_bit, carry_bit = self.compute(a, b)
            if sum_bit != expected_sum or carry_bit != expected_carry:
                return False, (a, b), (expected_sum, expected_carry), (sum_bit, carry_bit)
        
        return True, None, None, None


class FullAdder:
    """
    Full-adder using Rule 110 gates.
    
    Inputs: A, B, Cin (carry in)
    Outputs: Sum, Cout (carry out)
    
    Implementation:
        Sum = A XOR B XOR Cin
        Cout = (A AND B) OR (Cin AND (A XOR B))
    """
    
    def __init__(self):
        self.xor1 = XorGate()
        self.xor2 = XorGate()
        self.and1 = AndGate()
        self.and2 = AndGate()
        self.or_gate = OrGate()
    
    def compute(self, a, b, cin):
        """
        Compute full-adder.
        Returns (sum, carry_out)
        """
        # First half-adder
        xor_ab = self.xor1.compute(a, b)
        and_ab = self.and1.compute(a, b)
        
        # Second half-adder (with carry-in)
        sum_bit = self.xor2.compute(xor_ab, cin)
        and_cin = self.and2.compute(xor_ab, cin)
        
        # Carry out
        carry_out = self.or_gate.compute(and_ab, and_cin)
        
        return sum_bit, carry_out
    
    def verify(self):
        """Verify full-adder against truth table"""
        truth_table = [
            # (A, B, Cin) -> (Sum, Cout)
            ((0, 0, 0), (0, 0)),
            ((0, 0, 1), (1, 0)),
            ((0, 1, 0), (1, 0)),
            ((0, 1, 1), (0, 1)),
            ((1, 0, 0), (1, 0)),
            ((1, 0, 1), (0, 1)),
            ((1, 1, 0), (0, 1)),
            ((1, 1, 1), (1, 1)),
        ]
        
        for (a, b, cin), (expected_sum, expected_cout) in truth_table:
            sum_bit, cout = self.compute(a, b, cin)
            if sum_bit != expected_sum or cout != expected_cout:
                return False, (a, b, cin), (expected_sum, expected_cout), (sum_bit, cout)
        
        return True, None, None, None


class RippleCarryAdder:
    """
    N-bit ripple carry adder using Rule 110 full-adders.
    """
    
    def __init__(self, bits=8):
        self.bits = bits
        self.full_adders = [FullAdder() for _ in range(bits)]
    
    def compute(self, a, b):
        """
        Add two N-bit numbers.
        
        Args:
            a: First number (integer)
            b: Second number (integer)
        
        Returns:
            Sum as integer
        """
        # Convert to bit arrays (LSB first for easier carry propagation)
        a_bits = [(a >> i) & 1 for i in range(self.bits)]
        b_bits = [(b >> i) & 1 for i in range(self.bits)]
        
        result_bits = []
        carry = 0
        
        for i in range(self.bits):
            sum_bit, carry = self.full_adders[i].compute(a_bits[i], b_bits[i], carry)
            result_bits.append(sum_bit)
        
        # Convert back to integer
        result = sum(bit << i for i, bit in enumerate(result_bits))
        
        # Include overflow carry if present
        if carry:
            result += (1 << self.bits)
        
        return result
    
    def verify(self, test_cases=None):
        """Verify adder with test cases"""
        if test_cases is None:
            max_val = (1 << self.bits) - 1
            test_cases = [
                (0, 0),
                (0, 1),
                (1, 0),
                (1, 1),
                (15, 1),
                (15, 15),
                (max_val, 0),
                (max_val, 1),
            ]
        
        for a, b in test_cases:
            expected = a + b
            result = self.compute(a, b)
            if result != expected:
                return False, (a, b), expected, result
        
        return True, None, None, None


def verify_all():
    """Verify all adder components"""
    print("Verifying Half-Adder...")
    ha = HalfAdder()
    success, inputs, expected, got = ha.verify()
    if success:
        print("✓ Half-Adder: PASS")
    else:
        print(f"✗ Half-Adder: FAIL - inputs={inputs}, expected={expected}, got={got}")
        return False
    
    print("\nVerifying Full-Adder...")
    fa = FullAdder()
    success, inputs, expected, got = fa.verify()
    if success:
        print("✓ Full-Adder: PASS")
    else:
        print(f"✗ Full-Adder: FAIL - inputs={inputs}, expected={expected}, got={got}")
        return False
    
    print("\nVerifying 4-bit Ripple Carry Adder...")
    rca = RippleCarryAdder(bits=4)
    test_cases = [
        (0, 0),
        (1, 1),
        (7, 8),
        (15, 1),  # 15 + 1 = 16 (overflow to 5 bits)
    ]
    success, inputs, expected, got = rca.verify(test_cases)
    if success:
        print("✓ 4-bit Adder: PASS")
        for a, b in test_cases:
            result = rca.compute(a, b)
            print(f"  {a} + {b} = {result}")
    else:
        print(f"✗ 4-bit Adder: FAIL - inputs={inputs}, expected={expected}, got={got}")
        return False
    
    return True


if __name__ == "__main__":
    print("=" * 50)
    print("Rule 110 Adder Verification")
    print("=" * 50)
    print()
    
    if verify_all():
        print("\n" + "=" * 50)
        print("All adder components verified!")
        print("=" * 50)
    else:
        print("\nVerification failed!")
        exit(1)

