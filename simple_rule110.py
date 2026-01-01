#!/usr/bin/env python3
"""
Simple Rule 110 demonstration.

Shows basic Rule 110 evolution with clear visualization.
"""

from rule110 import Rule110
import time
import os


def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')


def print_state(state, step):
    """Print the current state with step number."""
    print(f"\nStep {step}:")
    print("".join("█" if cell else " " for cell in state))
    print(f"Active cells: {sum(state)}")


def demo_single_cell():
    """Demonstrate single cell evolution."""
    print("🚀 Rule 110: Single Cell Evolution")
    print("===================================")

    # Create initial state with single 1 in the middle
    initial = [0] * 50 + [1] + [0] * 49
    ca = Rule110(initial)

    print_state(ca.get_state(), 0)

    for step in range(20):
        time.sleep(0.1)
        ca.step()
        print_state(ca.get_state(), step + 1)


def demo_glider():
    """Demonstrate glider pattern."""
    print("🚀 Rule 110: Glider Pattern")
    print("===========================")

    # Known glider pattern from Cook
    glider = [0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1]
    ca = Rule110(glider)

    print_state(ca.get_state(), 0)

    for step in range(15):
        time.sleep(0.2)
        ca.step()
        print_state(ca.get_state(), step + 1)


def demo_interactive():
    """Interactive demo with user input."""
    print("🚀 Rule 110 Interactive Demo")
    print("============================")
    print("Enter a binary string (e.g., '010' or '101010'):")

    while True:
        try:
            user_input = input("> ").strip()
            if not user_input:
                break

            # Convert string to list of ints
            initial_state = [int(c) for c in user_input if c in '01']
            if not initial_state:
                print("Please enter a string with 0s and 1s only.")
                continue

            ca = Rule110(initial_state)

            print(f"\nStarting with: {user_input}")
            print_state(ca.get_state(), 0)

            steps = int(input("How many steps to run? ") or "10")

            for step in range(steps):
                input(f"Press Enter for step {step + 1}...")
                ca.step()
                print_state(ca.get_state(), step + 1)

            again = input("\nTry another pattern? (y/n): ").lower()
            if again != 'y':
                break

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            continue


def main():
    """Main demo menu."""
    while True:
        clear_screen()
        print("🎯 Rule 110 Cellular Automaton Demo")
        print("===================================")
        print("1. Single cell evolution")
        print("2. Glider pattern")
        print("3. Interactive mode")
        print("4. Run unit tests")
        print("q. Quit")

        choice = input("\nChoose demo (1-4,q): ").strip().lower()

        if choice == '1':
            clear_screen()
            demo_single_cell()
            input("\nPress Enter to continue...")

        elif choice == '2':
            clear_screen()
            demo_glider()
            input("\nPress Enter to continue...")

        elif choice == '3':
            clear_screen()
            demo_interactive()

        elif choice == '4':
            clear_screen()
            print("Running unit tests...")
            os.system("python3 test_rule110_visualization.py")

        elif choice in ('q', 'quit'):
            break

        else:
            print("Invalid choice. Press Enter to try again...")
            input()


if __name__ == '__main__':
    main()





