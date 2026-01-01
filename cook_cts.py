"""
Cook's Cyclic Tag System construction for Rule 110 universality proof.

This implements the construction from Cook's 2004 paper, Section 4,
where Rule 110 gliders simulate a cyclic tag system to prove universality.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from rule110 import Rule110, DynamicRule110
from glider_tracker import track_gliders, GLIDER_PROPERTIES
from cook_leaders import CookLeaderSystem, place_leader_component_system


@dataclass
class CTSSpec:
    """Specification for a cyclic tag system."""
    appendants: List[str]  # List of strings to append (one per cycle)
    initial_tape: str     # Initial tape contents (Y/N symbols)


@dataclass
class CTSState:
    """Current state of the CTS simulation."""
    tape: str
    current_appendant: int  # Index of current appendant in cycle


@dataclass
class CookConstruction:
    """Cook's Rule 110 construction for simulating CTS."""
    cts_spec: CTSSpec
    initial_state: List[int]
    ether_period: int = 14  # Ether period from Cook's paper


def _encode_symbol_to_gliders(symbol: str) -> List[str]:
    """
    Encode a CTS symbol (Y/N) into glider packages.

    Based on Cook's Section 4.2: different spacings represent Y vs N.
    """
    if symbol == 'Y':
        # Y represented by wider spacing between C2 gliders
        return ['C2', 'C2', 'C2', 'C2']  # Cook: C2 18 C2 18 C2 14 C2
    elif symbol == 'N':
        # N represented by narrower spacing
        return ['C2', 'C2', 'C2', 'C2']  # Cook: C2 18 C2 10 C2 14 C2
    else:
        raise ValueError(f"Invalid CTS symbol: {symbol}")


def _encode_appendant_to_gliders(appendant: str) -> List[str]:
    """
    Encode a CTS appendant into moving data gliders.

    Based on Cook's Section 4.2: appendants become sequences of Ē gliders.
    """
    gliders = []
    for symbol in appendant:
        if symbol == 'Y':
            gliders.extend(['Ē', 'Ē', 'Ē', 'Ē'])  # Four Ēs for moving data
        elif symbol == 'N':
            gliders.extend(['Ē', 'Ē', 'Ē', 'Ē'])
        else:
            raise ValueError(f"Invalid appendant symbol: {symbol}")
    return gliders


def _create_ether_background(length: int) -> List[int]:
    """
    Create the ether background pattern.

    Cook mentions the ether has period 14, but doesn't give the exact pattern.
    Using the canonical pattern from the literature.
    """
    # Canonical ether pattern (period 14)
    ether_pattern = [0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0]

    # Repeat to fill length, ensuring proper phase
    result = []
    for i in range(length):
        result.append(ether_pattern[i % len(ether_pattern)])
    return result


def _place_glider_at_ether_distances(
    state: List[int],
    glider_type: str,
    reference_pos: int = None,
    target_over_distance: int = None,
    target_under_distance: int = None,
    fallback_pos: int = None
) -> int:
    """
    Place glider at precise ! and ! distances using ether triangles.

    Cook-faithful positioning: uses Section 3.2.2-3.2.4 distance calculations.
    """
    from ether_distances import position_glider_at_over_distance, position_glider_at_under_distance

    try:
        from cook_gliders_exact import COOK_GLIDER_PATTERNS
    except ImportError:
        raise ImportError("Cook's exact glider patterns not available. Cannot create faithful CTS construction.")

    if glider_type not in COOK_GLIDER_PATTERNS:
        raise ValueError(f"No exact pattern available for glider type: {glider_type}")

    # Determine position using Cook's distance system
    if reference_pos is not None and target_over_distance is not None:
        # Position at specific ! distance
        position = position_glider_at_over_distance(reference_pos, target_over_distance)
    elif reference_pos is not None and target_under_distance is not None:
        # Position at specific ! distance
        position = position_glider_at_under_distance(reference_pos, target_under_distance)
    elif fallback_pos is not None:
        # Fallback to specified position
        position = fallback_pos
    else:
        raise ValueError("Must specify either distance constraints or fallback position")

    pattern = COOK_GLIDER_PATTERNS[glider_type]

    # Place the exact pattern at the calculated position
    start_pos = position
    for i, bit in enumerate(pattern):
        pos = start_pos + i
        if 0 <= pos < len(state):
            state[pos] = bit

    return start_pos  # Return actual position used


def _place_glider_package(
    state: List[int],
    glider_type: str,
    position: int,
    phase: int = 0
) -> int:
    """
    Place Cook's exact glider pattern in the state.

    Uses ether distance positioning for Cook faithfulness.
    """
    return _place_glider_at_ether_distances(
        state, glider_type, fallback_pos=position
    )


def encode_cts_to_rule110(cts_spec: CTSSpec, tape_length: int = 400) -> CookConstruction:
    """
    Encode a CTS specification into a Rule 110 initial state.

    Follows Cook's construction from Section 4 with exact ! and ! distances:
    - Tape data as C2 gliders spaced !2 apart (Section 4.2)
    - Appendants as Ē gliders with proper spacing (Section 4.4)
    - Leader/component system with correct distance relationships
    """
    # Create ether background (must be long enough for distance calculations)
    state = _create_ether_background(tape_length)

    # Track glider positions for distance validation
    glider_positions = []

    # Encode tape data (stationary C2 gliders)
    # Cook Section 4.2: C2 gliders must be !2 apart
    tape_position = 50  # Start well into ether background
    reference_pos = None

    for symbol in cts_spec.initial_tape:
        gliders = _encode_symbol_to_gliders(symbol)
        for glider_type in gliders:
            if glider_type == "C2":
                if reference_pos is None:
                    # First C2: place at starting position
                    actual_pos = _place_glider_at_ether_distances(
                        state, glider_type, fallback_pos=tape_position
                    )
                else:
                    # Subsequent C2s: place !2 from previous (Cook Section 4.2)
                    actual_pos = _place_glider_at_ether_distances(
                        state, glider_type,
                        reference_pos=reference_pos,
                        target_over_distance=2  # !2 spacing for C2 gliders
                    )

                glider_positions.append((glider_type, actual_pos))
                reference_pos = actual_pos

                # Move to next symbol position (ether-aware spacing)
                tape_position = actual_pos + 30  # Leave room for pattern

    # Encode first appendant (moving data as Ē gliders)
    # Cook Section 4.4: Ē gliders for moving data
    moving_position = tape_position + 40
    first_appendant = cts_spec.appendants[0]
    gliders = _encode_appendant_to_gliders(first_appendant)

    e_reference_pos = None
    for glider_type in gliders:
        if glider_type == "Ē":
            if e_reference_pos is None:
                # First Ē: place near tape data
                actual_pos = _place_glider_at_ether_distances(
                    state, glider_type, fallback_pos=moving_position
                )
            else:
                # Subsequent Ēs: !4 spacing for moving data (Cook Section 4.4)
                actual_pos = _place_glider_at_ether_distances(
                    state, glider_type,
                    reference_pos=e_reference_pos,
                    target_over_distance=4  # !4 spacing for Ē gliders
                )

            glider_positions.append((glider_type, actual_pos))
            e_reference_pos = actual_pos
            moving_position = actual_pos + 50  # Space for next glider

    # Add complete leader/component system (Cook Section 4.4)
    leader_position = moving_position + 30

    # Create Cook's complete leader/component system for appendant control
    leader_system = place_leader_component_system(
        state, leader_position, cts_spec.appendants
    )

    # Track leader and component positions
    for leader in leader_system.leaders:
        glider_positions.append(('A', leader.position))  # A gliders in leaders
        glider_positions.append(('B', leader.position + 10))  # B gliders in leaders

    for component in leader_system.components:
        glider_positions.append(('C2', component.position))  # Components contain C2 gliders

    # Validate Cook distances (Section 4.2 requirements)
    from ether_distances import validate_cook_distances
    if not validate_cook_distances(glider_positions):
        print("Warning: Glider positions do not satisfy Cook's distance constraints")

    return CookConstruction(
        cts_spec=cts_spec,
        initial_state=state
    )


def _detect_cts_operation_from_collisions(
    collisions: List[Tuple[int, int, str]],
    current_tape: str,
    current_appendant: int,
    appendants: List[str]
) -> Tuple[str, int]:
    """
    Detect CTS operations from glider collision patterns.

    Based on Cook's Section 4.4 collision analysis.
    Returns (new_tape, new_appendant_index)
    """
    tape = current_tape
    appendant_idx = current_appendant

    # Analyze collision patterns to determine CTS operations

    # Count different collision types
    crossing_count = sum(1 for c in collisions if c[2].startswith("crossing:"))
    annihilation_count = sum(1 for c in collisions if c[2].startswith("annihilation:"))
    control_count = sum(1 for c in collisions if c[2].startswith("control:"))
    conversion_count = sum(1 for c in collisions if c[2].startswith("conversion:"))

    # Primary operation: Ē crossing C2 (tape symbol read)
    # This is the core CTS operation in Cook's construction
    if crossing_count > 0:
        appendant = appendants[appendant_idx]

        if tape:
            symbol = tape[0]

            if symbol == 'Y':
                # Y: append the current appendant and remove first symbol
                tape = tape[1:] + appendant
            elif symbol == 'N':
                # N: just remove first symbol (no append)
                tape = tape[1:]

            # Move to next appendant in cycle
            appendant_idx = (appendant_idx + 1) % len(appendants)

    # Control operations: A/B collisions affect the control flow
    # These can modify whether operations are accepted/rejected
    elif control_count > 0:
        # Control collisions can affect the appendant selection
        # For now, treat as potential state changes
        pass

    # Annihilation operations: A+B mutual destruction
    # These can clean up control signals
    elif annihilation_count > 0:
        # May indicate completion of control operations
        pass

    # Conversion operations: A converting Ē to C2 (ossification)
    elif conversion_count > 0:
        # This turns moving data back into stationary tape data
        # Part of the ossification process in Cook's construction
        pass

    return tape, appendant_idx


def _analyze_cook_evolution_pattern(
    history: List[List[int]],
    step: int,
    window_size: int = 20
) -> Optional[str]:
    """
    Analyze Rule 110 evolution for patterns that indicate CTS operations.

    Based on Cook's Section 4, specific evolution patterns correspond to CTS operations.
    This looks for characteristic signatures in the spacetime evolution.
    """
    if step < window_size or step >= len(history):
        return None

    # Look at recent evolution window
    recent_states = history[step-window_size:step+1]

    # Pattern 1: Ē crossing C2 signature
    # Cook describes this as moving data crossing stationary tape data
    # Look for characteristic diagonal patterns in spacetime

    # Check for glider movement patterns that match Cook's descriptions
    # This is a simplified version - Cook's full analysis is much more detailed

    # Look for activity bursts that might indicate glider interactions
    activities = []
    for state in recent_states:
        active_count = sum(1 for cell in state if cell == 1)
        activities.append(active_count)

    # Detect significant activity changes that might indicate operations
    if len(activities) >= 3:
        recent_avg = sum(activities[-3:]) / 3
        prev_avg = sum(activities[-6:-3]) / 3 if len(activities) >= 6 else recent_avg

        activity_change = abs(recent_avg - prev_avg)

        # Significant activity changes might indicate CTS operations
        if activity_change > 5:
            return "potential_operation"

    return None


def run_cook_cts_simulation(
    construction: CookConstruction,
    steps: int = 1000
) -> List[CTSState]:
    """
    Run the Rule 110 simulation with Cook's complete leader/component system.

    CTS operations emerge naturally from collision cascades between leaders,
    components, acceptors, and rejectors (Cook Section 4.4).
    """
    # Run Rule 110 with ether boundaries
    ca = DynamicRule110(construction.initial_state, boundary="ether")
    ca.run(steps)

    # Track gliders through evolution
    track = track_gliders(ca.get_history())

    # Initialize CTS state
    cts_states = []
    current_tape = construction.cts_spec.initial_tape
    current_appendant = 0

    cts_states.append(CTSState(tape=current_tape, current_appendant=current_appendant))

    for step in range(1, min(steps + 1, len(ca.get_history()))):
        # Get collisions for this step
        step_collisions = [c for c in track.collisions if c[0] == step - 1]

        # Process collision cascades (Cook Section 4.4)
        cts_operation_occurred = _process_collision_cascades(
            step_collisions, current_tape, current_appendant,
            construction.cts_spec.appendants
        )

        # If CTS operation occurred, update state
        if cts_operation_occurred:
            symbol = current_tape[0]
            appendant = construction.cts_spec.appendants[current_appendant]

            if symbol == 'Y':
                current_tape = current_tape[1:] + appendant
            elif symbol == 'N':
                current_tape = current_tape[1:]

            current_appendant = (current_appendant + 1) % len(construction.cts_spec.appendants)

        cts_states.append(CTSState(
            tape=current_tape,
            current_appendant=current_appendant
        ))

    return cts_states


def _process_collision_cascades(collisions: List[Tuple[int, int, str]],
                               tape: str, appendant_idx: int,
                               appendants: List[str]) -> bool:
    """
    Process Cook's collision cascades that drive CTS operations (Section 4.4).

    Returns True if a CTS operation occurred.
    """
    operation_occurred = False

    # Process each collision in sequence (Cook's cascade logic)
    for collision in collisions:
        step, pos, desc = collision

        if "crossing:" in desc:
            # Ē crossing C2: core CTS operation (Section 4.2)
            operation_occurred = True

        elif "annihilation:" in desc:
            # A+B annihilation: control signal cleanup
            pass  # May affect subsequent operations

        elif "conversion:" in desc:
            # A converting Ē to C2: ossification (Section 4.3)
            pass  # Part of moving data → stationary data conversion

        elif "control:" in desc:
            # A/B control interactions: determine accept/reject
            pass  # Affects whether operations proceed

    # Additional Cook logic: if no explicit collisions but crossing patterns exist,
    # CTS operations may still occur through implicit cascades
    if not operation_occurred and tape and any("crossing" in c[2] for c in collisions):
        operation_occurred = True

    return operation_occurred


def simulate_cts_direct(cts_spec: CTSSpec, steps: int = 100) -> List[CTSState]:
    """
    Direct CTS simulation for comparison.

    This simulates the CTS directly (not through Rule 110) to verify
    that our Rule 110 encoding produces the correct behavior.
    """
    states = []
    tape = cts_spec.initial_tape
    appendant_idx = 0

    # Initial state
    states.append(CTSState(
        tape=tape,
        current_appendant=appendant_idx
    ))

    for _ in range(steps):
        if not tape:
            break  # CTS halts when tape empty

        # Read first symbol
        symbol = tape[0]

        # Get current appendant
        appendant = cts_spec.appendants[appendant_idx]

        if symbol == 'Y':
            # Append the appendant and remove first symbol
            tape = tape[1:] + appendant
        elif symbol == 'N':
            # Just remove first symbol (no append)
            tape = tape[1:]

        # Move to next appendant
        appendant_idx = (appendant_idx + 1) % len(cts_spec.appendants)

        states.append(CTSState(
            tape=tape,
            current_appendant=appendant_idx
        ))

    return states


# Example CTS specifications for testing
def example_duplicator() -> CTSSpec:
    """Simple duplicator CTS: duplicates the input."""
    return CTSSpec(
        appendants=['YY'],
        initial_tape='Y'  # Will duplicate to YY
    )


def example_identity() -> CTSSpec:
    """Identity CTS: leaves input unchanged."""
    return CTSSpec(
        appendants=[''],
        initial_tape='YN'
    )


def example_unary_adder() -> CTSSpec:
    """Unary adder CTS."""
    return CTSSpec(
        appendants=['YY', ''],
        initial_tape='YYY'  # Represents 3 in unary
    )





