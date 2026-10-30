import math
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
    variables = {}
    data_qubits = []
    for obj in cnf.objects:
        if obj.classifier.name == "Literal":
            pos = (obj.row, obj.column)
            if pos not in variables:
                data_qubits.append(pos)
                variables[pos] = len(variables)

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
        lits = lambda d: d.literal if hasattr(d.literal, "__len__") else [d.literal]
        solutions = sum(
            all(any(((x >> variables[(l.row, l.column)]) & 1) == bool(l.queen) for l in lits(d)) for d in disjunctions)
            for x in range(2 ** len(variables))
        )
        iterations = math.floor(math.pi / 4 * math.sqrt(2 ** len(variables) / solutions)) if solutions else 0
    debug(f"Grover iterations: {iterations}")

    # Superposition
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

    for _ in range(iterations):
        # Compute clauses
        compute_groups()

        # X-Gates + Phase Flip
        zgate = PauliZGate(target_qubit=len(variables) + group_size)
        for g in range(1, len(groups)):
            zgate.control_qubits.append(g + len(variables) + group_size)
            zgate.control_states.append(ControlState.CONTROL)
        circuit.add_operation(zgate)

        # Uncompute ancillas
        compute_groups()

        # Diffuser
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