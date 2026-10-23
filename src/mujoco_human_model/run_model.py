# Launch MuJoCo viewer for testing XML models

import argparse
import sys
import time
from pathlib import Path
from typing import Sequence

import mujoco
import mujoco.viewer
import numpy as np

def normalise_xml_input_path(model_file: str | Path) -> Path:
    path = Path(model_file)
    if path.suffix == "":
        path = path.with_suffix(".xml")
    elif path.suffix.lower() != ".xml":
        raise ValueError(f"Invalid model file extension: {path.suffix}. Expected .xml")
    return path

def normalise_xml_output_path(file_name: str | Path) -> Path:
    path = Path(output_file)
    if path.suffix == "":
        path = path.with_suffix(".xml")
    elif path.suffix.lower() != ".xml":
        raise ValueError(f"Invalid output file extension: {path.suffix}. Expected .xml")
    return path

def compute_overview_camera(model: mujoco.MjModel, data: mujoco.MjData, distance_scale: float) -> tuple[np.ndarray, float]:
    """Compute camera parameters that frame the entire model."""
    if distance_scale <= 0:
        raise ValueError("distance_scale must be greater than 0")
    
    mujoco.mj_forward(model, data)
    positions = [data.xpos[i].copy() for i in range(model.nbody)]
    positions.extend(data.geom_xpos[i].copy() for i in range(model.ngeom))
    positions_array = np.asarray(positions)

    minimum = np.min(positions_array, axis=0)
    maximum = np.max(positions_array, axis=0)
    center = (minimum + maximum) / 2.0
    extent = np.linalg.norm(maximum - minimum)
    distance = max(extent * distance_scale, 1.0)
    return center, distance

# Build a combined XML string that includes all the provided model files as submodels in a number of columns specified by the user
def build_combined_xml(model_files: Sequence[str | Path], spacing: float=1.5, number_of_columns: int=1) -> str:
    """Combine multiple MuJoCo XML models into a single shared scene with specified spacing and number of columns."""
    
    if not model_files:
        raise ValueError("No model files provided.")
    if spacing <= 0:
        raise ValueError("Spacing must be greater than 0.")
    if number_of_columns < 1:
        raise ValueError("Number of columns must be at least 1.")

    paths = [normalise_xml_input_path(path) for path in model_files]
    missing = [path for path in paths if not path.is_file()]
    if missing:
        missing_text = ", ".join(str(path) for path in missing)
        raise FileNotFoundError(f"Model file(s) not found: {missing_text}")
    
    num_models = len(paths)
    num_rows = (num_models + number_of_columns - 1) // number_of_columns
    max_x = (num_rows - 1) * spacing
    max_y = (min(num_models, number_of_columns) - 1) * spacing
    center_x = max_x / 2.0
    center_y = max_y / 2.0

    base_xml = f"""
    <mujoco model="combined_scene">
        <asset>
            <texture type="skybox" builtin="gradient" rgb1="0.3 0.5 0.7" rgb2="0 0 0" width="32" height="512"/>
            <texture name="grid" type="2d" builtin="checker" width="512" height="512" rgb1="0.1 0.1 0.1" rgb2="0.9 0.9 0.9"/>
            <material  name="grid" texture="grid" texrepeat="1 1" texuniform="true" reflectance="0.2"/>
        </asset>
        <worldbody>
            <geom name="floor" type="plane" pos="{center_x} {center_y} 0" size="100 100 0.1" material="grid"/>
        </worldbody>
    </mujoco>
    """

    parent = mujoco.MjSpec.from_string(base_xml)

    for index, model_path in enumerate(paths):
        child = mujoco.MjSpec.from_file(str(model_path))
        child_floor = child.geom("floor")
        if child_floor is not None:
            child.delete(child_floor)

        column_position = (index % number_of_columns) * spacing
        row_position = (index // number_of_columns) * spacing
        frame = parent.worldbody.add_frame(pos=[row_position, column_position, 0.0])
        parent.attach(child, frame=frame, prefix=f"m{index}_")
    
    parent.compile()
    return parent.to_xml()

def save_combined_scene(xml: str, output_file: str | Path) -> Path:
    output_path = normalise_xml_output_path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(xml, encoding="utf-8")
    return output_path

def set_joint_qpos(model: mujoco.MjModel, data: mujoco.MjData, joint_name: str, qpos_value: float) -> bool:
    joint_id = mujoco.joint_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, joint_name)
    if joint_id < 0:
        return False

    qpos_address = (model.jnt_qposadr[joint_id])
    data.qpos[qpos_address] = qpos_value
    return True

def scene_viewer(combined_xml: str, model_count: int, shoulder_angle: float, paused: bool, cam_azimuth: float, cam_elevation: float, cam_distance_scale: float): -> None:
    model = mujoco.MjModel.from_xml_string(combined_xml)
    data = mujoco.MjData(model)

    for i in range(model_count):
        left_name = f"m{i}_left_shoulder_x"
        right_name = f"m{i}_right_shoulder_x"
        left_set = set_joint_qpos(model, data, left_name, shoulder_angle)
        right_set = set_joint_qpos(model, data, right_name, -shoulder_angle
        if not (left_set and right_set):
            print(f"Warning: Could not set shoulder angles for model {i}. Joint names may not match expected format.")

    mujoco.mj_forward(model, data)
    center, distance = compute_overview_camera(model, data, distance_scale=cam_distance_scale)

    simulation_paused = paused

    def key_callback(keycode: int): -> None:
        nonlocal simulation_paused
        if keycode == 32:  # spacebar toggles pause
            simulation_paused = not simulation_paused

    with mujoco.viewer.launch_passive(model, data, key_callback=key_callback) as viewer:
        with viewer.lock():
            viewer.cam.type = mujoco.mjtCamera.mjCAMERA_FREE
            viewer.cam.lookat[:] = center
            viewer.cam.distance = distance
            viewer.cam.azimuth = cam_azimuth
            viewer.cam.elevation = cam_elevation

        while viewer.is_running():
            step_start = time.time()
            if not simulation_paused:
                mujoco.mj_step(model, data)
            viewer.sync()

            if simulation_paused:
                time.sleep(0.01)
            else:
                remaining_time = model.opt.timestep - (time.time() - step_start)
                if remaining_time > 0:
                    time.sleep(remaining_time)

def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a combined MuJoCo scene from multiple XML files, load and run models and optionally pause and save them.")
    parser.add_argument(
        "model_files",
        nargs="+",
        help="Path to the .xml model file to load",
    )
    parser.add_argument(
        "-o",
        "--output",
        "--file-name",
        "--file_name",
        "-fn",
        dest="output",
        default="scene.xml",
        help="Output scene XML file (default: scene.xml).",
    )
    parser.add_argument(
        "--save-only",
        action="store_true",
        help="Save the combined XML without opening the viewer.",
    )
    parser.add_argument(
        "--pause",
        action="store_true",
        help="Load the models in the viewer without running the simulation (no .xml at the end)",
    )
    parser.add_argument(
        "--spacing", "-s",
        type=float,
        default=1.5,
        help="Spacing between loaded models on the x axis (default: 1.5)"
    )
    parser.add_argument(
        "-sa",
        "--shoulder-angle",
        "--shoulder_angle",
        dest="shoulder_angle",
        type=float,
        default=1.5707963,
        help="Initial shoulder angle in radians (default: T-pose).",
    )
    parser.add_argument(
        "-nc",
        "--number-of-columns",
        "--number_of_columns",
        dest="number_of_columns",
        type=int,
        default=1,
        help="Number of model columns (default: 1).",
    )
    parser.add_argument(
        "-ca",
        "--cam-azimuth",
        type=float,
        default=180.0,
        help="Viewer camera azimuth in degrees (default: 180).",
    )
    parser.add_argument(
        "-ce",
        "--cam-elevation",
        type=float,
        default=-35.0,
        help="Viewer camera elevation in degrees (default: -35).",
    )
    parser.add_argument(
        "-cds",
        "--cam-distance-scale",
        type=float,
        default=2.0,
        help="Viewer camera distance multiplier (default: 2).",
    )
    return parser

def main() -> None:
    args = build_argument_parser().parse_args()
    combined_xml = build_combined_xml(model_files=args.model_files, spacing=args.spacing, number_of_columns=args.number_of_columns)
    output_path = save_combined_scene(combined_xml, args.output)

    if args.save_only:
        return

    scene_viewer(
        combined_xml=combined_xml,
        model_count=len(args.model_files),
        shoulder_angle=args.shoulder_angle,
        paused=args.pause,
        cam_azimuth=args.cam_azimuth,
        cam_elevation=args.cam_elevation,
        cam_distance_scale=args.cam_distance_scale
    )

if __name__ == "__main__":
    main()
