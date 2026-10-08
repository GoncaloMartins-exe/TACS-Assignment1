## Problems
1. **N-queens completation**: **N**x**N** board that must start with some queens already positioned and completed with the rest.
   - At max one queen per row, column and diagonal.
  
2. **Latin square completation**: given a **N**x**N** board partially filled, complete it so that each value appears once in each row and column.
    - Does'nt have the diagonal restriction.
________________________________________________________________________
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

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

### **Latin Square**

For a *4x4* Latin Square, each cell contains a value from `1` to `4`.

- Each cell requires `log2(4) = 2` qubits
- Pre-filled cells are fixed and do not require qubits
- Only empty cells are encoded as quantum variables

Therefore, with a 12-qubit limit:

- Maximum number of empty cells: `12 / 2 = 6`

#### (**10 cells pre-filled** and **6 free** -> `12 qubits`).
________________________________________________________________________