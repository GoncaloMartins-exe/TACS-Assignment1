import math

from besser.BUML.metamodel.quantum import (
    QuantumCircuit,
    QuantumRegister,
    ClassicalRegister,
    HadamardGate,
    CXGate,
    RZGate,
    RXGate,
    Measurement)


# ---------------------------------------------------------------------------
# Fixed angle schedule (depth p=1) — these come from the solver config model,
# not derived here; placeholder values shown for a single QAOA layer.
# ---------------------------------------------------------------------------
GAMMA_1 = math.pi / 8
BETA_1 = math.pi / 4


# ---------------------------------------------------------------------------
# Registers: q0=a, q1=b, q2=c. No ancillas needed — Ising cost terms map
# directly onto ZZ interactions between the node qubits themselves.
# ---------------------------------------------------------------------------
node_reg = QuantumRegister(size=3, name="nodes")
cls_reg = ClassicalRegister(size=3, name="result")


qa, qb, qc_ = node_reg.qubits[0], node_reg.qubits[1], node_reg.qubits[2]   # a, b, c


qc = QuantumCircuit(name="TriangleCut")
qc.add_qreg(node_reg)
qc.add_creg(cls_reg)


# ---------------------------------------------------------------------------
# Initial state: uniform superposition |+>^3
# ---------------------------------------------------------------------------
qc.add_operation(HadamardGate(qa))
qc.add_operation(HadamardGate(qb))
qc.add_operation(HadamardGate(qc_))


# ---------------------------------------------------------------------------
# Cost layer U_C(gamma_1): one ZZ-rotation per edge: (a,b), (b,c), (a,c)
# ---------------------------------------------------------------------------


# edge a--b
qc.add_operation(CXGate(control_qubit=qa, target_qubit=qb))
qc.add_operation(RZGate(theta=2 * GAMMA_1, target_qubit=qb))
#def __init__(self, target_qubit: int, theta: float, control_qubits: List[int] = None, control_states: List[ControlState] = None):
qc.add_operation(CXGate(control_qubit=qa, target_qubit=qb))


# edge b--c
qc.add_operation(CXGate(control_qubit=qb, target_qubit=qc_))
qc.add_operation(RZGate(theta=2 * GAMMA_1, target_qubit=qc_))
qc.add_operation(CXGate(control_qubit=qb, target_qubit=qc_))


# edge a--c
qc.add_operation(CXGate(control_qubit=qa, target_qubit=qc_))
qc.add_operation(RZGate(theta=2 * GAMMA_1, target_qubit=qc_))
qc.add_operation(CXGate(control_qubit=qa, target_qubit=qc_))


# ---------------------------------------------------------------------------
# Mixer layer U_B(beta_1): RX on every node qubit
# ---------------------------------------------------------------------------
qc.add_operation(RXGate(theta=2 * BETA_1, target_qubit=qa))
qc.add_operation(RXGate(theta=2 * BETA_1, target_qubit=qb))
qc.add_operation(RXGate(theta=2 * BETA_1, target_qubit=qc_))


# ---------------------------------------------------------------------------
# Measurement (1024 shots comes from the solver config, applied at execution,
# not part of the circuit model itself)
# ---------------------------------------------------------------------------
qc.add_operation(Measurement([qa, qb, qc_], cls_reg))

print("Circuito BESSER criado:", qc.name)
print("Nº de operações:", len(qc.operations))