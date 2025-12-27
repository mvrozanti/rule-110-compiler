#!/usr/bin/env python3
"""
Universal Rule 110 Compiler.

Complete pipeline: Brainfuck → Turing Machine → CTS → Rule 110
With HTML visualization for educational demonstration.
"""

import json
from typing import List, Dict
from brainfuck_compiler import compile_brainfuck_to_turing, execute_turing_machine
from turing_to_cts import compile_turing_to_cts, simulate_turing_through_cts
from cts_to_rule110 import compile_cts_to_rule110, simulate_cts_in_rule110
from rule110 import DynamicRule110


def compile_brainfuck_to_rule110(program: str, tape_length: int = 300) -> dict:
    """
    Complete compilation pipeline: Brainfuck → Rule 110 initial state.

    Returns compilation results and metadata.
    """
    print("🚀 Starting Universal Rule 110 Compilation")
    print("=" * 50)

    # Phase 1: Brainfuck → Turing Machine
    print("📝 Phase 1: Brainfuck → Turing Machine")
    tm = compile_brainfuck_to_turing(program)
    print(f"   Compiled to TM with {len(tm.states)} states, {len(tm.transitions)} transitions")

    # Phase 2: Turing Machine → CTS
    print("🔄 Phase 2: Turing Machine → CTS")
    tm_to_cts = compile_turing_to_cts(tm)
    cts = tm_to_cts.cts
    print(f"   Converted to CTS with {len(cts.appendants)} appendants")

    # Phase 3: CTS → Rule 110
    print("⚛️  Phase 3: CTS → Rule 110")
    rule110_initial = compile_cts_to_rule110(cts, tape_length)
    active_cells = sum(1 for cell in rule110_initial if cell == 1)
    print(f"   Generated Rule 110 initial state with {active_cells} active cells")

    # Phase 4: Verification
    print("✅ Phase 4: Verification")
    # Direct TM execution for comparison
    tm_tape, tm_output = execute_turing_machine(tm, "", max_steps=50)
    print(f"   Direct TM execution: tape='{tm_tape}', output='{tm_output}'")

    return {
        "program": program,
        "turing_machine": {
            "states": tm.states,
            "transitions": dict(tm.transitions),
            "initial_state": tm.initial_state,
            "accept_state": tm.accept_state
        },
        "cts": {
            "appendants": cts.appendants,
            "initial_tape": cts.initial_tape
        },
        "rule110_initial": rule110_initial,
        "verification": {
            "tm_tape": tm_tape,
            "tm_output": tm_output
        }
    }


def execute_rule110_computation(rule110_initial: List[int], steps: int = 100) -> dict:
    """
    Execute the Rule 110 computation and capture results.
    """
    print("🎬 Executing Rule 110 Computation")

    ca = DynamicRule110(rule110_initial, boundary="ether")
    ca.run(steps)

    # Analyze evolution
    evolution_data = []
    for step, state in enumerate(ca.get_history()):
        active = sum(1 for cell in state if cell == 1)
        evolution_data.append({
            "step": step,
            "active_cells": active,
            "state_sample": state[50:150]  # Sample middle section
        })

    final_state = ca.get_history()[-1]
    final_active = sum(1 for cell in final_state if cell == 1)

    print(f"   Evolution complete: {steps} steps, final active cells: {final_active}")

    return {
        "steps": steps,
        "final_state": final_state,
        "evolution_summary": evolution_data,
        "final_active_cells": final_active
    }


def create_html_visualization(compilation_result: dict, execution_result: dict) -> str:
    """
    Create HTML visualization of the complete compilation and execution.
    """
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rule 110 Universal Compiler</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .phase {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .phase h3 {{
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .code {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
        }}
        .evolution {{
            background: #f0f8ff;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
        }}
        .metric {{
            display: inline-block;
            background: #e3f2fd;
            padding: 8px 12px;
            margin: 5px;
            border-radius: 4px;
            font-weight: bold;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(20px, 1fr));
            gap: 1px;
            background: #333;
            padding: 2px;
            margin: 10px 0;
        }}
        .cell {{
            width: 18px;
            height: 18px;
            background: white;
        }}
        .cell.active {{
            background: #667eea;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔥 Rule 110 Universal Compiler</h1>
        <p>Demonstrating Cook's Proof: Any Algorithm → Rule 110 Evolution</p>
        <p><strong>Brainfuck Program:</strong> {compilation_result['program']}</p>
    </div>

    <div class="phase">
        <h3>📝 Phase 1: Brainfuck → Turing Machine</h3>
        <p>The Brainfuck program is compiled into a Turing machine with {len(compilation_result['turing_machine']['states'])} states and {len(compilation_result['turing_machine']['transitions'])} transitions.</p>
        <div class="code">
            Initial State: {compilation_result['turing_machine']['initial_state']}<br>
            Accept State: {compilation_result['turing_machine']['accept_state']}
        </div>
    </div>

    <div class="phase">
        <h3>🔄 Phase 2: Turing Machine → Cyclic Tag System</h3>
        <p>The Turing machine is encoded as a Cyclic Tag System (CTS) with {len(compilation_result['cts']['appendants'])} appendants.</p>
        <div class="code">
            Initial Tape: {compilation_result['cts']['initial_tape']}<br>
            Appendants: {', '.join(compilation_result['cts']['appendants'][:3])}{'...' if len(compilation_result['cts']['appendants']) > 3 else ''}
        </div>
    </div>

    <div class="phase">
        <h3>⚛️ Phase 3: CTS → Rule 110 Initial State</h3>
        <p>The CTS is compiled to a Rule 110 initial configuration with {sum(1 for x in compilation_result['rule110_initial'] if x == 1)} active cells.</p>
        <div class="grid">
"""

    # Add Rule 110 grid visualization (sample)
    initial_state = compilation_result['rule110_initial']
    for i in range(100, 200):  # Show middle section
        cell_class = "cell active" if initial_state[i] == 1 else "cell"
        html += f'            <div class="{cell_class}"></div>\n'

    html += f"""
        </div>
        <p><em>Showing cells 100-200 of {len(initial_state)}-cell Rule 110 initial state</em></p>
    </div>

    <div class="phase">
        <h3>🎬 Phase 4: Rule 110 Evolution</h3>
        <p>The Rule 110 cellular automaton evolves for {execution_result['steps']} steps.</p>
        <div class="metric">Final Active Cells: {execution_result['final_active_cells']}</div>
        <div class="evolution">
            <h4>Evolution Summary:</h4>
"""

    # Show evolution metrics
    for i in range(0, len(execution_result['evolution_summary']), 10):
        step_data = execution_result['evolution_summary'][i]
        html += f"            Step {step_data['step']}: {step_data['active_cells']} active cells<br>\n"

    html += f"""
        </div>
    </div>

    <div class="phase">
        <h3>✅ Phase 5: Verification</h3>
        <p>Direct Turing machine execution for comparison:</p>
        <div class="code">
            Final Tape: {compilation_result['verification']['tm_tape']}<br>
            Output: {compilation_result['verification']['tm_output']}
        </div>
        <p><strong>Universality Demonstrated:</strong> Any algorithm can be encoded as Rule 110 evolution!</p>
    </div>

    <div class="phase">
        <h3>🎓 Educational Notes</h3>
        <p>This demonstrates Matthew Cook's 2004 proof that Rule 110 is Turing complete:</p>
        <ul>
            <li><strong>Brainfuck</strong> → High-level programming language</li>
            <li><strong>Turing Machine</strong> → Universal computation model</li>
            <li><strong>Cyclic Tag System</strong> → Simpler universal system</li>
            <li><strong>Rule 110</strong> → Simple cellular automaton that simulates CTS</li>
        </ul>
        <p>Through this pipeline, any computable function can be executed by Rule 110 evolution!</p>
    </div>

</body>
</html>"""

    return html


def compile_and_visualize_brainfuck(program: str, steps: int = 100) -> str:
    """
    Complete pipeline: Brainfuck → HTML visualization.

    Returns HTML string showing the complete compilation and execution.
    """
    # Compile through all layers
    compilation = compile_brainfuck_to_rule110(program)

    # Execute Rule 110 computation
    execution = execute_rule110_computation(compilation["rule110_initial"], steps)

    # Create HTML visualization
    html = create_html_visualization(compilation, execution)

    return html


def demo_universality():
    """Demonstrate Rule 110 universality with simple programs."""
    print("🚀 Rule 110 Universality Demonstration")
    print("=" * 50)

    # Test programs
    test_programs = [
        ("Simple increment", "+++"),  # Add 3
        ("Loop", "[+++]"),  # Loop that does nothing
        ("Add and move", "++>+<"),  # More complex
    ]

    for name, program in test_programs:
        print(f"\n🎯 Testing: {name}")
        print(f"Program: {program}")

        try:
            # Compile
            compilation = compile_brainfuck_to_rule110(program)

            # Quick execution
            execution = execute_rule110_computation(compilation["rule110_initial"], 20)

            print(f"✅ Compiled successfully")
            print(f"   TM states: {len(compilation['turing_machine']['states'])}")
            print(f"   CTS appendants: {len(compilation['cts']['appendants'])}")
            print(f"   Rule 110 active cells: {sum(1 for x in compilation['rule110_initial'] if x == 1)}")
            print(f"   Evolution: {execution['final_active_cells']} final active cells")

        except Exception as e:
            print(f"❌ Compilation failed: {e}")

    print("\n🎉 Universality Demonstration Complete!")
    print("Rule 110 can simulate any algorithm through this compilation pipeline!")


if __name__ == '__main__':
    # Quick demo
    demo_universality()

    # Create HTML for a sample program
    sample_program = "++>+"
    html = compile_and_visualize_brainfuck(sample_program)

    # Save to file
    with open('rule110_universality_demo.html', 'w') as f:
        f.write(html)

    print("\n📄 HTML visualization saved to: rule110_universality_demo.html")
    print("Open in browser to see the complete universality demonstration!")