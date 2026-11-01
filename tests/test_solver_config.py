import json

import pytest

from solver_config import load_solver_config


def write(tmp_path, values):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(values))
    return str(path)


def test_defaults_without_file():
    config = load_solver_config()
    assert (config.rounds, config.shots, config.group_size) == (0, 1024, 0)


def test_repository_config_is_valid():
    assert load_solver_config("config/solver_config.json").shots > 0


def test_json_overrides_defaults(tmp_path):
    config = load_solver_config(write(tmp_path, {"rounds": 3, "shots": 200}))
    assert (config.rounds, config.shots, config.group_size) == (3, 200, 0)


@pytest.mark.parametrize("values, violated", [
    ({"shots": 0}, "shots_positive"),
    ({"rounds": -1}, "rounds_not_negative"),
    ({"group_size": -2}, "group_size_not_negative"),
])
def test_ocl_rejects_invalid_values(tmp_path, values, violated):
    with pytest.raises(ValueError, match=violated):
        load_solver_config(write(tmp_path, values))


def test_unknown_setting_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="Unknown"):
        load_solver_config(write(tmp_path, {"shotz": 10}))