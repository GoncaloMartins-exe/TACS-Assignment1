import json, sys
import re
from pathlib import Path
from besser.BUML.metamodel.structural import Constraint
from bocl.OCLWrapper import OCLWrapper
from metamodels.Metamodel_NQueens import (
    Board, Problem, Queen, FixedPosition, domain_model
)
from besser.BUML.metamodel.object import ObjectModel
from besser.generators.json import JSONObjectGenerator

OCL_FILE = "constraints/NQueens.ocl"

CLASS_MAP = {
    "Problem": Problem,
    "Board": Board,
    "Queen": Queen,
    "FixedPosition": FixedPosition,
}


def read_ocl_constraints(path: str = OCL_FILE) -> list[Constraint]:
    """Read the OCL constraints and associate each one with its respective metamodel."""
    if not Path(path).exists():
        return []
        
    text = Path(path).read_text()
    blocks = re.split(r"(?m)^(?=context\s)", text)
    constraints = []
    
    for block in filter(str.strip, blocks):
        match = re.match(r"context\s+(\w+)\s+inv\s+(\w+)\s*:", block)
        if match:
            class_name, inv_name = match.group(1), match.group(2)
            target_class = CLASS_MAP.get(class_name)
            if target_class:
                constraints.append(
                    Constraint(
                        name=inv_name,
                        context=target_class,
                        expression=block.strip(),
                        language="OCL",
                    )
                )
    return constraints


def validate_problem_ocl(model: ObjectModel, ocl_path: str = OCL_FILE) -> None:
    """Validates the object model against the OCL constraints file."""
    constraints = read_ocl_constraints(ocl_path)
    if not constraints:
        return

    wrapper = OCLWrapper(domain_model, model)
    violated = [c.name for c in constraints if wrapper.evaluate(c) is not True]

    if violated:
        raise ValueError(
            f"Invalid problem instance: violates OCL constraint(s) {', '.join(violated)} (see {ocl_path})"
        )


def json_to_dsl(data: str) -> tuple[
    ObjectModel,
    set[tuple[int, int]],
    int,
]:
    data = json.loads(data)

    problem = Problem("Queens").attributes(name = "NQueens_Problem").build()
    size = data["board_size"]
    board = Board(f"Board_{size}x{size}").attributes(size = size).build()
    problem.board = board
    board.problem = problem
    queens = set()
    fixedpos = set()
    fixed_queens = set()

    for (i, queen) in enumerate(data["queens"]):
        fixed_queens.add((queen[0], queen[1]))
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

    # OCL validation of the instance
    validate_problem_ocl(model)

    return (model, fixed_queens, size)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as f:
            data = f.read()
    else:
        data = sys.stdin.read()

    (model, _, _) = json_to_dsl(data)
    JSONObjectGenerator(
        model=model,
        output_dir="output/",
    ).generate()
