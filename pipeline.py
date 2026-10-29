from transformations.json_to_dsl import json_to_dsl
from transformations.t1 import t1
from transformations.t2 import t2
import sys
from besser.generators.json import JSONObjectGenerator

if len(sys.argv) > 1:
    with open(sys.argv[1], "r") as f:
        data = f.read()
else:
    print(f"Usage: {sys.argv[0]} <file-path>")
    exit(1)
    # data = sys.stdin.read()

problem = json_to_dsl(data)
cnf = t1(problem)
qiskit_model = t2(cnf)
# TODO

# JSONObjectGenerator(
#     model=cnf,
#     output_dir="output/",
# ).generate()
