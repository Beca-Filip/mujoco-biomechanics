import mujoco as mj
from mujoco import MjModel
import argparse
from pathlib import Path

mjJointTypeToString = {
    int(mj.mjtJoint.mjJNT_FREE): "free",
    int(mj.mjtJoint.mjJNT_BALL): "ball",
    int(mj.mjtJoint.mjJNT_SLIDE): "slide",
    int(mj.mjtJoint.mjJNT_HINGE): "hinge",
}

def print_model(model: MjModel) -> None:
    # print("Model name:", model.name)
    print("Number of coordinates:", model.nq)
    print("Number of bodies:", model.nbody)
    for i in range(model.nbody):
        print(f"\tBody {i}: {model.body(i).name}")
    print("Number of joints:", model.njnt)
    for i in range(model.njnt):
        print(f"\tJoint {i}: {model.joint(i).name} (type={mjJointTypeToString.get(model.jnt_type[i], 'unknown')})")
    print("Number of geometries:", model.ngeom)
    for i in range(model.ngeom):
        print(f"\tGeom {i}: {model.geom(i).name}")
    print("Number of sites:", model.nsite)
    for i in range(model.nsite):
        print(f"\tSite {i}: {model.site(i).name}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect a MuJoCo model")
    parser.add_argument(
        "model_path",
        help="Path to the MuJoCo model XML file"
    )

    args = parser.parse_args()

    model_path = Path(args.model_path)
    if not model_path.is_file():
        parser.error(
            f"Model file does not exist: {model_path}"
        )

    model = mj.MjModel.from_xml_path(args.model_path)
    print_model(model)

if __name__ == "__main__":
    main()