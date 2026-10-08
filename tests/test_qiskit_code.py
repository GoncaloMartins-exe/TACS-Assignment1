import sys
import os
sys.path = [p.strip() for p in sys.path if p]
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile


from qiskit_aer import AerSimulator


from qiskit.circuit.library import *
import numpy as np




# Initialize Registers


nodes = QuantumRegister(3, 'nodes')


result = ClassicalRegister(3, 'result')




# Initialize Circuit
qc = QuantumCircuit(nodes, result)


# Operations


qc.append(HGate(), [nodes[0]])


qc.append(HGate(), [nodes[1]])


qc.append(HGate(), [nodes[2]])


qc.append(CXGate(), [nodes[0], nodes[1]])


qc.append(RZGate(0.7853981633974483), [nodes[1]])


qc.append(CXGate(), [nodes[0], nodes[1]])


qc.append(CXGate(), [nodes[1], nodes[2]])


qc.append(RZGate(0.7853981633974483), [nodes[2]])


qc.append(CXGate(), [nodes[1], nodes[2]])


qc.append(CXGate(), [nodes[0], nodes[2]])


qc.append(RZGate(0.7853981633974483), [nodes[2]])


qc.append(CXGate(), [nodes[0], nodes[2]])


qc.append(RXGate(1.5707963267948966), [nodes[0]])


qc.append(RXGate(1.5707963267948966), [nodes[1]])


qc.append(RXGate(1.5707963267948966), [nodes[2]])


# Draw
print(qc.draw())


qc.measure(nodes, result)


# Execution (Local Aer Simulator)
print("Simulating circuit with Aer Simulator...")
simulator = AerSimulator()
transpiled_qc = transpile(qc, simulator)
sim_result = simulator.run(transpiled_qc, shots=1024).result()
counts = sim_result.get_counts()
print("Counts:", counts)
