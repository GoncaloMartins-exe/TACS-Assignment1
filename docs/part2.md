# Part II: Quantum Transformation, Code Generation, and Validation

Group TACS_G12

## T2: CNF to Quantum Circuit

`transformations/t2.py` converts the CNF model into a platform-independent BESSER quantum circuit.

- Each candidate board cell in the CNF gets a **data qubit**. A value of 1 means a queen is placed; 0 means the cell is empty.
- Extra **ancilla qubits** are used to check clauses and combine their results. By default, clauses are split into groups of about $\sqrt{C}$, where $C$ is the number of clauses. The group size can also be set in the solver configuration.
- Hadamard gates put the data qubits into a superposition of all $2^n$ assignments.
- The oracle checks the CNF, flips the phase of satisfying assignments, and clears the ancillas. The diffuser then amplifies those assignments. These steps are repeated for the selected number of Grover rounds, and the data qubits are measured.

If the number of rounds is not set in the configuration, T2 calculates it from $n$, the number of data qubits, and $M$, the number of solutions found by the classical solver:

$$
k = \left\lfloor \frac{\pi}{4} \sqrt{\frac{2^n}{M}} \right\rfloor
$$

If there are no solutions ($M = 0$), the circuit uses zero Grover rounds.

## T3: Code Generation and Execution

`QiskitGenerator` translates the quantum model into a Python script. The pipeline runs that script with Qiskit's `AerSimulator`, using the configured number of shots.

Each measured bitstring is mapped back to board cells using `qubit_mapping`. The pipeline accounts for Qiskit's bit order, adds the fixed queens, and keeps bitstrings whose counts are more than 10% of the highest count. Valid boards are then printed as solutions.

## Validation Results

The classical backtracking solver, `solve_nqueens` in `baseline.py`, provides the reference solution count and configurations. The table summarizes the recorded Aer Simulator runs with 1024 shots.

| Instance | Data qubits | Total qubits | Solutions | Grover rounds | Solutions found |
|---|---:|---:|---:|---:|---:|
| `10x10_seven_queens` | 6 | 13 | 2 | 4 | 2 / 2 |
| `4x4_impossible` | 6 | 14 | 0 | 0 | 0 / 0 |
| `4x4_one_queen` | 6 | 14 | 1 | 6 | 1 / 1 |
| `4x4_two_queens` | 3 | 7 | 1 | 2 | 1 / 1 |
| `5x5_impossible` | 4 | 10 | 0 | 0 | 0 / 0 |
| `5x5_two_queens` | 4 | 9 | 1 | 3 | 1 / 1 |
| `6x6_three_queens` | 5 | 12 | 1 | 4 | 1 / 1 |

All solutions were found for the satisfiable instances in these runs. The two impossible instances correctly produced no solutions.

## Limitations

The number of possible assignments grows exponentially with the number of data qubits, which limits classical simulation of large boards. The CNF oracle also needs ancillas to evaluate clauses and clause groups. Fixed queens reduce the search by removing cells that cannot contain another queen.