import argparse
from pathlib import Path

import mujoco


JOINT_TYPE_NAMES = {
    int(mujoco.mjtJoint.mjJNT_FREE): "free",
    int(mujoco.mjtJoint.mjJNT_BALL): "ball",
    int(mujoco.mjtJoint.mjJNT_SLIDE): "slide",
    int(mujoco.mjtJoint.mjJNT_HINGE): "hinge",
}


def inspect_model(model: mujoco.MjModel) -> str:
    """Return a human-readable summary of a compiled MuJoCo model."""
    lines = [
        f"Number of coordinates: {model.nq}",
        f"Number of bodies: {model.nbody}",
    ]
    lines.extend(f"\tBody {i}: {model.body(i).name}" for i in range(model.nbody))

    lines.append(f"Number of joints: {model.njnt}")
    for i in range(model.njnt):
        joint_type = JOINT_TYPE_NAMES.get(int(model.jnt_type[i]), "unknown")
        lines.append(f"\tJoint {i}: {model.joint(i).name} (type={joint_type})")

    lines.append(f"Number of geometries: {model.ngeom}")
    lines.extend(f"\tGeom {i}: {model.geom(i).name}" for i in range(model.ngeom))

    lines.append(f"Number of sites: {model.nsite}")
    lines.extend(f"\tSite {i}: {model.site(i).name}" for i in range(model.nsite))

    return "\n".join(lines)


def print_model(model: mujoco.MjModel) -> None:
    """Print the model summary to standard output."""
    print(inspect_model(model))


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect a MuJoCo XML model.")
    parser.add_argument("model_path", type=Path, help="Path to a MuJoCo XML file.")
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    model_path = args.model_path
    if not model_path.is_file():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    model = mujoco.MjModel.from_xml_path(str(model_path))
    print_model(model)


if __name__ == "__main__":
    main()
