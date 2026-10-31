import sys
import runpy
from pathlib import Path
from transformations.json_to_dsl import json_to_dsl
from transformations.t1 import t1
from transformations.t2 import t2
from besser.generators.json import JSONObjectGenerator
from besser.generators.qiskit import QiskitGenerator

def print_board(solution: list[tuple[int, int]], board_size: int, fixed_queens: list[tuple[int, int]] | set[tuple[int, int]] = ()):
    """Visually renders the board in the terminal."""
    grid = [["." for _ in range(board_size)] for _ in range(board_size)]
    fixed_set = set(fixed_queens)
    for r, c in solution:
        if (r, c) in fixed_set:
            grid[c - 1][r - 1] = "\033[0;32mQ\033[0m"  # Fixed Queen (green)
        else:
            grid[c - 1][r - 1] = "Q"                  # Calculated Queen
    
    border = "+" + "---+" * board_size
    print(border)
    for row in grid:
        print("| " + " | ".join(row) + " |")
        print(border)

def is_valid_solution(sol: list[tuple[int, int]]) -> bool:
    if len(sol) <= 1:
        return True
    p1 = sol[0]
    if any(p2 for p2 in sol[1:] if p1[0] == p2[0] or p1[1] == p2[1] or abs(p1[0]-p2[0]) == abs(p1[1]-p2[1])):
        return False
    return is_valid_solution(sol[1:])

def main():
    filename = list(filter(lambda x: '--' not in x, sys.argv[1:]))
    if len(filename) != 1:
        print(f"Usage: {sys.argv[0]} <file-path> [...flags]")
        print("  |- <file-path>: Path to the simplified problem (JSON)")
        print("  |- --debug-t1, --debug-t2, --debug-qiskit, --debug-all: Print debug information")
        print("  |- --t1: Stop after T1, save results in output/CNF.json")
        sys.exit(1)
    else:
        filename = filename[0]
        with open(filename, "r") as f:
            data = f.read()

    if any(x == "--debug-all" for x in sys.argv):
        debug_t1 = debug_t2 = debug_qiskit = True
    else:
        debug_t1 = any(x == "--debug-t1" for x in sys.argv)
        debug_t2 = any(x == "--debug-t2" for x in sys.argv)
        debug_qiskit = any(x == "--debug-qiskit" for x in sys.argv)

    # Load problem from simplified JSON
    print("\033[0;33mJSON -> Problem...\033[0m")
    (problem, fixed_queens, board_size) = json_to_dsl(data)

    # Transform problem into CNF
    print("\033[0;33mT1: Problem -> CNF...\033[0m")
    cnf = t1(problem, debug=debug_t1)

    # Persist intermediate CNF model
    JSONObjectGenerator(
        model=cnf,
        output_dir="output/",
    ).generate()

    if any(x == "--t1" for x in sys.argv):
        sys.exit(0)

    # Transform CNF into quantum model
    print("\033[0;33mT2: CNF -> Quantum Circuit...\033[0m")
    (quantum_model, qubit_mapping) = t2(cnf, debug=debug_t2)

    # Translate quantum model to Qiskit
    print("\033[0;33mT3: Quantum Circuit -> Qiskit...\033[0m")
    QiskitGenerator(quantum_model, output_dir="output", shots=1024).generate()

    # Qiskit script run directly
    print("\033[0;33mRunning output/qiskit_circuit.py...\033[0m")
    counts: dict[str, int] = runpy.run_path("output/qiskit_circuit.py")["counts"]

    # Prune counts lesser than 10% of max frequency
    most_frequent = max(counts.values()) if counts else 0
    solution_bitstrings = {s for (s, count) in counts.items() if count > most_frequent * 0.1}

    solutions: list[list[tuple[int, int]]] = []
    for bitstring in solution_bitstrings:
        solution = list(fixed_queens)
        for (bit, pos) in zip(reversed(bitstring), qubit_mapping):
            if bit == '1':
                solution.append(pos)

        # ignore non-sensical solutions
        if len(solution) == board_size:
            solutions.append(solution)

    print("\n" + "="*40)
    if solutions and is_valid_solution(solutions[0]):
        solutions = [sorted(sol, key=lambda x: x[0]) for sol in solutions]
        print(f"\033[0;32mFound {len(solutions)} valid solution(s):\033[0m")
        for i, sol in enumerate(solutions, 1):
            print(f"\Solution #{i}: {sol}")
            print_board(sol, board_size, fixed_queens)
    else:
        print("\033[0;31mNo valid solutions found.")
    print("="*40 + "\033[0m", flush=True)

if __name__ == "__main__":
    main()