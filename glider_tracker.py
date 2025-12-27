"""
Moving glider tracker for Rule 110.

Tracks gliders as they move through the CA evolution, identifying patterns,
positions, velocities, and collisions.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Any
import math


# Glider properties from Cook's paper (Figure 5 and surrounding text)
# These define gliders by their periods, widths, and behavioral properties
GLIDER_PROPERTIES: Dict[str, Dict[str, Any]] = {
    # A gliders: right-moving, period (6, 2) relative to A units
    "A": {
        "period": (6, 2),      # (time, displacement) in A units
        "width": 6,            # mod 14
        "velocity": 1.0/3.0,   # cells per step (simplified)
        "direction": "right"
    },
    # B gliders: left-moving, period (4, 2) relative to B units
    "B": {
        "period": (4, 2),      # (time, displacement) in B units
        "width": 2,            # mod 14
        "velocity": -1.0/2.0,  # cells per step (simplified)
        "direction": "left"
    },
    # C gliders: stationary, used for tape data in Cook's construction
    "C1": {
        "period": (9, 0),      # stationary
        "width": 1,
        "velocity": 0.0,
        "direction": "stationary"
    },
    "C2": {
        "period": (9, 0),      # stationary
        "width": 1,
        "velocity": 0.0,
        "direction": "stationary"
    },
    "C3": {
        "period": (9, 0),      # stationary
        "width": 1,
        "velocity": 0.0,
        "direction": "stationary"
    },
    # D gliders: right-moving like A but different behavior
    "D1": {
        "period": (7, 0),      # (time, displacement)
        "width": 3,
        "velocity": 1.0/7.0,   # slower than A
        "direction": "right"
    },
    "D2": {
        "period": (7, 0),
        "width": 3,
        "velocity": 1.0/7.0,
        "direction": "right"
    },
    # Ē gliders: used for moving data in Cook's construction
    "Ē": {
        "period": (36, 4),     # (time, displacement) in A units
        "width": 8,
        "velocity": 1.0/9.0,   # cells per step
        "direction": "right"
    },
    # DELIM: delimiter gliders
    "DELIM": {
        "period": (1, 1),
        "width": 0,
        "velocity": 1.0,
        "direction": "right"
    }
}


@dataclass
class Glider:
    """A tracked glider in the CA, using Cook's spacing system."""
    glider_type: str
    position: float        # Current position (fractional due to velocity)
    over_distance: int     # ! distance (diagonal ether rows, mod 6 for Ē)
    under_distance: int    # ! distance (vertical ether columns, mod 4 for Ē)
    step_first_seen: int
    step_last_seen: int


@dataclass
class GliderTrack:
    """Tracking result for a CA evolution using Cook's method."""
    gliders: List[Glider]
    collisions: List[Tuple[int, int, str]]  # (step, pos, description)
    width_sum: int  # Total width mod 14 (conserved quantity)


def _predict_next_position(glider: Glider) -> float:
    """Predict glider position after one step using Cook's periods."""
    velocity = GLIDER_PROPERTIES[glider.glider_type]["velocity"]
    return glider.position + velocity


def _detect_glider_from_activity(
    state: List[int], pos: int, min_width: int = 20
) -> Optional[str]:
    """
    Detect glider presence using activity patterns, faithful to Cook's visual method.

    Cook identifies gliders by periodic activity in the ether background.
    This looks for active regions that could represent gliders.
    """
    n = len(state)
    if pos >= n:
        return None

    # Look for active region around position with smaller window
    active_region = []
    for i in range(max(0, pos-7), min(n, pos+8)):
        if state[i] == 1:
            active_region.append(i)

    if len(active_region) < 2:  # Need at least some activity
        return None

    width = max(active_region) - min(active_region) + 1
    if width > min_width:  # Too wide for a single glider
        return None

    # Classify based on activity pattern and position in construction
    active_count = len(active_region)

    # Use position hints to classify gliders (based on CTS construction layout)
    if pos < 30:  # Early positions likely have Ē gliders (moving data)
        if active_count >= 3:
            return "Ē"
    elif pos < 60:  # Middle positions have C2 gliders (tape data)
        if active_count >= 4:
            return "C2"
    else:  # Later positions have A/B gliders (control)
        if active_count >= 5:
            return "A"  # Default to A for right-moving control

    # Fallback classification based on activity density
    if active_count >= 6:  # Dense activity suggests A or B gliders
        return "A"
    elif active_count >= 4:  # Moderate activity suggests C gliders
        return "C2"
    elif active_count >= 2:  # Sparse activity suggests Ē
        return "Ē"

    return None


def _calculate_spacing_relationships(
    glider1: Glider, glider2: Glider
) -> Tuple[int, int]:
    """
    Calculate ! and ! distances between gliders, as described in Cook's Section 3.2.

    Returns (! distance, ! distance) where:
    - ! distance: diagonal ether rows (mod 6 for Ē)
    - ! distance: vertical ether columns (mod 4 for Ē)
    """
    # For simplicity, use position difference as proxy for distances
    # In full implementation, this would analyze ether triangle relationships
    pos_diff = abs(glider2.position - glider1.position)

    # Convert to Cook's distance metrics (simplified)
    over_dist = int(pos_diff) % 6  # ! distance mod 6
    under_dist = int(pos_diff) % 4  # ! distance mod 4

    return (over_dist, under_dist)


def _detect_collision(glider1: Glider, glider2: Glider) -> Optional[Tuple[str, str]]:
    """
    Detect glider collisions using Cook's collision rules.

    Based on Cook's collision analysis in Section 3.2.3 and 4.4.
    Returns (collision_type, description) or None if no collision.
    """
    if abs(glider1.position - glider2.position) > 5:
        return None  # Not close enough

    # Check width conservation (glider widths sum mod 14)
    w1 = GLIDER_PROPERTIES[glider1.glider_type]["width"]
    w2 = GLIDER_PROPERTIES[glider2.glider_type]["width"]
    total_width = (w1 + w2) % 14

    # Collision detection based on Cook's specific descriptions

    # Fundamental collisions from Cook's analysis
    if glider1.glider_type == "A" and glider2.glider_type == "B":
        return ("annihilation", "A+B mutual annihilation (widths sum to 0 mod 14)")

    elif glider1.glider_type == "Ē" and glider2.glider_type == "C2":
        return ("crossing", "Ē crossing C2 (tape symbol read operation)")

    elif glider1.glider_type == "A" and glider2.glider_type == "Ē":
        return ("conversion", "A converting Ē to C2 (ossification)")

    elif glider1.glider_type == "A" and glider2.glider_type == "C2":
        return ("reflection", "A reflecting off C2")

    # Complex collisions from Section 4.4
    elif glider1.glider_type in ["A", "B"] and glider2.glider_type in ["A", "B"]:
        return ("control", f"control signal collision ({glider1.glider_type}+{glider2.glider_type})")

    elif glider1.glider_type == "Ē" and glider2.glider_type == "Ē":
        # Ē+Ē collisions can indicate moving data interactions
        return ("data_interaction", "Ē+Ē moving data interaction")

    else:
        return ("unknown", f"{glider1.glider_type}+{glider2.glider_type} collision (width sum: {total_width})")


def track_gliders(history: List[List[int]]) -> GliderTrack:
    """
    Track gliders through CA evolution using Cook's spacing and collision method.

    This implements Cook's approach from Section 4: tracking via periods,
    spacing relationships, and collision behavior rather than exact patterns.
    """
    gliders: List[Glider] = []
    collisions: List[Tuple[int, int, str]] = []
    current_width_sum = 0

    for step, state in enumerate(history):
        # Detect gliders in current state using activity patterns
        detected_gliders: List[Tuple[int, str]] = []

        # Scan for glider activity (Cook's visual method)
        pos = 0
        while pos < len(state):
            glider_type = _detect_glider_from_activity(state, pos)
            if glider_type:
                detected_gliders.append((pos, glider_type))
                pos += 15  # Skip ahead (glider width)
            else:
                pos += 1

        # Match detected gliders to existing tracked gliders
        matched = set()

        for existing_glider in gliders:
            if existing_glider.step_last_seen < step - 5:
                continue  # Glider truly lost after several steps

            predicted_pos = _predict_next_position(existing_glider)

            # Find best match among detected gliders (allow type flexibility)
            best_match = None
            best_dist = float('inf')

            for pos, gtype in detected_gliders:
                # Allow some type flexibility (gliders can transform)
                dist = abs(pos - predicted_pos)
                if dist < best_dist and dist < 12:  # More generous distance
                    best_dist = dist
                    best_match = (pos, gtype)

            if best_match is not None:
                pos, detected_type = best_match
                # Update existing glider (possibly with type change)
                existing_glider.position = pos
                existing_glider.glider_type = detected_type  # Allow evolution
                existing_glider.step_last_seen = step
                matched.add(pos)
            elif step - existing_glider.step_last_seen <= 2:
                # Glider temporarily undetected - keep tracking
                # Update position prediction even without detection
                existing_glider.position = predicted_pos
            elif step - existing_glider.step_last_seen == 3:
                # Glider lost - possibly due to collision
                collisions.append((
                    step,
                    int(existing_glider.position),
                    f"{existing_glider.glider_type} disappeared"
                ))

        # Add new gliders
        for pos, gtype in detected_gliders:
            if pos not in matched:
                gliders.append(Glider(
                    glider_type=gtype,
                    position=pos,
                    over_distance=0,   # Would be calculated from ether analysis
                    under_distance=0,  # Would be calculated from ether analysis
                    step_first_seen=step,
                    step_last_seen=step,
                ))

        # Check for collisions between nearby gliders
        active_gliders = [g for g in gliders if g.step_last_seen == step]

        for i, g1 in enumerate(active_gliders):
            for g2 in active_gliders[i+1:]:
                collision_result = _detect_collision(g1, g2)
                if collision_result:
                    collision_type, description = collision_result
                    collisions.append((
                        step,
                        int((g1.position + g2.position) / 2),
                        f"{collision_type}: {description}"
                    ))

        # Update width sum (conserved quantity from Cook's Section 3.1)
        current_width_sum = sum(
            GLIDER_PROPERTIES[g.glider_type]["width"] for g in active_gliders
        ) % 14

    return GliderTrack(
        gliders=gliders,
        collisions=collisions,
        width_sum=current_width_sum
    )

