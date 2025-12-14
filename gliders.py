"""
Rule 110 Glider-Based Computation

Proper implementation using gliders propagating through ether background.
Gliders are localized disturbances that maintain their shape while moving.
Collisions between gliders implement logic.
"""

from rule110 import Rule110


class EtherBackground:
    """
    The Rule 110 ether - the periodic background pattern.
    
    The ether has:
    - Spatial period: 14 cells
    - Temporal period: 7 steps
    
    Gliders are perturbations that travel through this ether.
    """
    
    # The fundamental ether unit (14 cells)
    ETHER_UNIT = [0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1]
    
    @classmethod
    def create(cls, width):
        """Create an ether pattern of given width"""
        repeats = (width // 14) + 2
        return (cls.ETHER_UNIT * repeats)[:width]
    
    @classmethod
    def create_at_phase(cls, width, phase):
        """Create ether at a specific temporal phase (0-6)"""
        ether = cls.create(width + 14)
        ca = Rule110(ether)
        ca.run(phase % 7)
        return ca.get_state()[:width]


class GliderInjector:
    """
    Inject gliders into the ether at specific positions.
    
    A glider is created by flipping specific bits in the ether.
    The glider then propagates through the ether.
    """
    
    @staticmethod
    def inject_simple_glider(state, position):
        """
        Inject a simple glider at the given position.
        
        This creates a disturbance that propagates leftward.
        """
        state = state.copy()
        # Flip a few bits to create a glider
        for offset in range(4):
            if position + offset < len(state):
                state[position + offset] = 1 - state[position + offset]
        return state
    
    @staticmethod
    def inject_signal(state, position, value):
        """
        Inject a signal (glider present = 1, absent = 0) at position.
        """
        if value:
            return GliderInjector.inject_simple_glider(state, position)
        else:
            return state.copy()


class GliderComputer:
    """
    Compute using gliders in Rule 110.
    
    This creates an ether, injects gliders representing input bits,
    runs the automaton, and reads output from glider positions.
    """
    
    def __init__(self, width=300, steps=100):
        self.width = width
        self.steps = steps
    
    def compute_xor(self, a, b):
        """
        Compute XOR using glider collision.
        
        Two gliders that collide annihilate (output 0).
        A single glider passes through (output 1).
        XOR(0,0)=0: no gliders, no output
        XOR(0,1)=1: one glider passes
        XOR(1,0)=1: one glider passes
        XOR(1,1)=0: gliders collide and annihilate
        """
        # Create ether
        state = EtherBackground.create(self.width)
        
        # Inject gliders at positions that will collide in the middle
        # Positions chosen so gliders meet at a specific point
        pos_a = 100  # Position for input A
        pos_b = 140  # Position for input B (spaced for collision timing)
        
        if a:
            state = GliderInjector.inject_simple_glider(state, pos_a)
        if b:
            state = GliderInjector.inject_simple_glider(state, pos_b)
        
        # Run the automaton
        ca = Rule110(state)
        history = [state]
        for _ in range(self.steps):
            ca.step()
            history.append(ca.get_state().copy())
        
        # Detect output: check for glider presence in output region
        final = ca.get_state()
        output_region = final[40:70]  # Region where output glider should appear
        
        # Count disturbances (differences from pure ether)
        expected_ether = EtherBackground.create_at_phase(30, self.steps % 7)
        disturbance = sum(1 for i in range(30) if output_region[i] != expected_ether[i])
        
        # Significant disturbance = glider present = output 1
        output = 1 if disturbance > 5 else 0
        
        return output, history
    
    def run_with_visualization(self, a, b):
        """Run and return history for visualization"""
        return self.compute_xor(a, b)


def demonstrate_gliders():
    """Show gliders in action"""
    print("Rule 110 Glider Demonstration")
    print("=" * 50)
    
    # Create ether
    width = 150
    ether = EtherBackground.create(width)
    
    print(f"\nEther pattern (first 42 cells): {ether[:42]}")
    print(f"Ether period: 14 cells")
    
    # Inject a glider
    state = GliderInjector.inject_simple_glider(ether, 80)
    
    print(f"\nInjected glider at position 80")
    print("Watching glider propagate through ether...\n")
    
    def show(s):
        return ''.join('█' if c else '·' for c in s)
    
    ca = Rule110(state)
    for i in range(30):
        s = ca.get_state()
        # Show window around glider
        window = s[50:130]
        print(f"{i:2d}: {show(window)}")
        ca.step()


def test_xor():
    """Test XOR gate using gliders"""
    print("\n" + "=" * 50)
    print("Testing XOR Gate with Gliders")
    print("=" * 50)
    
    computer = GliderComputer(width=200, steps=80)
    
    for a in [0, 1]:
        for b in [0, 1]:
            output, _ = computer.compute_xor(a, b)
            expected = a ^ b
            status = "✓" if output == expected else "✗"
            print(f"XOR({a}, {b}) = {output} (expected {expected}) {status}")


if __name__ == "__main__":
    demonstrate_gliders()
    test_xor()

