import itertools
import math


def attacks(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return a[0] == b[0] or a[1] == b[1] or abs(a[0] - b[0]) == abs(a[1] - b[1])


def is_valid_board(queens) -> bool:
    return not any(attacks(a, b) for a, b in itertools.combinations(queens, 2))


def solve_nqueens(board_size: int, fixed_queens) -> list[frozenset[tuple[int, int]]]:
    """Backtracking over the rows without a fixed queen.
    Returns every complete valid board as a frozenset of (row, column), fixed queens included."""
    fixed = frozenset(fixed_queens)
    if not is_valid_board(fixed):
        return []
    free_rows = [row for row in range(1, board_size + 1) if row not in {q[0] for q in fixed}]
    solutions = []

    def place(i: int, queens: frozenset) -> None:
        if i == len(free_rows):
            solutions.append(queens)
            return
        for column in range(1, board_size + 1):
            square = (free_rows[i], column)
            if not any(attacks(square, q) for q in queens):
                place(i + 1, queens | {square})

    place(0, fixed)
    return solutions


def grover_rounds(n_qubits: int, n_solutions: int) -> int:
    """floor(pi/4 * sqrt(N/M)) with N = 2^n [Boyer et al. 1998; Nielsen & Chuang ch. 6]."""
    if n_solutions == 0:
        return 0
    return math.floor(math.pi / 4 * math.sqrt(2 ** n_qubits / n_solutions))


def expected_success_probability(n_qubits: int, n_solutions: int, rounds: int) -> float:
    """sin^2((2k+1) * theta), sin(theta) = sqrt(M/N): chance of measuring a solution after k rounds [Grover 1996]."""
    if n_solutions == 0:
        return 0.0
    theta = math.asin(math.sqrt(n_solutions / 2 ** n_qubits))
    return math.sin((2 * rounds + 1) * theta) ** 2


def decode_bitstring(bitstring: str, qubit_mapping, fixed_queens) -> frozenset[tuple[int, int]]:
    """Qiskit is little-endian: the right-most bit is qubit 0, and qubit_mapping[i] is the board square of qubit i."""
    bits = bitstring.replace(" ", "")
    return frozenset(fixed_queens) | {pos for bit, pos in zip(reversed(bits), qubit_mapping) if bit == "1"}


def quantum_metrics(counts: dict[str, int], qubit_mapping, fixed_queens, board_size: int, baseline_solutions, rounds: int = None) -> dict:
    """Compare the measured counts with the classical baseline. rounds: Grover rounds the circuit used (default: the optimal number)."""
    shots = sum(counts.values())
    valid_shots = 0
    found = set()
    for bitstring, count in counts.items():
        board = decode_bitstring(bitstring, qubit_mapping, fixed_queens)
        if len(board) == board_size and is_valid_board(board):
            valid_shots += count
            found.add(board)

    n_qubits, n_solutions = len(qubit_mapping), len(baseline_solutions)
    if rounds is None:
        rounds = grover_rounds(n_qubits, n_solutions)
    return {
        "search_qubits": n_qubits,
        "assignments": 2 ** n_qubits,
        "solutions": n_solutions,
        "oracle_calls": rounds,
        "shots": shots,
        "success_probability": valid_shots / shots if shots else 0.0,
        "expected_probability": expected_success_probability(n_qubits, n_solutions, rounds),
        "solutions_found": len(found),
        "all_found": found == set(baseline_solutions),
    }


def format_metrics(metrics: dict) -> str:
    solutions, assignments = metrics["solutions"], metrics["assignments"]
    lines = [
        f"Classical baseline: {solutions} solution(s) among {assignments} assignments (2^{metrics['search_qubits']})",
        f"Grover oracle calls: {metrics['oracle_calls']} (brute force would check up to {assignments})",
    ]
    if solutions == 0:
        lines.append("No solution exists: no valid board should be reported")
    else:
        lines.append(
            f"Probability of measuring a valid solution: {metrics['success_probability']:.1%} measured, "
            f"{metrics['expected_probability']:.1%} expected ({metrics['shots']} shots)"
        )
        lines.append(f"Solutions found: {metrics['solutions_found']} of {solutions}")
    return "\n".join(lines)