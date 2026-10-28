from pathlib import Path

import mujoco
import pytest

from mujoco_biomechanics_code.run_model import (
    build_combined_xml,
    normalise_xml_input_path,
    save_combined_scene,
)


SIMPLE_MODEL = """
<mujoco model="simple">
  <worldbody>
    <geom name="floor" type="plane" size="1 1 0.1"/>
    <body name="body" pos="0 0 1">
      <joint name="hinge" type="hinge"/>
      <geom name="ball" type="sphere" size="0.1"/>
    </body>
  </worldbody>
</mujoco>
"""


def test_build_combined_xml_and_save(tmp_path: Path) -> None:
    first = tmp_path / "first.xml"
    second = tmp_path / "second.xml"
    first.write_text(SIMPLE_MODEL, encoding="utf-8")
    second.write_text(SIMPLE_MODEL, encoding="utf-8")

    xml = build_combined_xml([first, second], spacing=1.5, number_of_columns=2)
    compiled = mujoco.MjModel.from_xml_string(xml)
    assert compiled.nbody >= 3
    assert compiled.geom("floor").id >= 0
    assert compiled.geom("m0_floor") is None
    assert compiled.geom("m1_floor") is None

    output = save_combined_scene(xml, tmp_path / "scene")
    assert output.name == "scene.xml"
    assert output.is_file()


def test_missing_model_is_reported(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        build_combined_xml([tmp_path / "missing.xml"])


def test_extension_is_added_only_when_missing() -> None:
    assert normalise_xml_input_path("model").name == "model.xml"
    with pytest.raises(ValueError):
        normalise_xml_input_path("model.txt")
