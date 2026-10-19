from besser.BUML.metamodel.object import ObjectModel
from metamodels.cnf_metamodel import Board, Conjunction, Disjunction, Literal

################
# OBJECT MODEL #
################
and_1_obj = Conjunction("and_1").build()
board_1_obj = Board("board_1").attributes(size=4).build()
literal_1_obj = Literal("literal_1").attributes(queen=True, row=1, column=2).build()
literal_2_obj = Literal("literal_2").attributes(queen=True, row=2, column=4).build()
literal_3_obj = Literal("literal_3").attributes(queen=True, row=3, column=1).build()
literal_4_obj = Literal("literal_4").attributes(queen=True, row=4, column=3).build()
or_1_obj = Disjunction("or_1").build()
or_2_obj = Disjunction("or_2").build()
or_3_obj = Disjunction("or_3").build()
or_4_obj = Disjunction("or_4").build()

board_1_obj.conjunction = and_1_obj
and_1_obj.disjunction = {or_1_obj, or_2_obj, or_3_obj, or_4_obj}
or_2_obj.literal = literal_2_obj
or_4_obj.literal = literal_4_obj
or_3_obj.literal = literal_3_obj
or_1_obj.literal = literal_1_obj

# Object Model instance
object_model: ObjectModel = ObjectModel(
    name="Object_Diagram",
    objects={and_1_obj, board_1_obj, literal_1_obj, literal_2_obj, literal_3_obj, literal_4_obj, or_1_obj, or_2_obj, or_3_obj, or_4_obj}
)
