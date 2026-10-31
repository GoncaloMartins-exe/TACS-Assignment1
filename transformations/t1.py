import json
from metamodels.cnf_metamodel import Board, Conjunction, Disjunction, Literal
from besser.BUML.metamodel.object import ObjectModel

def pos_is_valid(row, col, queens):
    for queen in queens:
        if row == queen.row or col == queen.column or abs(row - queen.row) == abs(col - queen.column):
            return False
    return True

def dont_print(*values, end = None):
    return

def t1(problem: ObjectModel, debug: bool = False) -> ObjectModel:
    debug = print if debug else dont_print

    for obj in problem.objects:
        if obj.classifier.name == "Board":
            size = obj.size
            break
    queens = [obj for obj in problem.objects if obj.classifier.name == "Queen"]
    valid_positions = [(row, col) for row in range(1, size+1) for col in range(1, size+1) if pos_is_valid(row, col, queens)]

    debug(f"Possible positions: {valid_positions}")

    board = Board(f"board_{size}x{size}").attributes(size=size).build()
    conjunction = Conjunction("conj_1").build()

    disjunctions = set()
    def new_disj(disjunctions: set[Disjunction]) -> Disjunction:
        d = Disjunction(f"disj_{len(disjunctions)+1}").build()
        disjunctions.add(d)
        return d

    all_literals = set() # to keep track of number of literals and to build ObjectModel
    def new_literal(literals: list[Literal], row: int, col: int, queen: bool, all_literals: set[Literal]) -> Literal:
        l = Literal(f"literal_{len(all_literals)+1}").attributes(row=row, column=col, queen=queen).build()
        literals.append(l)
        all_literals.add(l)
        return l

    def all_pairs(positions: list[tuple[int, int]], disjunctions: set[Disjunction], all_literals: set[Literal]) -> set[Disjunction]:
        # disjunctions = set()
        for i in range(len(positions) - 1):
            for j in range(i+1, len(positions)):
                (p1, p2) = (positions[i], positions[j])
                debug(f" AND (!{p1} OR !{p2})", end="")
                literals = []
                disj = new_disj(disjunctions)
                l1 = new_literal(literals, p1[0], p1[1], False, all_literals)
                l2 = new_literal(literals, p2[0], p2[1], False, all_literals)
                disj.literal = set(literals)
                disjunctions.add(disj)
        return disjunctions

    # Exactly one queen per row
    debug("Exactly one per row:")
    for i in range(1, size+1):
        row_positions = [(row, col) for (row, col) in valid_positions if row == i]
        if len(row_positions) == 0:
            continue

        # At least one per row
        at_least_one_per_row = new_disj(disjunctions)
        literals = []
        debug("AND (", end="")
        first_iter = True
        for (row, col) in row_positions:
            l = new_literal(literals, row, col, True, all_literals)
            debug(f"{'' if first_iter else ' OR '}{row, col}", end="")
            first_iter = False
        debug(")")
        at_least_one_per_row.literal = set(literals)

        # At most one per row
        all_pairs(row_positions, disjunctions, all_literals)
        debug()

    debug()

    # At most one per column
    debug("At most one per column:")
    for i in range(1, size+1):
        col_positions = [(row, col) for (row, col) in valid_positions if col == i]
        if len(col_positions) == 0:
            continue
        all_pairs(col_positions, disjunctions, all_literals)
        debug()

    debug()

    # At most one per diagonal
    for i in range(1, size):
        # Diagonal in the upper triangle (+ main diagonal)
        upper_triangle = [(col-i+1, col) for col in range(i, size+1)]
        debug(f"Upper Triangle {upper_triangle}:")
        all_pairs([p for p in upper_triangle if p in valid_positions], disjunctions, all_literals)
        debug()

        # Diagonal in the upper anti-triangle (+ anti-diagonal)
        upper_anti_triangle = [(size-j+i, j) for j in range(i, size+1)]
        debug(f"Upper Anti-Triangle {upper_anti_triangle}:")
        all_pairs([p for p in upper_anti_triangle if p in valid_positions], disjunctions, all_literals)
        debug()

        # Don't repeat main/anti diagonal
        if i == 1:
            continue

        # Diagonal in the lower triangle
        lower_triangle = [(row, row-i+1) for row in range(i, size+1)]
        debug(f"Lower Triangle {lower_triangle}:")
        all_pairs([p for p in lower_triangle if p in valid_positions], disjunctions, all_literals)
        debug()

        # Diagonal in the lower anti-triangle
        lower_anti_triangle = [(j, size-j+i) for j in range(i, size+1)]
        debug(f"Lower Anti-Triangle {lower_anti_triangle}:")
        all_pairs([p for p in lower_anti_triangle if p in valid_positions], disjunctions, all_literals)
        debug()

    conjunction.disjunction = disjunctions
    return ObjectModel(
        name="CNF",
        objects={board, conjunction}.union(disjunctions).union(all_literals),
    )
