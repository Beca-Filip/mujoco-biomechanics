from importlib.resources import files

import pytest

from mujoco_biomechanics_code import data
from mujoco_biomechanics_code.data_loader import read_package_csv


EXPECTED_TABLES = {
    "anthropometric_table_male.csv",
    "anthropometric_table_female.csv",
    "male_shoulder_hip.csv",
    "female_shoulder_hip.csv",
    "site_positions_male.csv",
    "site_positions_female.csv",
}


def test_all_expected_tables_are_packaged() -> None:
    data_root = files(data)
    missing = sorted(name for name in EXPECTED_TABLES if not data_root.joinpath(name).is_file())
    assert not missing, f"Missing packaged CSV files: {missing}"


@pytest.mark.parametrize("file_name", sorted(EXPECTED_TABLES))
def test_every_packaged_table_can_be_loaded(file_name: str) -> None:
    frame = read_package_csv(file_name)
    assert not frame.empty


@pytest.mark.parametrize("bad_name", ["../table.csv", "data/table.csv", "table.txt", ""])
def test_invalid_resource_names_are_rejected(bad_name: str) -> None:
    with pytest.raises(ValueError):
        read_package_csv(bad_name)
