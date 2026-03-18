# Launch MuJoCo viewer for testing XML models

import argparse
import time

import mujoco
import mujoco.viewer
import numpy as np


def compute_overview_camera(model, data, distance_scale):
    """Compute camera parameters that frame the entire model."""
    mujoco.mj_forward(model, data)

    # Collect all body and geom positions
    positions = []
    for i in range(model.nbody):
        positions.append(data.xpos[i].copy())
    for i in range(model.ngeom):
        positions.append(data.geom_xpos[i].copy())

    positions = np.array(positions)

    # Center the camera on the midpoint of all positions
    center = (positions.min(axis=0) + positions.max(axis=0)) / 2.0

    # Distance: enough to see the full extent of the model
    extent = np.linalg.norm(positions.max(axis=0) - positions.min(axis=0))
    distance = max(extent * distance_scale, 1.0)

    return center, distance

# Build a combined XML string that includes all the provided model files as submodels
def build_combined_xml(model_names, spacing):
    asset_models = []
    attached_models = []

    for i, name in enumerate(model_names):
        submodel_name = f"sub{i}"
        prefix = f"m{i}_"

        asset_models.append(
            f'<model name="{submodel_name}" file="{name}.xml"/>'
        )

        attached_models.append(f"""
        <frame pos="{i * spacing} 0 0">
            <attach model="{submodel_name}" prefix="{prefix}"/>
        </frame>
        """)

    return f"""
    <mujoco model="combined_scene">
        <asset>
            {''.join(asset_models)}
        </asset>
        <worldbody>
            {''.join(attached_models)}
        </worldbody>
    </mujoco>
    """

def main():
    parser = argparse.ArgumentParser(description="Load and run MuJoCo XML model.")
    parser.add_argument("model_files", nargs="+", help="Path to the .xml model file to load")
    parser.add_argument(
        "--pause",
        action="store_true",
        help="Load the models in the viewer without running the simulation",
    )
    parser.add_argument(
        "--spacing", "-s",
        type=float,
        default=1.5,
        help="Spacing between loaded models on the x axis (default: 3)"
    )
    parser.add_argument(
        "--cam-azimuth", "-ca",
        type=float,
        default=180.,
        help="Azimuth of the viewer's camera (default: 0 degrees)"
    )
    parser.add_argument(
        "--cam-elevation", "-ce",
        type=float,
        default=-35.,
        help="Elevation of the viewer's camera (default: -35 degrees)"
    )
    parser.add_argument(
        "--cam-distance-scale", "-cds",
        type=float,
        default=2.,
        help="Distance scaling of the viewer's camera (default: 2; scaling=1 whole mesh is barely seen)"
    )
    args = parser.parse_args()

    combined_xml = build_combined_xml(args.model_files, args.spacing)

    model = mujoco.MjModel.from_xml_string(combined_xml)
    data = mujoco.MjData(model)

    # Set initial joint positions for the shoulders so that all models are in a T-pose
    for i, _ in enumerate(args.model_files):
        left_name = f"m{i}_left_shoulder_x"
        right_name = f"m{i}_right_shoulder_x"

        data.joint(left_name).qpos[0] = 1.5707963
        data.joint(right_name).qpos[0] = -1.5707963

    mujoco.mj_forward(model, data)

    # Compute a camera that sees the whole model
    center, distance = compute_overview_camera(model, data, distance_scale=args.cam_distance_scale)

    paused = args.pause

    def key_callback(keycode):
        nonlocal paused
        if keycode == 32:  # spacebar toggles pause
            paused = not paused

    # Launch the passive viewer and configure the camera via its handle
    with mujoco.viewer.launch_passive(
        model, data, key_callback=key_callback
    ) as viewer:
        with viewer.lock():
            viewer.cam.type = mujoco.mjtCamera.mjCAMERA_FREE
            viewer.cam.lookat[:] = center
            viewer.cam.distance = distance
            viewer.cam.azimuth = args.cam_azimuth
            viewer.cam.elevation = args.cam_elevation

        # Simulation loop
        while viewer.is_running():
            if not paused:
                mujoco.mj_step(model, data)
            viewer.sync()
            time.sleep(model.opt.timestep)


if __name__ == "__main__":
    main()
