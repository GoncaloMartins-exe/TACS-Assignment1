import json, sys
from metamodels.Metamodel_NQueens import Board, Problem, Constraint, ConstraintType, FixedPosition, Queen
from besser.BUML.metamodel.object import ObjectModel
from besser.generators.json import JSONObjectGenerator

def json_to_dsl(data: str) -> ObjectModel:
    data = json.loads(data)

    problem = Problem("Queens").attributes(name = "NQueens_Problem").build()
    size = data["board_size"]
    board = Board(f"Board_{size}x{size}").attributes(size = size).build()
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

    model = ObjectModel(
        name = "ProblemDSL",
        objects = set([board, problem]).union(queens).union(fixedpos),
    )

    return model

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as f:
            data = f.read()
    else:
        data = sys.stdin.read()

    JSONObjectGenerator(
        model=json_to_dsl(data),
        output_dir="output/",
    ).generate()
