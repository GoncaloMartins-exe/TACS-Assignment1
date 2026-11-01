####################
# STRUCTURAL MODEL #
####################

from besser.BUML.metamodel.structural import (
    Class, Property, DomainModel, IntegerType
)

# Classes
SolverConfig = Class(name="SolverConfig")


SolverConfig_rounds: Property = Property(name="rounds", type=IntegerType)
SolverConfig_shots: Property = Property(name="shots", type=IntegerType)
SolverConfig_group_size: Property = Property(name="group_size", type=IntegerType)

SolverConfig.attributes={SolverConfig_group_size, SolverConfig_rounds, SolverConfig_shots}


domain_model = DomainModel(
    name="Solver_Config_Diagram",
    types={SolverConfig},
    associations=set(),
    generalizations=set(),
    metadata=None
)