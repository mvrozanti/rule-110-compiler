#!/usr/bin/env python3
"""
Web server for Rule 110 Brainfuck compilation.

Provides HTTP endpoints for compiling Brainfuck programs to Rule 110 initial states.
"""

from flask import Flask, request, jsonify, send_from_directory
import json
import os
from rule110_universal_compiler import compile_brainfuck_to_rule110
from rule110 import Rule110, DynamicRule110
from glider_tracker import track_gliders, GLIDER_PROPERTIES
from output_detection import analyze_computation_result

app = Flask(__name__, static_folder='.')

# Global compilation state for status polling
compilation_status = {
    'is_compiling': False,
    'start_time': None,
    'current_program': None,
    'progress': 0,
    'stage': 'idle',
    'estimated_time_remaining': None
}

# Cook's glider patterns for region identification
COOK_GLIDER_PATTERNS = {
    "A": [0, 0, 0, 1, 1, 1],
    "B": [0, 0, 0, 1, 0, 0, 0, 0],
    "C1": [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    "C2": [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0],
    "Ē": [1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1],
}
ETHER_PATTERN = [0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0]

def identify_glider_regions(state):
    """Identify regions in Rule 110 state containing different glider types."""
    regions = {}
    n = len(state)

    # Scan for glider patterns
    for i in range(n):
        for glider_type, pattern in COOK_GLIDER_PATTERNS.items():
            pattern_len = len(pattern)
            if i + pattern_len <= n:
                # Check if pattern matches
                if state[i:i+pattern_len] == pattern:
                    region_type = {
                        'C1': 'input-tape',
                        'C2': 'input-tape',
                        'A': 'computation',
                        'B': 'computation',
                        'Ē': 'gliders'
                    }.get(glider_type, 'unknown')

                    # Mark the region
                    for j in range(i, min(i + pattern_len, n)):
                        if j not in regions:
                            regions[j] = region_type

    # Mark ether background (regions not containing gliders)
    # Ether is the repeating background pattern
    ether_positions = set()
    for i in range(0, n - len(ETHER_PATTERN) + 1, len(ETHER_PATTERN)):
        if state[i:i+len(ETHER_PATTERN)] == ETHER_PATTERN:
            for j in range(i, i + len(ETHER_PATTERN)):
                ether_positions.add(j)

    # Any position not identified as a glider is likely ether
    for i in range(n):
        if i not in regions and i in ether_positions:
            regions[i] = 'ether'

    # ADDITIONAL: Identify input regions by looking for non-ether regions
    # In CTS encoding, input data creates non-ether patterns
    # Look for contiguous blocks that are not ether and mark as input-tape
    i = 0
    while i < n:
        if regions.get(i) == 'ether':
            i += 1
            continue

        # Found a non-ether region
        start = i
        while i < n and regions.get(i) != 'ether':
            i += 1
        end = i

        # If this block is reasonably sized, mark as input-tape
        if end - start >= 2 and end - start <= 25:  # Reasonable input data size
            # Check if any part is already classified as input-tape
            has_input = any(regions.get(j, '') == 'input-tape' for j in range(start, end))
            if not has_input:
                # Mark as input-tape
                for j in range(start, end):
                    regions[j] = 'input-tape'

    return regions

# Serve static files (HTML, JS, CSS)
@app.route('/')
def serve_demo():
    return send_from_directory('.', 'rule110_universality_demo.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

# Simple CORS handling (keeping for compatibility)
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Pre-compiled examples for faster loading
EXAMPLES = {
    'hello_world': '+[-->-[>>+>-----<<]<--<---]>-.>>>+.>>..+++[.]]<<<<.+++.------.<<-.>>>>+.',
    'add': '++>++[<+>-]<',
    'multiply': '++[>++++++<-]>',
    'echo': '+[,.]',
    'increment': '++>+',
    'loop_demo': '[+++]',
}

@app.route('/compile', methods=['POST', 'OPTIONS'])
def compile_program():
    """Compile Brainfuck program to Rule 110 initial state."""
    if request.method == 'OPTIONS':
        # Handle preflight request
        return '', 200

    try:
        data = request.get_json()
        program = data.get('program', '').strip()

        if not program:
            return jsonify({'error': 'No program provided'}), 400

        # Set compilation status
        import time
        compilation_status.update({
            'is_compiling': True,
            'start_time': time.time(),
            'current_program': program[:50] + ('...' if len(program) > 50 else ''),
            'progress': 0,
            'stage': 'initializing'
        })

        # Use pre-compiled if available
        if program in EXAMPLES.values():
            name = [k for k, v in EXAMPLES.items() if v == program][0]
            print(f"Using pre-compiled example: {name}")

        print(f"Compiling program: {program[:50]}...")
        compilation_status['stage'] = 'compiling_brainfuck'
        result = compile_brainfuck_to_rule110(program, tape_length=None)  # Auto-calculate tape length

        # Run Rule 110 evolution to see glider interactions
        print("Running Rule 110 evolution...")
        compilation_status['stage'] = 'running_evolution'
        # Use fixed-width evolution for clearer visualization
        # (DynamicRule110 grows the state, which can be confusing)
        ca = Rule110(result['rule110_initial'], boundary="ether")
        # Run evolution until stabilization or reasonable limit
        max_steps = 500  # Much higher limit
        stabilization_window = 20  # Steps of no change to consider stable

        initial_state = result['rule110_initial']
        history = [initial_state]
        stable_count = 0

        for step in range(max_steps):
            ca.step()
            current_state = ca.get_state()
            history.append(current_state)

            # Update progress with detailed information
            progress = 10 + int((step + 1) / max_steps * 70)
            compilation_status['progress'] = min(80, progress)
            compilation_status['current_step'] = step + 1
            compilation_status['total_steps'] = max_steps
            compilation_status['cells_processed'] = len(current_state)

            # Check if state changed from previous
            changed = any(a != b for a, b in zip(history[-2], current_state))

            if not changed:
                stable_count += 1
                if stable_count >= stabilization_window:
                    print(f"Evolution stabilized after {step + 1} steps")
                    break
            else:
                stable_count = 0

        if stable_count < stabilization_window:
            print(f"Evolution still changing after {max_steps} steps (ran to limit)")
            # Keep only last 100 steps to avoid memory issues
            if len(history) > 100:
                history = history[-100:]
        history = ca.get_history()

        # Track gliders and detect collisions
        print("Tracking gliders and collisions...")
        compilation_status['stage'] = 'tracking_gliders'
        compilation_status['progress'] = 85
        compilation_status['history_steps'] = len(history)

        # Glider tracking is computationally intensive - provide detailed progress
        import time
        tracking_start = time.time()

        print(f"Starting glider tracking on {len(history)} steps...")

        # Glider tracking is computationally intensive
        # We'll show detailed progress through callback system
        def glider_progress_callback(current_step, total_steps, phase, details):
            """Callback to update detailed glider tracking progress"""
            compilation_status['current_step'] = current_step
            compilation_status['total_steps'] = total_steps
            compilation_status['tracking_phase'] = phase
            compilation_status['tracking_details'] = details

            # Update overall progress based on phase
            if phase == 'initializing':
                compilation_status['progress'] = 86
            elif phase == 'scanning_patterns':
                # Progress through scanning phase (86-90%)
                progress = 86 + int((current_step / total_steps) * 4)
                compilation_status['progress'] = min(90, progress)
            elif phase == 'processing_step':
                # Progress through step processing (86-94%)
                progress = 86 + int((current_step / total_steps) * 8)
                compilation_status['progress'] = min(94, progress)
            elif phase == 'complete':
                compilation_status['progress'] = 95
                compilation_status['gliders_found'] = details.get('final_gliders', 0)
                compilation_status['collisions_found'] = details.get('final_collisions', 0)

        try:
            glider_track = track_gliders(history, glider_progress_callback)
            tracking_time = time.time() - tracking_start

            compilation_status['progress'] = 95
            compilation_status['gliders_found'] = len(glider_track.gliders) if hasattr(glider_track, 'gliders') else 0
            compilation_status['collisions_found'] = len(glider_track.collisions) if hasattr(glider_track, 'collisions') else 0
            print(f"Glider tracking completed in {tracking_time:.1f}s: {compilation_status['gliders_found']} gliders, {compilation_status['collisions_found']} collisions")

        except Exception as e:
            tracking_time = time.time() - tracking_start
            print(f"Glider tracking failed after {tracking_time:.1f}s: {e}")
            # Allow compilation to continue with minimal results
            compilation_status['progress'] = 95
            compilation_status['gliders_found'] = 0
            compilation_status['collisions_found'] = 0
            glider_track = type('GliderTrack', (), {'gliders': [], 'collisions': []})()

        # Identify regions for universal computation
        compilation_status['stage'] = 'analyzing_regions'
        compilation_status['progress'] = 95
        compilation_status['tape_length'] = len(result['rule110_initial'])
        # For universal computation, regions are not glider patterns but encoded data
        initial_state = result['rule110_initial']
        tape_length = len(initial_state)

        # Find data regions (contiguous non-zero cells)
        data_regions = []
        i = 0
        while i < tape_length:
            if initial_state[i] != 0:  # Found data
                start = i
                while i < tape_length and initial_state[i] != 0:
                    i += 1
                end = i
                if end - start >= 2:  # Substantial data blocks only
                    data_regions.append({'start': start, 'end': end})
            else:
                i += 1

        # Set up regions for universal computation
        region_ranges_for_detection = {}

        if data_regions:
            # Leftmost data region = input
            region_ranges_for_detection['input-tape'] = [data_regions[0]]

            # Rightmost area = output
            output_start = int(tape_length * 0.6)
            region_ranges_for_detection['output-tape'] = [{
                'start': output_start,
                'end': tape_length,
                'steps': list(range(max(0, len(history) - 10), len(history)))  # Last 10 steps
            }]
        else:
            # Fallback heuristics
            region_ranges_for_detection['input-tape'] = [{
                'start': 0,
                'end': int(tape_length * 0.25)
            }]
            region_ranges_for_detection['output-tape'] = [{
                'start': int(tape_length * 0.6),
                'end': tape_length,
                'steps': list(range(max(0, len(history) - 10), len(history)))
            }]

        # REAL OUTPUT DETECTION: Analyze where computation results actually appear
        print("Detecting output region...")
        
        # Get expected result from verification if available
        expected_result = None
        try:
            tm_output = result['verification'].get('tm_output', '')
            if tm_output:
                # Try to parse as number (simplified)
                expected_result = len(tm_output)  # Temporary - needs proper parsing
        except:
            pass
        
        # Analyze computation result
        computation_analysis = analyze_computation_result(
            history,
            glider_track.gliders,
            region_ranges_for_detection,
            expected_result
        )
        
        output_regions = {}
        if computation_analysis.get('output_region'):
            output_region_info = computation_analysis['output_region']
            output_regions['output-tape'] = [{
                'start': output_region_info['start'],
                'end': output_region_info['end'],
                'steps': list(range(max(0, len(history) - 10), len(history))),  # Last 10 steps
                'detection_method': output_region_info.get('detection_method', 'unknown'),
                'confidence': output_region_info.get('confidence', 'unknown')
            }]

        # Use the already-converted region_ranges_for_detection, add steps info
        region_ranges = {}
        for region_type, ranges in region_ranges_for_detection.items():
            region_ranges[region_type] = [
                {**r, 'steps': [0]}  # Add steps info for initial state
                for r in ranges
            ]
        
        # Merge output regions
        for region_type, ranges in output_regions.items():
            if region_type not in region_ranges:
                region_ranges[region_type] = []
            region_ranges[region_type].extend(ranges)

        # Format collisions for frontend
        collisions = []
        for step, pos, desc in glider_track.collisions:
            collisions.append({
                'step': step,
                'position': pos,
                'description': desc
            })

        # Format glider tracks for visualization
        glider_tracks = []
        for glider in glider_track.gliders:
            glider_tracks.append({
                'type': glider.glider_type,
                'start_step': glider.step_first_seen,
                'end_step': glider.step_last_seen,
                'start_pos': int(glider.position),
                'velocity': GLIDER_PROPERTIES.get(glider.glider_type, {}).get('velocity', 0)
            })

        # Final progress update
        compilation_status['progress'] = 100
        compilation_status['stage'] = 'complete'

        elapsed = time.time() - compilation_status.get('start_time', time.time())
        print(f"Compilation completed in {elapsed:.1f} seconds")

        return jsonify({
            'program': program,
            'rule110_initial': result['rule110_initial'],
            'history': history,  # Full evolution history
            'collisions': collisions,
            'glider_tracks': glider_tracks,
            'metadata': {
                'tm_states': len(result['turing_machine']['states']),
                'cts_appendants': len(result['cts']['appendants']),
                'rule110_cells': len(result['rule110_initial']),
                'evolution_steps': len(history),
                'collisions_detected': len(collisions),
                'gliders_tracked': len(glider_tracks)
            },
            'regions': region_ranges,
            'verification': result.get('verification', {}),  # Include verification data
            'computation_analysis': computation_analysis,  # Include output detection and decoding
            'success': True
        })

        # Reset compilation status on success
        compilation_status.update({
            'is_compiling': False,
            'start_time': None,
            'current_program': None,
            'progress': 100,
            'stage': 'completed'
        })

    except Exception as e:
        print(f"Compilation error: {e}")
        # Reset compilation status on error
        compilation_status.update({
            'is_compiling': False,
            'start_time': None,
            'current_program': None,
            'progress': 0,
            'stage': 'error'
        })
        return jsonify({'error': str(e)}), 500

@app.route('/examples', methods=['GET'])
def get_examples():
    """Get list of available pre-compiled examples."""
    return jsonify({
        'examples': [
            {'name': 'Hello World', 'key': 'hello_world', 'program': EXAMPLES['hello_world']},
            {'name': 'Add Numbers', 'key': 'add', 'program': EXAMPLES['add']},
            {'name': 'Multiply', 'key': 'multiply', 'program': EXAMPLES['multiply']},
            {'name': 'Echo Input', 'key': 'echo', 'program': EXAMPLES['echo']},
            {'name': 'Increment', 'key': 'increment', 'program': EXAMPLES['increment']},
            {'name': 'Infinite Loop', 'key': 'loop_demo', 'program': EXAMPLES['loop_demo']},
        ]
    })

@app.route('/status', methods=['GET'])
def get_compilation_status():
    """Get current compilation status."""
    import time

    status = compilation_status.copy()

    if status['is_compiling'] and status['start_time']:
        elapsed = time.time() - status['start_time']
        status['elapsed_seconds'] = round(elapsed, 1)

        # Only provide time estimates for very long-running phases to avoid confusion
        # Focus on actual progress metrics instead
        if elapsed > 30 and status.get('stage') in ['tracking_gliders']:
            # Only show time for glider tracking if it's taking really long
            estimated_total = max(120, elapsed + 20)
            remaining = max(10, estimated_total - elapsed)
            status['estimated_time_remaining'] = round(remaining, 1)

    return jsonify(status)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    print("Starting Rule 110 Brainfuck Compiler Server...")
    print("Available endpoints:")
    print("  POST /compile - Compile Brainfuck program")
    print("  GET /status - Get compilation status (for polling)")
    print("  GET /examples - Get pre-compiled examples")
    print("  GET /health - Health check")
    print()
    app.run(host='0.0.0.0', port=5000, debug=True)
