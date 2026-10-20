# Part I — N-Queens

Group TACS_G12

## Problem DSL

### N-Queens completion

The selected problem is **N-Queens completion**. Given an \(N \times N\) chessboard with some queens already positioned, the goal is to place the remaining queens so that no two queens attack each other (no shared row, column or diagonal).

Normal N-Queens is easy: there are known steps that build a solution for any N. But once some queens are already fixed, these steps can break, and finding a valid completion becomes hard. Gent, Jefferson and Nightingale (2017) proved it is NP-complete. This makes it a good fit for Class B, since it is a hard search problem that can be written as a Boolean formula (CNF) and attacked with Grover's search algorithm (Grover, 1996).

The constraints are:

- At least one queen per row.
- At most one queen per row.
- At most one queen per column.
- At most one queen per diagonal.

The problem model describes the board, the constraints, and any pre-filled queen positions. It does not itself describe the completed solution. It contains no logic and no quantum circuits: all of that is reserved for the transformation to the solution model, so the problem model stays easy to read even for someone who is not familiar with SAT or Grover.

### Test Instance

Along this report, we will be using the following small example (4x4 board with queens at (1,2) and (3,1)). Rows 2 and 4 are still empty, and the only valid completion is a queen at (2,4) and one at (4,3).

| . | Q | . | . |
|---|---|---|---|
| . | . | . | . |
| Q | . | . | . |
| . | . | . | . |

### Problem DSL metamodel

The Problem DSL metamodel is defined in BESSER. It contains the concepts `Problem`, `Board`, `Queen`, `FixedPosition`, and `Constraint`, as well as the `ConstraintType` enumeration.

![N-Queens Problem DSL metamodel](../assets/N_Queens_Diagram.png)

The metamodel defines a `Problem` with a `Board` and a set of `Constraint` objects. The board can contain `Queen` objects and `FixedPosition` objects. The constraint types currently model the row, column, and diagonal rules.

| Concept | Attributes | Description |
|---|---|---|
| `Problem` | `name: str` | Identifies the N-Queens problem instance. |
| `Board` | `size: int` | Defines the dimensions (side length) of the square chessboard. |
| `Queen` | `row: int`, `column: int` | Represents a queen positioned on the board. |
| `FixedPosition` | `row: int`, `column: int` | Represents a queen that is already placed and must be preserved when completing the board. |
| `Constraint` | `type: ConstraintType` | Represents one rule that the solution must satisfy. |
| `ConstraintType` | Enumeration | Defines `AT_LEAST_ONE_PER_ROW`, `AT_MOST_ONE_PER_ROW`, `AT_MOST_ONE_PER_COLUMN`, and `AT_MOST_ONE_PER_DIAGONAL`. |

The main associations are `Problem–Board`, `Problem–Constraint`,
`Board–Queen`, and `Board–FixedPosition`. Each problem has one board
and a set of constraints. A board can contain zero or more queens and
zero or more fixed positions. The `Board–Queen` and
`Board–FixedPosition` associations are compositions, as these objects
belong to their board. The exact multiplicities are defined in the
BESSER metamodel.

#### Design choices

- **Rules are real objects.** A `Problem` owns `Constraint` objects instead of hiding the rules in code. Each rule type later produces one family of clauses in the transformation to the solution model, so any clause in the final formula can be traced back to the rule that caused it.
- **Fixed positions get their own concept.** Pre-filled queens are what turn plain N-Queens into a completion problem. Keeping them separate means they translate directly into the simplest possible clauses (a single cell that must be true).
- **The model describes the start, not the answer.** The board does not have to be full, so the OCL rules below deliberately do not ask for a complete solution.

### Example problem model

The following BESSER Object Diagram illustrates a small N-Queens problem instance. The board size is 4, and the problem is associated with the four constraint types.

![N-Queens example Object Diagram](../assets/N_Queens_Object%20Diagram.png)

The Object Diagram represents the problem instance and its constraints,
rather than a completed solution. The pre-filled queens are represented
by `FixedPosition` objects associated with the board. These positions
must remain unchanged when the remaining queens are placed. The
Object Diagram must therefore include one `FixedPosition` object for
each pre-filled queen in the test instance.

### OCL constraints

OCL (Object Constraint Language) is used to specify additional invariants that instances of the Problem DSL metamodel must satisfy. The constraints are defined in `constraints/NQueens.ocl`.

The following invariants are specified:

- **ValidSize:** the board size must be greater than zero.
- **QueensWithinBoard:** every queen must have row and column coordinates within the board boundaries.
- **FixedPositionsWithinBoard:** every fixed position must lie within the board boundaries.
- **FixedPositionsCorrespondToQueens:** every fixed position must correspond to a queen placed at the same coordinates.
- **NoConflictingQueens:** no two distinct queens may share a row, column, or diagonal.
- **NoConflictingFixedPositions:** no two fixed positions may conflict by sharing a row, column, or diagonal.

These invariants ensure that the model represents a valid partial N-Queens configuration. The board is not required to be complete at this stage, since the purpose of the problem DSL is to represent the initial state of the completion problem.

Why the last invariant matters: if two fixed queens already attack each other, the puzzle can never be solved, and the formula would be unsatisfiable for a trivial reason. We catch that at the model level instead of letting it surface later.

The OCL constraints complement the structural restrictions of the metamodel by expressing semantic properties of the problem. Their syntax and compatibility with the selected OCL implementation must be validated before execution.

## Solution DSL

The solution model is a Boolean formula in **Conjunctive Normal Form (CNF)**, and it acts as a checklist. The formula is an AND of several clauses, and each clause is an OR of simple yes or no statements. The formula is only true when every clause on the checklist is satisfied.

The problem can be mapped into CNF with one variable per cell of the board. For example, on an empty 4x4 board, if we want to ensure there is exactly one queen on the first row, we can represent that as (first digit = row, second digit = column):

$$
(11 \lor 12 \lor 13 \lor 14) \land (\neg 11 \lor \neg 12) \land (\neg 11 \lor \neg 13) \land (\neg 11 \lor \neg 14) \land (\neg 12 \lor \neg 13) \land (\neg 12 \lor \neg 14) \land (\neg 13 \lor \neg 14)
$$

We use plain CNF because Grover's oracle (Nielsen and Chuang, ch. 6) is built clause by clause. Each clause is computed into a helper qubit (an ancilla), a multi-controlled gate checks that all helpers are true, and then everything is undone (uncomputed). The structure of the model therefore mirrors the structure of the circuit.

### Metamodel

The metamodel is a basic CNF with literals specialized for the N-Queens problem:

![CNF metamodel for N-Queens](../assets/cnf_metamodel.png)

| Concept | Attributes | Description |
|---|---|---|
| `Board` | `size: int` | Defines the board dimensions |
| `Conjunction` | | Represents a CNF instance, i.e. a conjunction of clauses (disjunctions), i.e. an "AND of ORs" |
| `Disjunction` | | Represents a disjunction of literals, i.e. an "OR of conditions" (one clause) |
| `Literal` | `queen: bool`, `row: int`, `column: int` | Represents whether there can be a queen at the given row and column (within the context of the disjunction it belongs to). With `queen = true` it claims "there is a queen at this cell"; with `queen = false` it claims "there is no queen at this cell" (a negation). |

### How the problem rules become clauses

| Problem concept | Clauses it produces | Source |
|---|---|---|
| `FixedPosition` (r,c) | one single-literal clause (rc) | encoding of a partial assignment |
| `AT_LEAST_ONE_PER_ROW` | one clause per row, e.g. (11 ∨ 12 ∨ 13 ∨ 14) | Gent et al., 2017 |
| `AT_MOST_ONE_PER_ROW`, `_COLUMN`, `_DIAGONAL` | for every pair of cells on the same line, a clause (¬a ∨ ¬b), meaning "not both" | standard pairwise at-most-one encoding |

### Example Solution Model

The CNF for an empty board gets very verbose. For an empty 4x4 board, it can be written as follows:

At least one queen per row:

$$
\newline
(11 \lor 12 \lor 13 \lor 14) \land (21 \lor 22 \lor 23 \lor 24) \land (31 \lor 32 \lor 33 \lor 34) \land (41 \lor 42 \lor 43 \lor 44)
\newline
$$

At most one queen per row:

$$
\newline
\land [(\neg 11 \lor \neg 12) \land (\neg 11 \lor \neg 13) \land (\neg 11 \lor \neg 14) \land (\neg 12 \lor \neg 13) \land (\neg 12 \lor \neg 14) \land (\neg 13 \lor \neg 14)]
\newline
\land [(\neg 21 \lor \neg 22) \land (\neg 21 \lor \neg 23) \land (\neg 21 \lor \neg 24) \land (\neg 22 \lor \neg 23) \land (\neg 22 \lor \neg 24) \land (\neg 23 \lor \neg 24)]
\newline
\land [(\neg 31 \lor \neg 32) \land (\neg 31 \lor \neg 33) \land (\neg 31 \lor \neg 34) \land (\neg 32 \lor \neg 33) \land (\neg 32 \lor \neg 34) \land (\neg 33 \lor \neg 34)]
\newline
\land [(\neg 41 \lor \neg 42) \land (\neg 41 \lor \neg 43) \land (\neg 41 \lor \neg 44) \land (\neg 42 \lor \neg 43) \land (\neg 42 \lor \neg 44) \land (\neg 43 \lor \neg 44)]
\newline
$$

At most one queen per column:

$$
\newline
\land [(\neg 11 \lor \neg 21) \land (\neg 11 \lor \neg 31) \land (\neg 11 \lor \neg 41) \land (\neg 21 \lor \neg 31) \land (\neg 21 \lor \neg 41) \land (\neg 31 \lor \neg 41)]
\newline
\land [(\neg 12 \lor \neg 22) \land (\neg 12 \lor \neg 32) \land (\neg 12 \lor \neg 42) \land (\neg 22 \lor \neg 32) \land (\neg 22 \lor \neg 42) \land (\neg 32 \lor \neg 42)]
\newline
\land [(\neg 13 \lor \neg 23) \land (\neg 13 \lor \neg 33) \land (\neg 13 \lor \neg 43) \land (\neg 23 \lor \neg 33) \land (\neg 23 \lor \neg 43) \land (\neg 33 \lor \neg 43)]
\newline
\land [(\neg 14 \lor \neg 24) \land (\neg 14 \lor \neg 34) \land (\neg 14 \lor \neg 44) \land (\neg 24 \lor \neg 34) \land (\neg 24 \lor \neg 44) \land (\neg 34 \lor \neg 44)]
\newline
$$

At most one queen per diagonal:

$$
\newline
\land [(\neg 13 \lor \neg 24)]
\newline
\land [(\neg 12 \lor \neg 23) \land (\neg 12 \lor \neg 34) \land (\neg 23 \lor \neg 34)]
\newline
\land [(\neg 11 \lor \neg 22) \land (\neg 11 \lor \neg 33) \land (\neg 11 \lor \neg 44) \land (\neg 22 \lor \neg 33) \land (\neg 22 \lor \neg 44) \land (\neg 33 \lor \neg 44)]
\newline
\land [(\neg 21 \lor \neg 32) \land (\neg 21 \lor \neg 43) \land (\neg 32 \lor \neg 43)]
\newline
\land [(\neg 31 \lor \neg 42)]
$$

---

Fortunately, the CNF can be reduced drastically when given initial queen positions. Each fixed queen cancels every cell it attacks, and those cells disappear from the formula. On a 4x4 board with queens at (1,2) and (3,1), there are only 3 possible positions for the remaining 2 queens:

| . | Q | . | . |
|---|---|---|---|
| . | . | . | ? |
| Q | . | . | . |
| . | . | ? | ? |

This can be translated to the following CNF:

$$
(24) \land (43 \lor 44) \land (\neg 43 \lor \neg 44) \land (\neg 24 \lor \neg 44)
$$

Read it as a checklist:

- there must be a queen at 24;
- there is a queen at 43 or 44, but not both;
- and not 24 together with 44.

The only assignment that passes all four clauses is 24 and 43 true, 44 false, so there is exactly one solution.

![Example CNF object diagram](../assets/cnf_object_model.png)

### OCL Constraints

This model contains only a subset of the constraints in the problem DSL:
- **ValidSize:** the board size must be greater than zero.
- **PositionsWithinBoard:** all positions must be within board

Although these invariants enforce a semantically correct model, they do not ensure that the CNF is satisfiable. "No solution" is a valid outcome for a completion problem, so this is deliberate.

<!-- ## Codification

### Limit of 12 qubits

The quantum circuit implementation is subject to a limit of **12 qubits**. The encoding therefore affects the size of the instances that can be considered.

For a \(4 \times 4\) board:

- 4 rows correspond to 4 variables.
- Each variable requires \(\log_2(4)=2\) qubits to encode the column of the queen in that row.
- Total: \(4 \times 2 = 8\) qubits.

Therefore, a \(4 \times 4\) N-Queens instance fits within the 12-qubit limit. Under this encoding, a row variable represents the column selected for the queen in that row. Pre-filled positions restrict the corresponding variable to the specified column. -->

## References

- Grover, L. K. (1996). A fast quantum mechanical algorithm for database search. *STOC*.
- Gent, I. P., Jefferson, C., Nightingale, P. (2017). Complexity of n-Queens completion. *Journal of Artificial Intelligence Research*.
- Nielsen, M. A., Chuang, I. L. *Quantum Computation and Quantum Information*, ch. 6.