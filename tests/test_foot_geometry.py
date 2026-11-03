from pathlib import Path
import xml.etree.ElementTree as ET

import mujoco
import pytest

from mujoco_biomechanics.generate_human_model import generate_human_model


@pytest.mark.parametrize("sex", ["male", "female"])
@pytest.mark.parametrize("height", [1.5, 2.0])
def test_foot_primitives(tmp_path: Path, sex: str, height: float) -> None:
    path = generate_human_model(tmp_path / "human.xml", 75, height, sex)
    assert ET.parse(path).getroot().find("asset") is None
    model = mujoco.MjModel.from_xml_path(path)

    for side in ("left", "right"):
        body_id = model.body(f"{side}_foot").id
        geoms = [model.geom(f"{side}_foot_{part}") for part in ("heel", "main", "forefoot", "toes")]
        heel = geoms[0]
        forefoot = geoms[2]
        toes = model.geom(f"{side}_foot_toes")
        assert model.body_geomnum[body_id] == 4
        for geom in geoms:
            assert model.geom_type[geom.id] in (mujoco.mjtGeom.mjGEOM_BOX, mujoco.mjtGeom.mjGEOM_ELLIPSOID)
            assert model.geom_bodyid[geom.id] == body_id

        site_x = model.site_pos[model.site_bodyid == body_id, 0]
        assert min(geom.pos[0] - geom.size[0] for geom in geoms) == pytest.approx(site_x.min())
        assert max(geom.pos[0] + geom.size[0] for geom in geoms) == pytest.approx(site_x.max())
        assert forefoot.pos[0] + forefoot.size[0] > toes.pos[0] - toes.size[0]
        assert heel.pos[1] - heel.size[1] == pytest.approx(toes.pos[1] - toes.size[1])
        assert toes.size[1] < heel.size[1]
