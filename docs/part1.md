## Problems
1. **N-queens completation**: **N**x**N** board that must start with some queens already positioned and completed with the rest.
   - At max one queen per row, column and diagonal.

## Codification
#### Limit of **12 qubits**

The 12-qubit limit constrains the number of variables encoded in the quantum circuit.

### **N-Queens**

For a *4x4* board:

- 4 rows = 4 variables
- Each variable requires `log2(4) = 2` qubits
- Total: `4 x 2 = 8` qubits

Therefore, a *4x4 N-Queens* instance fits within the 12-qubit limit.

#### (**2 queens pre-filled** leaving **2 queens to be placed** -> `8 qubits`).

## Tests

### Queens

| . | Q | . | . |
|---|---|---|---|
| . | . | . | `Q` |
| Q | . | . | . |
| . | . | `Q` | . |

## Solution DSL

### N-Queens
The solution always contains one queen per row. Therefore, we can represent $q_r$ as the column of the queen at row `r`. The constraints can then be written as follows (cannot be on the same column nor on the same diagonal):

$$\forall r \neq s, q_r \neq q_s \land |q_r - q_s| \neq |r-s| $$

CNF is really verbose. Here's the CNF for N=4:

$$
% One \; queen \; per \; row:
\newline
(11 \lor 12 \lor 13 \lor 14) \land (21 \lor 22 \lor 23 \lor 24) \land (31 \lor 32 \lor 33 \lor 34) \land (41 \lor 42 \lor 43 \lor 44)
\newline
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

$$
% One \; queen \; per \; column:
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

$$
% One \; queen \; per \; diagonal:
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
