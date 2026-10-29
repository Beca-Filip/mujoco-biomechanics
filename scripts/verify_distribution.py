import sys
import tarfile
import zipfile
from pathlib import Path


EXPECTED_CSV = {
    "anthropometric_table_male.csv",
    "anthropometric_table_female.csv",
    "male_shoulder_hip.csv",
    "female_shoulder_hip.csv",
    "site_positions_male.csv",
    "site_positions_female.csv",
}


def verify_wheel(path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
    missing = [
        name
        for name in EXPECTED_CSV
        if f"mujoco_biomechanics/data/{name}" not in names
    ]
    if missing:
        raise SystemExit(f"{path.name}: missing CSV files: {missing}")
    print(f"OK: {path.name}")


def verify_sdist(path: Path) -> None:
    with tarfile.open(path, "r:gz") as archive:
        names = set(archive.getnames())
    missing = [
        name
        for name in EXPECTED_CSV
        if not any(item.endswith(f"/src/mujoco_biomechanics/data/{name}") for item in names)
    ]
    if missing:
        raise SystemExit(f"{path.name}: missing CSV files: {missing}")
    print(f"OK: {path.name}")


def main() -> None:
    dist_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    wheels = sorted(dist_dir.glob("*.whl"))
    sdists = sorted(dist_dir.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise SystemExit(
            f"Expected exactly one wheel and one sdist in {dist_dir}; "
            f"found {len(wheels)} wheel(s) and {len(sdists)} sdist(s)."
        )
    verify_wheel(wheels[0])
    verify_sdist(sdists[0])


if __name__ == "__main__":
    main()
