from importlib.resources import files
from pathlib import PurePath
import pandas as pd

from . import data

def load_csv_data(file_name: str) -> pd.DataFrame:

    if not file_name or PurePath(file_name).name != file_name:
        raise ValueError("File name must be a non-empty string and cannot contain path")
    if not file_name.endswith(".csv"):
        raise ValueError("File name must end with .csv")

    resource =files(data).joinpath(file_name)
    if not resource.is_file():
        raise FileNotFoundError(f"File {file_name} not found in data package")

    with resource.open("r", encoding="utf-8-sig", newline="") as f:
        return pd.read_csv(f)