import sys
import runpy
from pathlib import Path
from transformations.json_to_dsl import json_to_dsl, solution_to_dsl
from transformations.t1 import t1
from transformations.t2 import t2
from besser.generators.json import JSONObjectGenerator
from besser.generators.qiskit import QiskitGenerator
from baseline import solve_nqueens, quantum_metrics, format_metrics
from solver_config import load_solver_config

MAX_QUBITS = 22


def print_board(solution: list[tuple[int, int]], board_size: int, fixed_queens: list[tuple[int, int]] | set[tuple[int, int]] = ()):
    """Visually renders the board in the terminal (rows top to bottom, columns left to right)."""
    grid = [["." for _ in range(board_size)] for _ in range(board_size)]
    fixed_set = set(fixed_queens)
    for r, c in solution:
        if (r, c) in fixed_set:
            grid[r - 1][c - 1] = "\033[0;32mQ\033[0m"  # Fixed Queen (green)
        else:
            grid[r - 1][c - 1] = "Q"                  # Calculated Queen

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
        print("  |- --config=<file>: Solver settings (JSON: rounds, shots, group_size), default config/config.json")
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

    # Solver settings (rounds, shots, group size), checked against ocl/solver_config.ocl
    config_flag = [x for x in sys.argv if x.startswith("--config=")]
    config = load_solver_config(config_flag[0].split("=", 1)[1] if config_flag else "config/config.json")

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

    # Classical baseline: number of solutions M, which sets the number of Grover rounds
    baseline_solutions = solve_nqueens(board_size, fixed_queens)

    # Transform CNF into quantum model
    print("\033[0;33mT2: CNF -> Quantum Circuit...\033[0m")
    (quantum_model, qubit_mapping) = t2(cnf, group_size=config.group_size or None, iterations=config.rounds or None, solutions=len(baseline_solutions), debug=debug_t2)

    # Circuits that exceed the limit of qubits cannot be simulated: stop before generating/running the circuit
    if quantum_model.num_qubits > MAX_QUBITS:
        print(f"\n\033[0;31mError: Circuit requires {quantum_model.num_qubits} qubits (simulation limit is {MAX_QUBITS}).\033[0m")
        sys.exit(0)

    # Translate quantum model to Qiskit
    print("\033[0;33mT3: Quantum Circuit -> Qiskit...\033[0m")
    QiskitGenerator(quantum_model, output_dir="output", shots=config.shots).generate()

    if not debug_qiskit:
        qiskit_script = Path("output/qiskit_circuit.py")
        lines = qiskit_script.read_text().splitlines()
        lines = [
            line for line in lines
            if "print(qc.draw())" not in line
            and 'print("Counts:", counts)' not in line
        ]
        qiskit_script.write_text("\n".join(lines) + "\n")

    # Qiskit script run directly
    print("\033[0;33mRunning output/qiskit_circuit.py...\033[0m")
    counts: dict[str, int] = runpy.run_path("output/qiskit_circuit.py")["counts"]

    # Prune counts lesser than 10% of max frequency
    most_frequent = max(counts.values()) if counts else 0
    solution_bitstrings = {s for (s, count) in counts.items() if count > most_frequent * 0.1}

    # Measured bitstring -> board (qubit i <-> square qubit_mapping[i], Qiskit is little-endian)
    solutions: list[list[tuple[int, int]]] = []
    for bitstring in solution_bitstrings:
        solution = list(fixed_queens)
        for (bit, pos) in zip(reversed(bitstring.replace(" ", "")), qubit_mapping):
            if bit == '1':
                solution.append(pos)

        # ignore non-sensical solutions: wrong number of queens or attacking queens
        if len(solution) == board_size and is_valid_solution(solution):
            solutions.append(sorted(solution, key=lambda x: x[0]))

    print("\n" + "="*40)
    if solutions:
        print(f"\033[0;32mFound {len(solutions)} valid solution(s):\033[0m")
        for i, sol in enumerate(solutions, 1):
            print(f"\nSolution #{i}: {sol}")
            print_board(sol, board_size, fixed_queens)
    else:
        print("\033[0;31mNo valid solutions found.")
    print("="*40 + "\033[0m", flush=True)

    # Compare the quantum result with the classical baseline
    print(format_metrics(quantum_metrics(counts, qubit_mapping, fixed_queens, board_size, baseline_solutions, config.rounds or None)))

    if not solutions:
        sys.exit(0)

    # Maps the found solution back to the Problem DSL and persists it in JSON
    solution_model = solution_to_dsl(solutions[0], board_size, fixed_queens)
    JSONObjectGenerator(model=solution_model, output_dir="output/").generate()


if __name__ == "__main__":
    main()