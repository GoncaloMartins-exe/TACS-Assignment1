import json, sys
from metamodels.Metamodel_NQueens import Board, Problem, Constraint, ConstraintType, FixedPosition, Queen

if len(sys.argv) > 1:
    with open(sys.argv[1], "r") as f:
        data = f.read()
else:
    data = sys.stdin.read()

def json_to_dsl(data) -> Problem:
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

    return problem

print(json_to_dsl(data))
