
import sys

filename = list(filter(lambda x: '--' not in x, sys.argv[1:]))
if len(filename) != 1:
    print(f"Usage: {sys.argv[0]} <file-path> [...flags]")
    print("  |- <file-path>: Path to the simplified problem (JSON)")
    print("  |- --debug-t1, --debug-t2, --debug-qiskit, --debug-all: Print debug information")
    print("  |- --t1: Stop after T1, save results in output/CNF.json")
    exit(1)
    # data = sys.stdin.read()
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
from transformations.json_to_dsl import json_to_dsl
print("\033[0;33mJSON -> Problem...\033[0m")
(problem, fixed_queens, board_size) = json_to_dsl(data)


# Transform problem into CNF
from transformations.t1 import t1
print("\033[0;33mT1: Problem -> CNF...\033[0m")
cnf = t1(problem, debug=debug_t1)

from besser.generators.json import JSONObjectGenerator
if any(x == "--t1" for x in sys.argv):
    JSONObjectGenerator(
        model=cnf,
        output_dir="output/",
    ).generate()
    exit(0)


# Transform CNF into quantum model
from transformations.t2 import t2
print("\033[0;33mT2: CNF -> Quantum Circuit...\033[0m")
(quantum_model, qubit_mapping) = t2(cnf, debug=debug_t2)


# Translate quantum model
from besser.generators.qiskit import QiskitGenerator
import runpy
from pathlib import Path
print("\033[0;33mT3: Quantum Circuit -> Qiskit...\033[0m")
QiskitGenerator(quantum_model, output_dir="output", shots=1024).generate()

# Remove prints from qiskit script
if not debug_qiskit:
    path = Path("output/qiskit_circuit.py")
    lines = path.read_text().splitlines()

    lines = [
        line for line in lines
        if 'print(qc.draw())' not in line
        and 'print("Counts:", counts)' not in line
    ]

    path.write_text("\n".join(lines) + "\n")



# Run qiskit and get solutions
print("\033[0;33mRunning output/qiskit_circuit.py...\033[0m\n  Building circuit...\n  ", end="")
counts: dict[str, int] = runpy.run_path("output/qiskit_circuit.py")["counts"]

# heuristic - prune any count that's clearly lesser than max
most_frequent = max(counts.values())
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

# Check if first solution is correct:
# If yes, probably all solutions are correct
# If no, there is probably no solution
def is_valid_solution(sol: list[tuple[int, int]]):
    if len(sol) <= 1:
        return True
    p1 = sol[0]
    if any(p2 for p2 in sol[1:] if p1[0] == p2[0] or p1[1] == p2[1] or abs(p1[0]-p2[0]) == abs(p1[1]-p2[1])):
        return False
    return is_valid_solution(sol[1:])

if is_valid_solution(solutions[0]):
    solutions = [sorted(sol, key=lambda x: x[0]) for sol in solutions]
    print("\033[0;32mSolutions:")
    for sol in solutions:
        print(f"  - {sol}")
else:
    print("\033[0;31mThere are no solutions.")
print("\033[0m", end="", flush=True)
