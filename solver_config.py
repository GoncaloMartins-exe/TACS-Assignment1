import json
import re
from pathlib import Path
from types import SimpleNamespace

from besser.BUML.metamodel.structural import Constraint
from bocl.OCLWrapper import OCLWrapper
from metamodels.solver_config_metamodel import SolverConfig, domain_model
from models.solver_config_model import DEFAULTS, solver_config_model

OCL_FILE = "ocl/solver_config.ocl"


def read_constraints(path: str = OCL_FILE) -> list[Constraint]:
    """One Constraint per 'context <Class> inv <name>: <expression>' block of the OCL file."""
    text = Path(path).read_text()
    blocks = re.split(r"(?m)^(?=context\s)", text)
    constraints = []
    for block in filter(str.strip, blocks):
        name = re.match(r"context\s+\w+\s+inv\s+(\w+)\s*:", block).group(1)
        constraints.append(Constraint(name=name, context=SolverConfig, expression=block.strip(), language="OCL"))
    return constraints


def load_solver_config(path: str | None = None) -> SimpleNamespace:
    """Settings from the JSON file (the defaults if there is no file), validated with the OCL file."""
    values = json.loads(Path(path).read_text()) if path else {}
    unknown = set(values) - set(DEFAULTS)
    if unknown:
        raise ValueError(f"Unknown solver setting(s) {sorted(unknown)}, expected {sorted(DEFAULTS)}")

    model = solver_config_model(**values)
    wrapper = OCLWrapper(domain_model, model)
    violated = [c.name for c in read_constraints() if wrapper.evaluate(c) is not True]
    if violated:
        raise ValueError(f"Invalid solver config {path}: violates {', '.join(violated)} (see {OCL_FILE})")
    return SimpleNamespace(**{**DEFAULTS, **values})