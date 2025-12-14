"""
Rule 110 Real Adder - Verified working implementation

This uses composed Rule 110 gates that are individually verified.
Each gate operation is a REAL Rule 110 computation.
"""

from rule110 import Rule110


class Rule110Gate:
    """A verified Rule 110 logic gate"""
    
    def __init__(self, name, input_positions, output_position, steps, width, extra_bits=None):
        self.name = name
        self.input_positions = input_positions
        self.output_position = output_position
        self.steps = steps
        self.width = width
        self.extra_bits = extra_bits or []
        self.last_history = None
    
    def compute(self, *inputs):
        """Run the gate and return (output, history)"""
        state = [0] * self.width
        
        for pos, val in zip(self.input_positions, inputs):
            state[pos] = val
        
        for pos in self.extra_bits:
            state[pos] = 1
        
        ca = Rule110(state)
        ca.run(self.steps)
        
        self.last_history = ca.get_history()
        return ca.get_state()[self.output_position]


# Verified gates
XOR_GATE = Rule110Gate("XOR", [20, 22], 8, 15, 50)
AND_GATE = Rule110Gate("AND", [15, 16], 1, 25, 40)
OR_GATE = Rule110Gate("OR", [15, 16], 6, 10, 40)
NOT_GATE = Rule110Gate("NOT", [15], 7, 10, 40, extra_bits=[10])


def full_adder_bit(a, b, carry_in, collect_history=False):
    """
    Compute one bit of addition using Rule 110 gates.
    
    Returns: (sum_bit, carry_out, gate_operations)
    
    Each gate operation records the Rule 110 computation.
    """
    operations = []
    
    # Step 1: partial_sum = a XOR b
    partial_sum = XOR_GATE.compute(a, b)
    if collect_history:
        operations.append({
            'gate': 'XOR',
            'inputs': [a, b],
            'output': partial_sum,
            'label': f'partial_sum = {a} ⊕ {b} = {partial_sum}',
            'history': XOR_GATE.last_history
        })
    
    # Step 2: sum = partial_sum XOR carry_in
    sum_bit = XOR_GATE.compute(partial_sum, carry_in)
    if collect_history:
        operations.append({
            'gate': 'XOR',
            'inputs': [partial_sum, carry_in],
            'output': sum_bit,
            'label': f'sum = {partial_sum} ⊕ {carry_in} = {sum_bit}',
            'history': XOR_GATE.last_history
        })
    
    # Step 3: partial_carry = a AND b
    partial_carry = AND_GATE.compute(a, b)
    if collect_history:
        operations.append({
            'gate': 'AND',
            'inputs': [a, b],
            'output': partial_carry,
            'label': f'partial_carry = {a} ∧ {b} = {partial_carry}',
            'history': AND_GATE.last_history
        })
    
    # Step 4: carry_contribution = partial_sum AND carry_in
    carry_contribution = AND_GATE.compute(partial_sum, carry_in)
    if collect_history:
        operations.append({
            'gate': 'AND',
            'inputs': [partial_sum, carry_in],
            'output': carry_contribution,
            'label': f'carry_contrib = {partial_sum} ∧ {carry_in} = {carry_contribution}',
            'history': AND_GATE.last_history
        })
    
    # Step 5: carry_out = partial_carry OR carry_contribution
    carry_out = OR_GATE.compute(partial_carry, carry_contribution)
    if collect_history:
        operations.append({
            'gate': 'OR',
            'inputs': [partial_carry, carry_contribution],
            'output': carry_out,
            'label': f'carry_out = {partial_carry} ∨ {carry_contribution} = {carry_out}',
            'history': OR_GATE.last_history
        })
    
    return sum_bit, carry_out, operations


def add(a, b, bits=4, collect_history=False):
    """
    Add two numbers using Rule 110 gates.
    
    Returns: (result, all_operations)
    """
    result = 0
    carry = 0
    all_operations = []
    
    for i in range(bits + 1):
        bit_a = (a >> i) & 1
        bit_b = (b >> i) & 1
        
        sum_bit, carry, ops = full_adder_bit(bit_a, bit_b, carry, collect_history)
        result |= (sum_bit << i)
        
        if collect_history:
            all_operations.append({
                'bit': i,
                'a': bit_a,
                'b': bit_b,
                'carry_in': carry,
                'sum': sum_bit,
                'carry_out': carry,
                'operations': ops
            })
    
    return result, all_operations


def test_all():
    """Test all 4-bit additions"""
    print("Testing Rule 110 Adder")
    print("=" * 50)
    print()
    
    correct = 0
    total = 0
    
    for a in range(16):
        for b in range(16):
            expected = a + b
            result, _ = add(a, b, bits=5)
            
            if result == expected:
                correct += 1
            total += 1
    
    print(f"Tested {total} additions")
    print(f"Correct: {correct}/{total} = {100*correct/total:.1f}%")
    print()
    
    # Show a few examples
    print("Examples:")
    for a, b in [(3, 5), (7, 8), (15, 1), (15, 15)]:
        result, ops = add(a, b, bits=5, collect_history=True)
        expected = a + b
        status = "✓" if result == expected else "✗"
        print(f"  {a} + {b} = {result} {status}")
        
        # Count gate operations
        total_ops = sum(len(bit_ops['operations']) for bit_ops in ops)
        print(f"    ({total_ops} Rule 110 gate operations)")


def export_computation(a, b, bits=4):
    """Export computation details for visualization"""
    result, all_ops = add(a, b, bits=bits+1, collect_history=True)
    
    # Flatten all histories
    all_histories = []
    for bit_ops in all_ops:
        for op in bit_ops['operations']:
            all_histories.append({
                'bit': bit_ops['bit'],
                'gate': op['gate'],
                'label': op['label'],
                'history': [[int(c) for c in row] for row in op['history']]
            })
    
    return {
        'a': a,
        'b': b,
        'result': result,
        'expected': a + b,
        'correct': result == (a + b),
        'computations': all_histories
    }


if __name__ == "__main__":
    test_all()

