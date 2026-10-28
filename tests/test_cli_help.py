import subprocess
import sys

import pytest


@pytest.mark.parametrize(
    "module",
    [
        "mujoco_biomechanics_code.generate_human_model",
        "mujoco_biomechanics_code.mjinspect",
        "mujoco_biomechanics_code.run_model",
    ],
)
def test_module_help(module: str) -> None:
    result = subprocess.run(
        [sys.executable, "-m", module, "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "usage:" in result.stdout.lower()
