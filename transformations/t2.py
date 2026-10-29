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

def t2(cnf: ObjectModel, debug: bool = True) -> QuantumCircuit:
    debug = print if debug else dont_print

    # Map positions to qubits
    variables = {}
    for obj in cnf.objects:
        if obj.classifier.name == "Literal":
            pos = (obj.row, obj.column)
            if pos not in variables:
                variables[pos] = len(variables)

    debug(f"Variables: {variables}")
    disjunctions = []
    for obj in cnf.objects:
        if obj.classifier.name == "Disjunction":
            disjunctions.append(obj)
    circuit = QuantumCircuit(name="QuantumCircuit", qubits=len(variables) + len(disjunctions))

    debug(f"Need {len(variables) + len(disjunctions)} qubits (data: {len(variables)}, ancillas: {len(disjunctions)})")

    # Superposition
    for i in range(len(variables)):
        hgate = HadamardGate(target_qubit=i)
        circuit.add_operation(hgate)

    # Compute clauses
    for (i, disj) in enumerate(disjunctions):
        ancilla = i + len(variables)
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

    # X-Gates + Phase Flip
    for i in range(len(disjunctions)):
        circuit.add_operation(PauliXGate(target_qubit=i+len(variables)))

    zgate = PauliZGate(target_qubit=len(variables))
    for i in range(1, len(disjunctions)):
        zgate.control_qubits.append(i + len(disjunctions))
        zgate.control_states.append(ControlState.CONTROL)
    circuit.add_operation(zgate)

    for i in range(len(disjunctions)):
        circuit.add_operation(PauliXGate(target_qubit=i+len(variables)))

    # Uncompute ancillas
    for (i, disj) in enumerate(reversed(disjunctions)):
        ancilla = len(variables) + len(disjunctions)-i-1
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

    return circuit
