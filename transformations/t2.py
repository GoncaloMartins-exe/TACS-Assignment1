from besser.BUML.metamodel.quantum.quantum import (
    QuantumCircuit, QuantumRegister, ClassicalRegister,
    HadamardGate, PauliXGate, PauliYGate, PauliZGate,
    SGate, TGate, SwapGate, RXGate, RYGate, RZGate, PhaseGate,
    ControlState, Measurement, InputGate, QFTGate, PhaseGradientGate,
    ArithmeticGate, ModularArithmeticGate, ComparisonGate, CustomGate,
    DisplayOperation, TimeDependentGate, SpacerGate, PostSelection,
    PrimitiveGate, ParametricGate, OrderGate, ScalarGate, FunctionGate,
    GateDefinition
)
from metamodels.cnf_metamodel import Board, Conjunction, Disjunction, Literal
from besser.BUML.metamodel.object import ObjectModel, Object

def dont_print(*values, end = None):
    return

def t2(cnf: ObjectModel, group_size: int = None, iterations: int = None, debug: bool = True) -> tuple[
    QuantumCircuit,
    list[tuple[int, int]]
]:
    debug = print if debug else dont_print

    # Map positions to qubits and vice-versa
    data_qubits = sorted({(obj.row, obj.column) for obj in cnf.objects if obj.classifier.name == "Literal"})
    variables = {pos: i for i, pos in enumerate(data_qubits)}

    debug(f"Variables: {variables}")
    disjunctions = []
    for obj in cnf.objects:
        if obj.classifier.name == "Disjunction":
            disjunctions.append(obj)
    if group_size is None:
        group_size = max(1, round(len(disjunctions) ** 0.5))
    groups = [disjunctions[i:i + group_size] for i in range(0, len(disjunctions), group_size)]
    # circuit = QuantumCircuit(name="QuantumCircuit", qubits=len(variables) + len(disjunctions))
    circuit = QuantumCircuit(name="QuantumCircuit")
    circuit.add_qreg(QuantumRegister(name="q", size=len(variables) + group_size + len(groups)))
    circuit.add_creg(ClassicalRegister(name="c", size=len(variables)))

    debug(f"Need {len(variables) + group_size + len(groups)} qubits (data: {len(variables)}, ancillas: {group_size + len(groups)})")

    if iterations is None:
        raise ValueError("iterations must come from the solver config")
    debug(f"Grover iterations: {iterations}")

    # Superposition: equal amplitude over all 2^n assignments [Grover 1996; Nielsen & Chuang ch. 6]
    for i in range(len(variables)):
        hgate = HadamardGate(target_qubit=i)
        circuit.add_operation(hgate)

    def clause(disj, ancilla):
        literals = disj.literal
        try:
            len(literals)
        except:
            literals = [literals]

        xgate = PauliXGate(target_qubit=ancilla)
        for literal in literals:
            q = variables[(literal.row, literal.column)]
            xgate.control_qubits.append(q)
            xgate.control_states.append(ControlState.ANTI_CONTROL if literal.queen else ControlState.CONTROL)
        circuit.add_operation(xgate)

    def compute_groups():
        for (g, group) in enumerate(groups):
            for (i, disj) in enumerate(group):
                clause(disj, len(variables) + i)
            xgate = PauliXGate(target_qubit=len(variables) + group_size + g)
            for i in range(len(group)):
                xgate.control_qubits.append(len(variables) + i)
                xgate.control_states.append(ControlState.ANTI_CONTROL)
            circuit.add_operation(xgate)
            for (i, disj) in enumerate(group):
                clause(disj, len(variables) + i)

    # Rounds k = floor(pi/4 * sqrt(N/M)), N = 2^n, M = number of solutions, given by the solver config [Boyer et al. 1998; Nielsen & Chuang ch. 6]
    for _ in range(iterations):
        # Compute clauses: oracle step, group result qubit = 1 iff every clause of the group holds [Grover 1996; Nielsen & Chuang ch. 6]
        compute_groups()

        # Phase Flip: -1 on assignments where all groups hold, i.e. the CNF is satisfied [Grover 1996; Nielsen & Chuang ch. 6]
        zgate = PauliZGate(target_qubit=len(variables) + group_size)
        for g in range(1, len(groups)):
            zgate.control_qubits.append(g + len(variables) + group_size)
            zgate.control_states.append(ControlState.CONTROL)
        circuit.add_operation(zgate)

        # Uncompute ancillas: back to |0>, so they do not stay entangled with the data qubits [Nielsen & Chuang ch. 6]
        compute_groups()

        # Diffuser: inversion about the mean [Grover 1996; Nielsen & Chuang ch. 6]
        for i in range(len(variables)):
            circuit.add_operation(HadamardGate(target_qubit=i))
        for i in range(len(variables)):
            circuit.add_operation(PauliXGate(target_qubit=i))

        zgate = PauliZGate(target_qubit=0)
        for i in range(1, len(variables)):
            zgate.control_qubits.append(i)
            zgate.control_states.append(ControlState.CONTROL)
        circuit.add_operation(zgate)

        for i in range(len(variables)):
            circuit.add_operation(PauliXGate(target_qubit=i))
        for i in range(len(variables)):
            circuit.add_operation(HadamardGate(target_qubit=i))

    # Measure
    for i in range(len(variables)):
        circuit.add_operation(Measurement(target_qubit=i, output_bit=i, basis='Z'))

    return (circuit, data_qubits)