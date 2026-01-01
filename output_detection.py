#!/usr/bin/env python3
"""
Output detection and decoding for Rule 110 computations.

Detects where computation results appear in the final Rule 110 state
and attempts to decode glider patterns back to numeric results.
"""

from typing import List, Tuple, Optional, Dict
from glider_tracker import GLIDER_PROPERTIES


def detect_output_region(
    history: List[List[int]], 
    gliders: List,  # List of Glider objects
    initial_regions: Dict[str, List]
) -> Optional[Dict]:
    """
    Detect where computation output actually appears in the final state.
    
    Strategy:
    1. Analyze where gliders end up (final positions)
    2. Look for regions with stable glider patterns in final steps
    3. Identify areas where computation gliders (A/B) interact and produce results
    
    Args:
        history: Full evolution history
        glider_tracks: Tracked glider information
        initial_regions: Regions identified in initial state
        
    Returns:
        Dict with output region info, or None if not detected
    """
    if not history or len(history) < 10:
        return None
    
    final_state = history[-1]
    tape_length = len(final_state)

    # Strategy 1: If we have input regions, output is typically to the right
    # (Check this first for better accuracy)
    if 'input-tape' in initial_regions and initial_regions['input-tape']:
        input_end = max(r['end'] for r in initial_regions['input-tape'])
        # Output region starts after input + some margin
        output_start = min(tape_length - 20, input_end + 20)
        output_end = tape_length

        return {
            'start': output_start,
            'end': output_end,
            'detection_method': 'input_region_heuristic',
            'confidence': 'medium'
        }

    # Strategy 2: Look for gliders that end up in final positions
    # Output regions often have C-gliders (stationary data) in final state
    final_glider_positions = {}

    for glider in gliders:
        # Check if glider is present near the end
        if hasattr(glider, 'step_last_seen'):
            end_step = glider.step_last_seen
        else:
            end_step = getattr(glider, 'end_step', len(history) - 1)

        if end_step >= len(history) - 5:  # Gliders present near end
            # Get glider position and velocity
            if hasattr(glider, 'position'):
                start_pos = glider.position
            else:
                start_pos = getattr(glider, 'start_pos', 0)

            if hasattr(glider, 'glider_type'):
                glider_type = glider.glider_type
                velocity = GLIDER_PROPERTIES.get(glider_type, {}).get('velocity', 0)
            else:
                glider_type = getattr(glider, 'type', 'unknown')
                velocity = getattr(glider, 'velocity', 0)

            if hasattr(glider, 'step_first_seen'):
                start_step = glider.step_first_seen
            else:
                start_step = getattr(glider, 'start_step', 0)

            # Calculate final position
            final_pos = int(start_pos + velocity * (len(history) - 1 - start_step))
            if 0 <= final_pos < tape_length:
                if final_pos not in final_glider_positions:
                    final_glider_positions[final_pos] = []
                final_glider_positions[final_pos].append(glider_type)

    # Find regions with C-gliders in final state (stationary = likely output)
    c_glider_positions = [
        pos for pos, types in final_glider_positions.items()
        if any(t in ['C1', 'C2'] for t in types)
    ]

    if c_glider_positions:
        output_start = min(c_glider_positions)
        output_end = max(c_glider_positions) + 1

        # Expand to include nearby gliders
        output_start = max(0, output_start - 10)
        output_end = min(tape_length, output_end + 10)

        return {
            'start': output_start,
            'end': output_end,
            'detection_method': 'final_c_gliders',
            'confidence': 'medium'
        }

    # Strategy 3: Look for regions with high activity that stabilize
    # Compare last few steps to find stable regions
    if len(history) >= 10:
        stable_regions = find_stable_regions(history[-10:])
        if stable_regions:
            return {
                'start': stable_regions[0],
                'end': stable_regions[1],
                'detection_method': 'stability',
                'confidence': 'low'
            }

    # Strategy 4: Fallback - use rightmost portion
    output_start = int(tape_length * 0.7)  # Rightmost 30%
    output_end = tape_length

    return {
        'start': output_start,
        'end': output_end,
        'detection_method': 'fallback_rightmost',
        'confidence': 'low'
    }


def find_stable_regions(last_states: List[List[int]], threshold: float = 0.9) -> Optional[Tuple[int, int]]:
    """
    Find regions that are stable (don't change much) across last states.
    
    Args:
        last_states: Last N states of evolution
        threshold: Fraction of states that must match for stability
        
    Returns:
        (start, end) of stable region, or None
    """
    if len(last_states) < 2:
        return None
    
    tape_length = len(last_states[0])
    stable_positions = []
    
    for pos in range(tape_length):
        # Check if this position is stable across states
        matching = sum(1 for i in range(len(last_states) - 1) 
                      if last_states[i][pos] == last_states[i+1][pos])
        stability = matching / (len(last_states) - 1)
        
        if stability >= threshold:
            stable_positions.append(pos)
    
    if len(stable_positions) >= 20:  # Need substantial stable region
        return (min(stable_positions), max(stable_positions) + 1)
    
    return None


def decode_output_pattern(
    output_region: List[int],
    expected_result: Optional[int] = None
) -> Optional[Dict]:
    """
    Attempt to decode output region pattern to numeric result.
    
    This is a simplified decoder - full Cook decoding is more complex.
    
    Args:
        output_region: Binary pattern from output region
        expected_result: Expected numeric result (for verification)
        
    Returns:
        Dict with decoded result info, or None if decoding fails
    """
    if not output_region:
        return None
    
    # Strategy 1: Count C-glider patterns (C-gliders represent data)
    # Each C1 glider pattern is roughly 12 cells, C2 is 17 cells
    # But this is simplified - real decoding needs glider type detection
    
    # Strategy 2: Look for binary encoding
    # Try to interpret significant portion as binary number
    active_positions = [i for i, bit in enumerate(output_region) if bit == 1]
    
    if not active_positions:
        return None
    
    # Get significant portion (remove leading/trailing zeros)
    start = active_positions[0]
    end = active_positions[-1] + 1
    significant = output_region[start:end]
    
    # Try interpreting as binary
    binary_str = ''.join(str(bit) for bit in significant)
    try:
        decoded_value = int(binary_str, 2)
        
        result = {
            'decoded_value': decoded_value,
            'binary_representation': binary_str,
            'method': 'binary_interpretation',
            'confidence': 'low'
        }
        
        # If we have expected result, check if it matches
        if expected_result is not None:
            result['matches_expected'] = (decoded_value == expected_result)
            result['expected'] = expected_result
        
        return result
    except ValueError:
        pass
    
    # Strategy 3: Count active cells as unary encoding
    active_count = sum(output_region)
    result = {
        'decoded_value': active_count,
        'method': 'unary_count',
        'confidence': 'very_low',
        'note': 'Simplified unary encoding (count of active cells)'
    }
    
    if expected_result is not None:
        result['matches_expected'] = (active_count == expected_result)
        result['expected'] = expected_result
    
    return result


def analyze_computation_result(
    history: List[List[int]],
    gliders: List,  # List of Glider objects
    initial_regions: Dict,
    expected_result: Optional[int] = None
) -> Dict:
    """
    Complete analysis: detect output region and decode result.
    
    Returns comprehensive analysis of where output is and what it represents.
    """
    # Detect output region
    output_region_info = detect_output_region(history, gliders, initial_regions)
    
    result = {
        'output_region': output_region_info,
        'decoded_result': None
    }
    
    if output_region_info:
        final_state = history[-1]
        start = output_region_info['start']
        end = output_region_info['end']
        output_pattern = final_state[start:end]
        
        # Try to decode
        decoded = decode_output_pattern(output_pattern, expected_result)
        result['decoded_result'] = decoded
    
    return result

