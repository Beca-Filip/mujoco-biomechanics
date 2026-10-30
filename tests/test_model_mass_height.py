from pathlib import Path

import mujoco
import numpy as np
import pytest

from mujoco_biomechanics.generate_human_model import generate_human_model

# Vary mass and height independently to catch accidental coupling of the scales.
pytestmark = [
    pytest.mark.parametrize("sex", ["male", "female"]),
    pytest.mark.parametrize("mass", [50.0, 75.0, 100.0]),
    pytest.mark.parametrize("height", [1.50, 1.75, 2.00]),
]

@pytest.fixture
def model(tmp_path: Path, sex: str, mass: float, height: float) -> mujoco.MjModel:
    output = generate_human_model(filename=tmp_path / f"{sex}_model.xml", mass=mass, height=height, sex=sex)
    return mujoco.MjModel.from_xml_path(output)

def test_total_model_mass_equals_input_mass(model: mujoco.MjModel, mass: float) -> None:
    total_mass = float(model.body_mass.sum())
    assert total_mass == pytest.approx(mass, rel=0, abs=1e-9), (
        f"Compiled model mass is {total_mass:.9f} kg; expected {mass:.9f} kg"
    )

def test_default_standing_height_matches_input_height(model: mujoco.MjModel, height: float) -> None:
    data = mujoco.MjData(model)
    mujoco.mj_resetData(model, data)
    mujoco.mj_forward(model, data)

    lower_bounds = []
    upper_bounds = []
    for geom_id in np.flatnonzero(model.geom_bodyid != 0):
        geom_type = model.geom_type[geom_id]
        size = model.geom_size[geom_id]
        rotation = data.geom_xmat[geom_id].reshape(3, 3)

        if geom_type == mujoco.mjtGeom.mjGEOM_SPHERE:
            half_height = size[0]
        elif geom_type == mujoco.mjtGeom.mjGEOM_CAPSULE:
            half_height = size[0] + size[1] * abs(rotation[2, 2])
        elif geom_type == mujoco.mjtGeom.mjGEOM_BOX:
            half_height = np.abs(rotation[2]) @ size
        else:
            pytest.fail(f"Height measurement does not support geom type {geom_type}")

        center_z = data.geom_xpos[geom_id, 2]
        lower_bounds.append(float(center_z - half_height))
        upper_bounds.append(float(center_z + half_height))

    standing_height = max(upper_bounds) - min(lower_bounds)
    assert standing_height == pytest.approx(height, rel=0, abs=0.03), (
        f"Default standing height is {standing_height:.6f} m; "
        f"expected {height:.6f} m within 0.03 m"
    )
