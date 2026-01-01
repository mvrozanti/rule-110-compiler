#!/usr/bin/env python3
"""
Debug collision detection in Cook's CTS construction.
"""

from cook_cts import encode_cts_to_rule110, example_duplicator
from rule110 import DynamicRule110
from glider_tracker import track_gliders


def debug_collisions():
    """Debug what collisions are being detected."""
    print("=== Collision Detection Debug ===")

    # Create a simple CTS
    cts = example_duplicator()
    print(f"CTS: {cts.appendants}, initial='{cts.initial_tape}'")

    # Encode to Rule 110
    construction = encode_cts_to_rule110(cts, tape_length=50)
    print(f"Initial state length: {len(construction.initial_state)}")

    # Show initial glider detection
    print("\nInitial state glider detection:")
    track = track_gliders([construction.initial_state])
    print(f"Detected gliders: {len(track.gliders)}")
    for glider in track.gliders:
        print(f"  {glider.glider_type} at position {glider.position:.1f}")

    # Run a few steps and track
    ca = DynamicRule110(construction.initial_state, boundary="ether")
    ca.run(10)

    print(f"\nAfter 10 steps:")
    track = track_gliders(ca.get_history())

    print(f"Total gliders tracked: {len(track.gliders)}")
    print(f"Total collisions detected: {len(track.collisions)}")

    if track.collisions:
        print("\nCollisions detected:")
        for collision in track.collisions[:10]:  # Show first 10
            step, pos, desc = collision
            print(f"  Step {step}: pos {pos} - {desc}")

    # Check final CTS state
    from cook_cts import run_cook_cts_simulation
    cts_states = run_cook_cts_simulation(construction, steps=10)
    print(f"\nCTS evolution: {len(cts_states)} states")
    for i, state in enumerate(cts_states):
        print(f"  Step {i}: tape='{state.tape}', appendant={state.current_appendant}")


if __name__ == '__main__':
    debug_collisions()





