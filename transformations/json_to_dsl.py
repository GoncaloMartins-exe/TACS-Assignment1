import json, sys
from metamodels.Metamodel_NQueens import Board, Problem, Constraint, ConstraintType, FixedPosition, Queen
from besser.BUML.metamodel.object import ObjectModel
from besser.generators.json import JSONObjectGenerator

if len(sys.argv) > 1:
    with open(sys.argv[1], "r") as f:
        data = f.read()
else:
    data = sys.stdin.read()

def json_to_dsl(data):
    data = json.loads(data)

    problem = Problem("Queens").attributes(name = "NQueens_Problem").build()
    board = Board("Board").attributes(size = data["board_size"]).build()
    problem.board = board
    board.problem = problem
    queens = set()
    fixedpos = set()

    for (i, queen) in enumerate(data["queens"]):
        fixed_pos = FixedPosition(f"fixed_position_{i}").attributes(row = queen[0], column = queen[1]).build()
        queen = Queen(f"queen_{i}").attributes(row = queen[0], column = queen[1]).build()
        queens.add(queen)
        fixedpos.add(fixed_pos)

    board.queen = queens
    board.fixedposition = fixedpos

    return set([board, problem]).union(queens).union(fixedpos)

objects = json_to_dsl(data)
problem = ObjectModel(
    name = "ProblemDSL",
    objects = objects,
)

JSONObjectGenerator(model=problem, output_dir="output/").generate()