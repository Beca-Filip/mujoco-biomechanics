from pathlib import Path

import mujoco
import pytest

from mujoco_biomechanics.generate_human_model import generate_human_model


@pytest.mark.parametrize(
    ("sex", "mass", "height"),
    [("male", 75.0, 1.82), ("female", 60.0, 1.68)],
)
def test_generate_model_creates_compilable_xml(tmp_path: Path, sex: str, mass: float, height: float) -> None:
    output = Path(
        generate_human_model( filename=tmp_path / f"{sex}_model.xml", mass=mass, height=height, sex=sex)
    )
    assert output.suffix == ".xml"
    assert output.is_file()

    model = mujoco.MjModel.from_xml_path(str(output))
    assert model.nbody > 1
    assert model.njnt > 0
    assert model.nsite > 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"mass": 0.0, "height": 1.8, "sex": "male", "alpha": 1.0},
        {"mass": 75.0, "height": 0.0, "sex": "male", "alpha": 1.0},
        {"mass": 75.0, "height": 1.8, "sex": "invalid", "alpha": 1.0},
        {"mass": 75.0, "height": 1.8, "sex": "male", "alpha": 1.1},
    ],
)
def test_invalid_generation_inputs_raise(tmp_path: Path, kwargs: dict) -> None:
    with pytest.raises(ValueError):
        generate_human_model(filename=tmp_path / "invalid.xml", **kwargs)
