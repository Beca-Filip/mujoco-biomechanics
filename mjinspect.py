import mujoco as mj
from mujoco import MjModel
import argparse

mjJointTypeToString = {
    0: "free",
    1: "ball",
    2: "slide",
    3: "hinge",
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect a MuJoCo model")
    parser.add_argument("model_path", help="Path to the MuJoCo model XML file")

    args = parser.parse_args()

    model = mj.MjModel.from_xml_path(args.model_path)
    print_model(model)