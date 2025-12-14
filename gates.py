"""
Rule 110 Logic Gates - Verified gate implementations

These gates are discovered through systematic search and verified to work.
Each gate specifies input positions, output position, and required steps.
"""

from rule110 import Rule110


class Gate:
    """Base class for Rule 110 logic gates"""
    
    def __init__(self, width, input_positions, output_position, steps):
        self.width = width
        self.input_positions = input_positions
        self.output_position = output_position
        self.steps = steps
    
    def compute(self, *inputs):
        """Run the gate and return output"""
        if len(inputs) != len(self.input_positions):
            raise ValueError(f"Expected {len(self.input_positions)} inputs, got {len(inputs)}")
        
        state = self._build_state(inputs)
        ca = Rule110(state)
        ca.run(self.steps)
        return ca.get_state()[self.output_position]
    
    def _build_state(self, inputs):
        """Build initial state with inputs placed"""
        state = [0] * self.width
        for pos, val in zip(self.input_positions, inputs):
            state[pos] = 1 if val else 0
        return state
    
    def verify(self, truth_table):
        """Verify gate against truth table"""
        for inputs, expected in truth_table:
            result = self.compute(*inputs)
            if result != expected:
                return False, inputs, expected, result
        return True, None, None, None


class IdentityGate(Gate):
    """Identity gate: output = input"""
    
    def __init__(self):
        # Discovered: in@15 -> out@0, 15 steps
        super().__init__(width=40, input_positions=[15], output_position=0, steps=15)
    
    def truth_table(self):
        return [
            ([0], 0),
            ([1], 1),
        ]


class NotGate(Gate):
    """NOT gate: output = NOT input"""
    
    def __init__(self):
        # Discovered: extra@10, in@15 -> out@7, 10 steps
        # The extra bit at position 10 creates the inversion
        super().__init__(width=40, input_positions=[15], output_position=7, steps=10)
        self.extra_position = 10
    
    def _build_state(self, inputs):
        state = super()._build_state(inputs)
        state[self.extra_position] = 1  # Always set the extra bit
        return state
    
    def truth_table(self):
        return [
            ([0], 1),
            ([1], 0),
        ]


class OrGate(Gate):
    """OR gate: output = A OR B"""
    
    def __init__(self):
        # Discovered: in1@15, in2@16 -> out@6, 10 steps
        super().__init__(width=40, input_positions=[15, 16], output_position=6, steps=10)
    
    def truth_table(self):
        return [
            ([0, 0], 0),
            ([0, 1], 1),
            ([1, 0], 1),
            ([1, 1], 1),
        ]


class AndGate(Gate):
    """AND gate: output = A AND B"""
    
    def __init__(self):
        # Discovered: in1@15, in2@16 -> out@1, 25 steps
        super().__init__(width=40, input_positions=[15, 16], output_position=1, steps=25)
    
    def truth_table(self):
        return [
            ([0, 0], 0),
            ([0, 1], 0),
            ([1, 0], 0),
            ([1, 1], 1),
        ]


class XorGate(Gate):
    """XOR gate: output = A XOR B"""
    
    def __init__(self):
        # Discovered: in1@20, in2@22 -> out@8, 15 steps
        super().__init__(width=50, input_positions=[20, 22], output_position=8, steps=15)
    
    def truth_table(self):
        return [
            ([0, 0], 0),
            ([0, 1], 1),
            ([1, 0], 1),
            ([1, 1], 0),
        ]


def verify_all_gates():
    """Verify all gates work correctly"""
    gates = [
        ("Identity", IdentityGate()),
        ("NOT", NotGate()),
        ("OR", OrGate()),
        ("AND", AndGate()),
        ("XOR", XorGate()),
    ]
    
    all_passed = True
    for name, gate in gates:
        success, inputs, expected, got = gate.verify(gate.truth_table())
        if success:
            print(f"✓ {name} gate: PASS")
        else:
            print(f"✗ {name} gate: FAIL - inputs={inputs}, expected={expected}, got={got}")
            all_passed = False
    
    return all_passed


if __name__ == "__main__":
    print("Verifying Rule 110 Logic Gates\n")
    if verify_all_gates():
        print("\nAll gates verified!")
    else:
        print("\nSome gates failed verification!")
        exit(1)

