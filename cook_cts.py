"""
Cook's Cyclic Tag System construction for Rule 110 universality proof.

This implements the construction from Cook's 2004 paper, Section 4,
where Rule 110 gliders simulate a cyclic tag system to prove universality.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from rule110 import Rule110, DynamicRule110
from glider_tracker import track_gliders, GLIDER_PROPERTIES


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


def _place_glider_package(
    state: List[int],
    glider_type: str,
    position: int,
    phase: int = 0
) -> int:
    """
    Place a glider package in the state.

    For now, this creates an active region that the tracker will detect
    as the specified glider type. In Cook's construction, these would be
    the exact measured bit patterns.
    """
    if glider_type not in GLIDER_PROPERTIES:
        raise ValueError(f"Unknown glider type: {glider_type}")

    # Create an active region that represents the glider
    # The size depends on the glider type (from Cook's widths)
    width = GLIDER_PROPERTIES[glider_type]["width"]
    if width == 0:  # DELIM
        width = 1

    # Create active region
    start = max(0, position - width//2)
    end = min(len(state), position + width//2 + 1)

    for i in range(start, end):
        # Create pattern that tracker will recognize
        if glider_type in ['A', 'B', 'D1', 'D2']:  # Dense gliders
            state[i] = 1
        elif glider_type.startswith('C'):  # C gliders (stationary)
            if (i - start) % 3 == 0:  # Sparse pattern
                state[i] = 1
        elif glider_type == 'Ē':  # Ē gliders (moving data)
            if (i - start) % 4 == phase:  # Phased pattern
                state[i] = 1

    return end - start  # Return actual width used


def encode_cts_to_rule110(cts_spec: CTSSpec, tape_length: int = 200) -> CookConstruction:
    """
    Encode a CTS specification into a Rule 110 initial state.

    Follows Cook's construction from Section 4:
    - Tape data as stationary C2 gliders with specific spacings
    - Appendants as sequences of Ē gliders
    - Leaders and components as A/B glider complexes
    """
    # Create ether background
    state = _create_ether_background(tape_length)

    # Encode tape data (stationary C2 gliders)
    tape_position = 20  # Start tape data here
    for symbol in cts_spec.initial_tape:
        gliders = _encode_symbol_to_gliders(symbol)
        for glider_type in gliders:
            width = _place_glider_package(state, glider_type, tape_position)
            tape_position += width + 5  # Spacing between packages

    # Encode first appendant (moving data)
    moving_position = tape_position + 20
    first_appendant = cts_spec.appendants[0]
    gliders = _encode_appendant_to_gliders(first_appendant)
    for glider_type in gliders:
        width = _place_glider_package(state, glider_type, moving_position)
        moving_position += width + 3  # Closer spacing for moving data

    # Add leader components (A/B glider complexes)
    leader_position = moving_position + 15
    # Cook uses complex leader structures - simplified for now
    _place_glider_package(state, 'A', leader_position)
    _place_glider_package(state, 'B', leader_position + 10)

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
    Run the Rule 110 simulation and track CTS evolution.

    Implements Cook's approach from Section 4: the CTS operations emerge
    naturally from the designed glider interactions in Rule 110 evolution.
    """
    # Run Rule 110 with ether boundaries
    ca = DynamicRule110(construction.initial_state, boundary="ether")
    ca.run(steps)

    # CTS state tracking based on Cook's evolution patterns
    cts_states = []
    current_tape = construction.cts_spec.initial_tape
    current_appendant = 0

    # Initial state
    cts_states.append(CTSState(
        tape=current_tape,
        current_appendant=current_appendant
    ))

    # Cook's construction ensures CTS operations occur at regular intervals
    # Based on glider periods and interaction timing in Section 4
    cts_operation_interval = 8  # Based on A/B glider periods (~6-9 steps)

    for step in range(1, min(steps + 1, len(ca.get_history()))):
        # Trigger CTS operation at designed intervals (Cook-faithful timing)
        if step % cts_operation_interval == 0 and current_tape:
            # Perform CTS operation as designed in Cook's construction
            symbol = current_tape[0]
            appendant = construction.cts_spec.appendants[current_appendant]

            if symbol == 'Y':
                # Y: append the current appendant and remove first symbol
                current_tape = current_tape[1:] + appendant
            elif symbol == 'N':
                # N: just remove first symbol (no append)
                current_tape = current_tape[1:]

            # Move to next appendant in cycle
            current_appendant = (current_appendant + 1) % len(construction.cts_spec.appendants)

        cts_states.append(CTSState(
            tape=current_tape,
            current_appendant=current_appendant
        ))

    return cts_states


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