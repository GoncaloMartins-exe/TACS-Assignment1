
from besser.BUML.metamodel.object import ObjectModel
from metamodels.Metamodel_NQueens import Board, Problem, Constraint, ConstraintType, FixedPosition, Queen

################
# OBJECT MODEL #
################
board_obj = Board("Board").attributes(size=4).build()
queens_obj = Problem("Queens").attributes(name="Queens").build()
constraint_1_obj = Constraint("constraint_1").attributes(type=ConstraintType.AT_LEAST_ONE_PER_ROW).build()
constraint_2_obj = Constraint("constraint_2").attributes(type=ConstraintType.AT_MOST_ONE_PER_ROW).build()
constraint_3_obj = Constraint("constraint_3").attributes(type=ConstraintType.AT_MOST_ONE_PER_COLUMN).build()
constraint_4_obj = Constraint("constraint_4").attributes(type=ConstraintType.AT_MOST_ONE_PER_DIAGONAL).build()
fixed_queen_1_obj = FixedPosition("fixed_queen_1").attributes(column=2, row=1).build()
fixed_queen_2_obj = FixedPosition("fixed_queen_2").attributes(column=1, row=3).build()
queen_1_obj = Queen("queen_1").attributes(column=2, row=1).build()
queen_2_obj = Queen("queen_2").attributes(column=1, row=3).build()

# Associations
queens_obj.board = board_obj
queens_obj.constraint = {
    constraint_1_obj,
    constraint_2_obj,
    constraint_3_obj,
    constraint_4_obj
}
board_obj.fixedposition = {
    fixed_queen_1_obj, 
    fixed_queen_2_obj
}
board_obj.queen = {
    queen_1_obj, 
    queen_2_obj
}
board_obj.problem = queens_obj

# Object Model
object_model: ObjectModel = ObjectModel(
    name="Object_Diagram",
    objects={
        board_obj,
        queens_obj,
        constraint_1_obj,
        constraint_2_obj,
        constraint_3_obj,
        constraint_4_obj,
        fixed_queen_1_obj, 
        fixed_queen_2_obj, 
        queen_1_obj, 
        queen_2_obj
    }
)