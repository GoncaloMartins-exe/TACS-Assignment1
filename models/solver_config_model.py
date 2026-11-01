from besser.BUML.metamodel.object import ObjectModel
from metamodels.solver_config_metamodel import SolverConfig

# Values used when the JSON config does not set them
DEFAULTS = {"rounds": 0, "shots": 1024, "group_size": 0}

def solver_config_model(**values) -> ObjectModel:
    """Instance of the SolverConfig metamodel: the defaults, overridden by the given values."""
    settings = {**DEFAULTS, **values}
    config = SolverConfig("solver_config").attributes(**settings).build()
    return ObjectModel(name="SolverConfigModel", objects={config})

# Default instance
solver_config = solver_config_model()