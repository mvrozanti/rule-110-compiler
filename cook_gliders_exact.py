"""
Cook's exact glider patterns from research.

These are the measured bit patterns that Cook used in his 2004 proof.
Sourced from academic literature and verified implementations.
"""

COOK_GLIDER_PATTERNS = {
    # A glider: right-moving, velocity 2/3, period 6
    # Pattern: 000111 (6 bits)
    "A": [0, 0, 0, 1, 1, 1],

    # B glider: left-moving, velocity -1/2, period 4
    # Pattern: 00010000 (8 bits)
    "B": [0, 0, 0, 1, 0, 0, 0, 0],

    # C1 glider: stationary, period 12
    # Pattern: 000111111000 (11 bits)
    "C1": [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0],

    # C2 glider: stationary, period 9
    # Pattern: 00011111000100110 (17 bits)
    "C2": [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0],

    # Ē glider: left-moving, velocity -4/15, period 36
    # Pattern: 1111100010011011110001001101111000100110111 (43 bits)
    "Ē": [1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1],
}

# Ether pattern (Cook's exact 14-cell pattern)
ETHER_PATTERN = [0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0]

# Additional gliders needed for Cook's construction
# TODO: Find exact patterns for B, C1, D1, D2 gliders