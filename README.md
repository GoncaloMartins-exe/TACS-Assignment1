# N-Queens Completion: Model-Driven Quantum Pipeline

**Group:** TACS_G12  
**Course:** TACS — MEIC / Faculdade de Engenharia da Universidade do Porto  

This project implements an end-to-end Model-Driven Engineering (MDE) pipeline that models, transforms, and solves the **N-Queens Completion** problem using Grover's Quantum Search Algorithm. Built on top of the **BESSER** modeling framework, the pipeline transforms high-level domain models into Conjunctive Normal Form (CNF) Boolean logic, generates platform-independent quantum circuit models, and executes transpiled Qiskit code on classical simulators.

---

## Architecture & Transformation Pipeline

```text
[ Input JSON ]
      │
      ▼ (json_to_dsl + OCL Validation)
[ Problem DSL Model ]
      │
      ▼ (T1: transformations/t1.py)
[ CNF Solution DSL Model ] ──► (Persisted as output/CNF.json)
      │
      ▼ (T2: transformations/t2.py)
[ Quantum Circuit DSL Model ]
      │
      ▼ (T3: QiskitGenerator M2T)
[ output/qiskit_circuit.py ]
      │
      ▼ (Qiskit Aer Simulator Execution)
[ Measured Solutions & Metrics ]
      │
      ▼ (solution_to_dsl)
[ Problem DSL Solution Model ] ──► (Persisted as output/SolutionProblemDSL.json)
```

1. **Input Parsing & Validation (`json_to_dsl.py`):** Loads simplified JSON problem instances into the `Problem DSL` and validates them against `constraints/NQueens.ocl` invariants.
2. **Transformation T1 (`transformations/t1.py`):** Translates row, column, diagonal, and fixed position constraints into a CNF model (`Solution DSL`).
3. **Transformation T2 (`transformations/t2.py`):** Constructs a BESSER Quantum Circuit model containing data qubits, grouped ancilla clause evaluation, phase inversion, uncomputation, and a Grover diffuser.
4. **Code Generation T3 & Execution:** Generates Qiskit code using `QiskitGenerator`, executes it on the `AerSimulator`, decodes `little-endian` bitstrings, and prints valid ASCII chessboards.
5. **Solution Back-Mapping:** Maps valid measured states back into a populated `Problem DSL` `ObjectModel` containing final `Queen` placements.

---

## Project Structure

```text
├── assets/                  # Diagrams and metamodel images
├── config/                  # Solver configuration files (shots, rounds, group_size)
├── constraints/             # OCL constraints for Problem DSL (NQueens.ocl)
├── docs/                    # Deliverable report sections (part1.md, part2.md)
├── input/                   # Problem instances (4x4, 5x5, 6x6, 10x10)
├── metamodels/              # BESSER metamodel definitions (Problem, CNF, SolverConfig)
├── models/                  # BUML model instances
├── ocl/                     # OCL constraints for Solver Config
├── output/                  # Generated intermediate models, Qiskit scripts, and results
├── tests/                   # Unit and regression test suites
├── transformations/         # Model-to-Model transformations (json_to_dsl, t1, t2)
├── baseline.py              # Classical backtracking solver and quantum metrics calculator
├── Makefile                 # Automation script for running, validating, and cleaning
├── pipeline.py              # Main execution entry point
├── README.md                # Project overview and usage guide
├── requirements.txt         # Python dependencies
├── solver_config.py         # Solver configuration loader with OCL validation
└── validation.py            # Automated evaluation suite across all test instances
```

# Setup

Create and activate a Python virtual environment, then install the required dependencies.

### 1. Create virtual environment

```bash
python3 -m venv .venv
```

### 2. Activate virtual environment

**Linux:**

```bash
source .venv/bin/activate
```

**Windows:**

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

# Run

Select one of the files in the `input/` directory (or create your own) and run:
```bash
python pipeline.py <file-path>
```

# Makefile Commands

<table>
  <tr>
    <th>Command</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>

```bash
make run
```

</td>
    <td>Run the pipeline sequentially on the 3 main test instances</td>
  </tr>
  <tr>
    <td>

```bash
make validate
```

</td>
    <td>Run the complete validation suite against the classical baseline</td>
  </tr>
  <tr>
    <td>

```bash
make clean
```

</td>
    <td>Clean generated output artifacts and Python caches</td>
  </tr>
  <tr>
    <td>

```bash
make help
```

</td>
    <td>Display all available commands</td>
  </tr>
</table>