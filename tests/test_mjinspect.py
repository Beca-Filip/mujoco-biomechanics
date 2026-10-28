import mujoco

from mujoco_biomechanics_code.mjinspect import inspect_model


def test_inspect_model_returns_expected_sections() -> None:
    model = mujoco.MjModel.from_xml_string(
        """
        <mujoco model="test">
          <worldbody>
            <body name="body">
              <joint name="joint" type="hinge"/>
              <geom name="geom" type="sphere" size="0.1"/>
              <site name="site"/>
            </body>
          </worldbody>
        </mujoco>
        """
    )
    output = inspect_model(model)
    assert "Number of bodies:" in output
    assert "joint (type=hinge)" in output
    assert "geom" in output
    assert "site" in output
