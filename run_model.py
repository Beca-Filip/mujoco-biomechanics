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


def main():
    parser = argparse.ArgumentParser(description="Load and run a MuJoCo XML model.")
    parser.add_argument("model_file", help="Path to the .xml model file to load")
    parser.add_argument(
        "--pause",
        action="store_true",
        help="Load the model in the viewer without running the simulation",
    )
    parser.add_argument(
        "--cam-azimuth", "-ca",
        type=float,
        default=0.,
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

    model = mujoco.MjModel.from_xml_path(args.model_file)
    data = mujoco.MjData(model)

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
