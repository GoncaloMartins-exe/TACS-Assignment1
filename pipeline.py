
import sys
if len(sys.argv) > 1:
    with open(sys.argv[1], "r") as f:
        data = f.read()
else:
    print(f"Usage: {sys.argv[0]} <file-path>")
    exit(1)
    # data = sys.stdin.read()

from transformations.json_to_dsl import json_to_dsl
problem = json_to_dsl(data)

from transformations.t1 import t1
cnf = t1(problem)

from transformations.t2 import t2
quantum_model = t2(cnf)

from besser.generators.qiskit import QiskitGenerator
import runpy
QiskitGenerator(quantum_model, output_dir="output", shots=1024).generate()
counts = runpy.run_path("output/qiskit_circuit.py")["counts"]
# print(counts)

# from besser.generators.json import JSONObjectGenerator
# JSONObjectGenerator(
#     model=cnf,
#     output_dir="output/",
# ).generate()
