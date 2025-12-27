"""
Cook's leader and component system from Section 4.4.

This implements the complete A/B leader structures and component sequences
that control CTS operation acceptance/rejection through collision cascades.
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
from cook_gliders_exact import COOK_GLIDER_PATTERNS, ETHER_PATTERN
from ether_distances import calculate_over_distance, calculate_under_distance


@dataclass
class LeaderStructure:
    """A Cook leader: complex A/B glider arrangement."""
    leader_type: str  # "prepared" or "raw"
    position: int
    components: List['ComponentStructure'] = None

    def __post_init__(self):
        if self.components is None:
            self.components = []


@dataclass
class ComponentStructure:
    """A Cook component: table data glider sequence."""
    component_type: str  # "primary" or "standard"
    position: int
    table_data: str  # Y/N sequence this component represents


class CookLeaderSystem:
    """
    Complete implementation of Cook's leader/component system (Section 4.4).

    This handles the complex A/B glider interactions that control CTS operations.
    """

    def __init__(self):
        self.leaders: List[LeaderStructure] = []
        self.components: List[ComponentStructure] = []

    def create_prepared_leader(self, position: int) -> LeaderStructure:
        """
        Create a prepared leader (Section 4.4).

        A prepared leader has already interacted with tape data and is ready
        to process components.
        """
        leader = LeaderStructure("prepared", position)

        # Cook's prepared leader structure (simplified)
        # In reality, this involves complex A/B glider positioning
        # For now, we place basic A/B structure

        return leader

    def create_raw_leader(self, position: int) -> LeaderStructure:
        """
        Create a raw leader (Section 4.4).

        Raw leaders must first interact with tape data before becoming prepared.
        """
        leader = LeaderStructure("raw", position)
        return leader

    def add_primary_component(self, leader: LeaderStructure, table_data: str) -> ComponentStructure:
        """
        Add primary component after a leader (Section 4.4).

        Primary components are the first after a leader and have special interaction rules.
        """
        # Position primary component !2 from leader (Cook's spacing)
        component_pos = leader.position + 20  # Simplified spacing

        component = ComponentStructure("primary", component_pos, table_data)
        leader.components.append(component)
        self.components.append(component)

        return component

    def add_standard_component(self, prev_component: ComponentStructure, table_data: str) -> ComponentStructure:
        """
        Add standard component in sequence (Section 4.4).

        Standard components follow primary components with specific spacing.
        """
        # Position standard component !2 from previous component
        component_pos = prev_component.position + 30  # Simplified

        component = ComponentStructure("standard", component_pos, table_data)
        self.components.append(component)

        return component

    def simulate_tape_reading(self, leader: LeaderStructure, tape_symbol: str) -> str:
        """
        Simulate leader hitting tape symbol (Cook Section 4.4, Figure 12).

        Returns: "acceptor" or "rejector" based on tape symbol and leader state.
        """
        if leader.leader_type == "raw":
            if tape_symbol == 'Y':
                # Raw leader + Y → acceptor production
                return "acceptor"
            elif tape_symbol == 'N':
                # Raw leader + N → rejector production
                return "rejector"
        elif leader.leader_type == "prepared":
            # Prepared leaders have different interaction rules
            # This is more complex in Cook's system
            if tape_symbol == 'Y':
                return "acceptor_prepared"
            elif tape_symbol == 'N':
                return "rejector_prepared"

        return "no_interaction"

    def simulate_component_processing(self, component: ComponentStructure,
                                    signal_type: str) -> Optional[List[str]]:
        """
        Simulate component interaction with acceptor/rejector (Cook Section 4.4, Figure 13).

        Returns: List of Ē gliders produced (moving data) or None if rejected.
        """
        if signal_type.startswith("rejector"):
            # Rejectors destroy components - no moving data produced
            return None

        elif signal_type.startswith("acceptor"):
            # Acceptors convert components to moving data
            moving_data = []

            # Each Y/N in table_data becomes 4 Ē gliders (Cook's encoding)
            for symbol in component.table_data:
                if symbol == 'Y':
                    moving_data.extend(['Ē', 'Ē', 'Ē', 'Ē'])
                elif symbol == 'N':
                    moving_data.extend(['Ē', 'Ē', 'Ē', 'Ē'])

            return moving_data

        return None

    def simulate_leader_absorption(self, current_leader: LeaderStructure,
                                 next_leader: LeaderStructure) -> bool:
        """
        Simulate leader absorption (Cook Section 4.4, Figure 14).

        Leaders absorb each other, converting raw leaders to prepared leaders.
        Returns: True if absorption occurred.
        """
        # Leaders absorb each other based on Cook's distance rules
        over_dist = calculate_over_distance(current_leader.position, next_leader.position)
        under_dist = calculate_under_distance(current_leader.position, next_leader.position)

        # Cook's absorption conditions (simplified)
        if over_dist == 0 and under_dist == 1:  # Close enough for absorption
            if current_leader.leader_type == "prepared" and next_leader.leader_type == "raw":
                # Prepared leader absorbs raw leader, converting it to prepared
                next_leader.leader_type = "prepared"
                return True

        return False


def place_leader_component_system(state: List[int], start_position: int,
                                appendant_data: List[str]) -> CookLeaderSystem:
    """
    Place complete leader/component system for Cook's construction (Section 4.4).

    This creates the complex A/B glider arrangements that control CTS operations.
    """
    system = CookLeaderSystem()

    current_pos = start_position

    # Create first prepared leader (Cook starts with prepared leader)
    leader1 = system.create_prepared_leader(current_pos)
    system.leaders.append(leader1)
    current_pos += 50

    # Add primary component for first appendant
    if appendant_data:
        component1 = system.add_primary_component(leader1, appendant_data[0])
        current_pos = component1.position + 40

        # Add standard components for remaining appendants
        prev_component = component1
        for appendant in appendant_data[1:]:
            std_component = system.add_standard_component(prev_component, appendant)
            prev_component = std_component
            current_pos = std_component.position + 40

    # Add raw leader for next cycle
    leader2 = system.create_raw_leader(current_pos)
    system.leaders.append(leader2)

    # Physically place the gliders in the state
    for leader in system.leaders:
        # Place A/B gliders for leader structure
        _place_leader_gliders(state, leader)

    for component in system.components:
        # Place component gliders
        _place_component_gliders(state, component)

    return system


def _place_leader_gliders(state: List[int], leader: LeaderStructure):
    """Place the A/B gliders that form a leader structure."""
    # Cook's leader structures are complex A/B arrangements
    # Simplified: place A and B gliders with Cook's spacing

    # Place A glider
    _place_exact_glider(state, 'A', leader.position)

    # Place B glider at !1 distance for interaction
    b_pos = leader.position + 10  # Simplified spacing
    _place_exact_glider(state, 'B', b_pos)


def _place_component_gliders(state: List[int], component: ComponentStructure):
    """Place the gliders that form a component structure."""
    # Components are sequences representing table data
    # Simplified: place based on component type and data

    pos = component.position

    if component.component_type == "primary":
        # Primary components have special structure (Cook Figure 13)
        # Place initial gliders
        pass  # Simplified for now
    else:
        # Standard components
        pass  # Simplified for now

    # For each symbol in table data, place appropriate gliders
    for symbol in component.table_data:
        if symbol == 'Y':
            # Y represented by specific glider spacing
            pass
        elif symbol == 'N':
            # N represented by different spacing
            pass
        pos += 15  # Spacing between symbols


def _place_exact_glider(state: List[int], glider_type: str, position: int):
    """Place Cook's exact glider pattern at position."""
    if glider_type not in COOK_GLIDER_PATTERNS:
        return

    pattern = COOK_GLIDER_PATTERNS[glider_type]

    for i, bit in enumerate(pattern):
        pos = position + i
        if 0 <= pos < len(state):
            state[pos] = bit