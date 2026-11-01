import argparse
import contextlib
import glob
import io
import runpy
import time
from pathlib import Path

from baseline import quantum_metrics, solve_nqueens
from besser.generators.qiskit import QiskitGenerator
from transformations.json_to_dsl import json_to_dsl
from transformations.t1 import t1
from transformations.t2 import t2


def validate(path: str, shots: int, max_qubits: int) -> dict:
    name = Path(path).stem
    problem, fixed_queens, board_size = json_to_dsl(Path(path).read_text())
    cnf = t1(problem)

    start = time.perf_counter()
    baseline_solutions = solve_nqueens(board_size, fixed_queens)
    baseline_ms = (time.perf_counter() - start) * 1000

    # Build the circuit without Grover rounds first, only to know how many qubits it needs
    n_qubits = t2(cnf, iterations=0, debug=False)[0].num_qubits
    if n_qubits > max_qubits:
        return {"instance": name, "qubits": n_qubits, "skipped": f"needs {n_qubits} qubits (limit {max_qubits})"}

    circuit, qubit_mapping = t2(cnf, solutions=len(baseline_solutions), debug=False)
    output_dir = f"output/validation/{name}"
    start = time.perf_counter()
    with contextlib.redirect_stdout(io.StringIO()):   # the generated script prints the circuit drawing
        QiskitGenerator(circuit, output_dir=output_dir, shots=shots).generate()
        counts = runpy.run_path(f"{output_dir}/qiskit_circuit.py")["counts"]
    simulation_s = time.perf_counter() - start

    metrics = quantum_metrics(counts, qubit_mapping, fixed_queens, board_size, baseline_solutions)
    return {"instance": name, "qubits": n_qubits, "baseline_ms": baseline_ms, "simulation_s": simulation_s, **metrics}


HEADER = ["instance", "qubits", "search", "M", "oracle calls", "P(valid) measured", "P(valid) expected", "found", "baseline", "simulation"]


def table_row(r: dict) -> list[str]:
    if "skipped" in r:
        return [r["instance"], str(r["qubits"]), "-", "-", "-", "-", "-", "-", "-", f"skipped: {r['skipped']}"]
    solved = r["solutions"] > 0
    return [
        r["instance"], str(r["qubits"]), str(r["search_qubits"]), str(r["solutions"]), str(r["oracle_calls"]),
        f"{r['success_probability']:.1%}" if solved else "-",
        f"{r['expected_probability']:.1%}" if solved else "-",
        f"{r['solutions_found']}/{r['solutions']}" if solved else "none expected",
        f"{r['baseline_ms']:.1f} ms", f"{r['simulation_s']:.1f} s",
    ]


def print_table(rows: list[list[str]]) -> None:
    widths = [max(len(line[i]) for line in [HEADER] + rows) for i in range(len(HEADER))]
    for line in [HEADER] + rows:
        print("  ".join(cell.ljust(width) for cell, width in zip(line, widths)))


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the chain against the classical baseline")
    parser.add_argument("files", nargs="*", help="problem files (JSON); default: input/*.json")
    parser.add_argument("--shots", type=int, default=1024)
    parser.add_argument("--max-qubits", type=int, default=22)
    args = parser.parse_args()

    files = args.files or sorted(glob.glob("input/*.json"))
    rows = []
    for path in files:
        print(f"Validating {path} ...", flush=True)
        rows.append(table_row(validate(path, args.shots, args.max_qubits)))

    print()
    print_table(rows)

    Path("output").mkdir(exist_ok=True)
    markdown = ["| " + " | ".join(HEADER) + " |", "|" + "---|" * len(HEADER)]
    markdown += ["| " + " | ".join(row) + " |" for row in rows]
    Path("output/validation_results.md").write_text("\n".join(markdown) + "\n")
    print("\nResults saved to output/validation_results.md")


if __name__ == "__main__":
    main()
