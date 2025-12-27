"""
Cook's ! and ! distance calculations using ether triangles.

Implements Section 3.2.2-3.2.4 of Cook's paper: precise distance measurements
using diagonal ether rows (!) and vertical ether columns (!).

These distances are fundamental to Cook's construction - gliders must be
positioned at exact ! and ! distances for collisions to work correctly.
"""

from typing import List, Tuple, Optional
from cook_gliders_exact import ETHER_PATTERN


def get_ether_triangle_row(position: int, ether_start: int = 0) -> int:
    """
    Get the diagonal ether row number for a position.

    Cook's ! distance: diagonal ether rows, measured in units where
    each row represents one diagonal step through the ether pattern.

    Args:
        position: Cell position in the lattice
        ether_start: Starting position of ether pattern (usually 0)

    Returns:
        Diagonal row number (for ! distance calculations)
    """
    # The diagonal rows slope down and to the right
    # Each row represents positions where (x + y) mod something gives row number

    # In Cook's ether, the diagonal lines follow the pattern repetition
    # For the standard ether pattern, diagonal rows are measured in steps of 7
    relative_pos = position - ether_start
    row = relative_pos // 7  # 7 cells per diagonal step in ether

    return row


def get_ether_triangle_column(position: int, ether_start: int = 0) -> int:
    """
    Get the vertical ether column number for a position.

    Cook's ! distance: vertical ether columns, measured in units where
    each column represents one vertical step through ether triangles.

    Args:
        position: Cell position in the lattice
        ether_start: Starting position of ether pattern (usually 0)

    Returns:
        Vertical column number (for ! distance calculations)
    """
    # Vertical columns are measured in steps that match the ether period
    relative_pos = position - ether_start
    column = relative_pos // len(ETHER_PATTERN)  # One column per ether period

    return column


def calculate_over_distance(glider1_pos: int, glider2_pos: int,
                          ether_start: int = 0) -> int:
    """
    Calculate ! distance (diagonal ether rows) between two positions.

    Cook Section 3.2.2: ! distance measured using diagonal ether rows.
    For Ē gliders, this is mod 6.

    Args:
        glider1_pos: Position of first glider
        glider2_pos: Position of second glider
        ether_start: Starting position of ether pattern

    Returns:
        ! distance (positive for glider2 right of glider1)
    """
    row1 = get_ether_triangle_row(glider1_pos, ether_start)
    row2 = get_ether_triangle_row(glider2_pos, ether_start)

    distance = row2 - row1

    # For Ē gliders, ! distance is mod 6 (Cook Section 3.2.3)
    return distance % 6


def calculate_under_distance(glider1_pos: int, glider2_pos: int,
                           ether_start: int = 0) -> int:
    """
    Calculate ! distance (vertical ether columns) between two positions.

    Cook Section 3.2.3: ! distance measured using vertical ether columns.
    For Ē gliders, this is mod 4.

    Args:
        glider1_pos: Position of first glider
        glider2_pos: Position of second glider
        ether_start: Starting position of ether pattern

    Returns:
        ! distance (positive for glider2 right of glider1)
    """
    col1 = get_ether_triangle_column(glider1_pos, ether_start)
    col2 = get_ether_triangle_column(glider2_pos, ether_start)

    distance = col2 - col1

    # For Ē gliders, ! distance is mod 4 (Cook Section 3.2.3)
    return distance % 4


def position_glider_at_over_distance(reference_pos: int, target_over_distance: int,
                                   ether_start: int = 0) -> int:
    """
    Position a glider at a specific ! distance from a reference glider.

    Args:
        reference_pos: Position of reference glider
        target_over_distance: Desired ! distance
        ether_start: Starting position of ether pattern

    Returns:
        Position for the new glider
    """
    reference_row = get_ether_triangle_row(reference_pos, ether_start)

    # Find position in target row
    target_row = (reference_row + target_over_distance) % 6

    # Convert back to position (approximate)
    # This is simplified - Cook has more precise positioning rules
    row_offset = target_over_distance * 7  # 7 cells per diagonal step

    return reference_pos + row_offset


def position_glider_at_under_distance(reference_pos: int, target_under_distance: int,
                                    ether_start: int = 0) -> int:
    """
    Position a glider at a specific ! distance from a reference glider.

    Args:
        reference_pos: Position of reference glider
        target_under_distance: Desired ! distance
        ether_start: Starting position of ether pattern

    Returns:
        Position for the new glider
    """
    reference_col = get_ether_triangle_column(reference_pos, ether_start)

    # Find position in target column
    target_col = (reference_col + target_under_distance) % 4

    # Convert back to position (approximate)
    # This is simplified - Cook has more precise positioning rules
    col_offset = target_under_distance * len(ETHER_PATTERN)  # One period per column

    return reference_pos + col_offset


def find_collision_positions(glider1_pos: int, glider2_pos: int,
                           ether_start: int = 0) -> List[Tuple[int, int]]:
    """
    Find positions where two gliders will collide based on their ! and ! distances.

    Cook's collision detection is based on distance relationships, not spatial proximity.

    Args:
        glider1_pos: Position of first glider
        glider2_pos: Position of second glider
        ether_start: Starting position of ether pattern

    Returns:
        List of (step, position) tuples where collisions occur
    """
    # Calculate current distances
    over_dist = calculate_over_distance(glider1_pos, glider2_pos, ether_start)
    under_dist = calculate_under_distance(glider1_pos, glider2_pos, ether_start)

    # Cook's collision analysis (Section 3.2.3) determines when gliders interact
    # This is simplified - full analysis considers glider velocities and periods

    collision_positions = []

    # For Ē crossing C2 collisions (key CTS operations)
    if over_dist in [1, 3] and under_dist in [0, 2]:  # Cook's crossing configurations
        # Calculate collision step based on relative velocities
        # Ē velocity = -4/15, C2 velocity = 0, so Ē approaches C2
        steps_to_collision = abs(glider2_pos - glider1_pos) * 15 // 4  # Approximate
        collision_pos = (glider1_pos + glider2_pos) // 2
        collision_positions.append((steps_to_collision, collision_pos))

    return collision_positions


def validate_cook_distances(glider_positions: List[Tuple[str, int]],
                          ether_start: int = 0) -> bool:
    """
    Validate that glider positions satisfy Cook's distance constraints.

    Section 4.2-4.4 specify exact distance requirements for CTS construction.

    Args:
        glider_positions: List of (glider_type, position) tuples
        ether_start: Starting position of ether pattern

    Returns:
        True if distances are Cook-compliant
    """
    # Check C2 spacing: must be !2 apart (Cook Section 4.2)
    c2_positions = [pos for gtype, pos in glider_positions if gtype == "C2"]

    for i in range(1, len(c2_positions)):
        over_dist = calculate_over_distance(c2_positions[i-1], c2_positions[i], ether_start)
        if over_dist != 2:
            return False

    # Check Ē spacing: must be !4 apart for moving data (Cook Section 4.4)
    e_positions = [pos for gtype, pos in glider_positions if gtype == "Ē"]

    for i in range(1, len(e_positions)):
        over_dist = calculate_over_distance(e_positions[i-1], e_positions[i], ether_start)
        if over_dist != 4:
            return False

    return True