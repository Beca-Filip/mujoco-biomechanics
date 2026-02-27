import pandas as pd
import xml.etree.ElementTree as ET
import argparse

def generate_human_model(filename : str, mass : float, height : float, sex : str):

    k = 1  # scaling coefficient - will be changed depending on subject height
    male_height = 177
    female_height = 161
    if sex == "male":
        sheet_name = 0
        k = float(k / male_height)
        rgba_in = "0.2 0.4 0.8 1"
    elif sex == "female":
        sheet_name = 1
        k = float(k / female_height)
        rgba_in = "0.9 0.4 0.6 1"

    df = pd.read_excel("AnthropometricTableComplete.xlsx", sheet_name=sheet_name)
    k = k * float(height)

    # First column is segment names, second column is lengths
    segments = df.iloc[:, 0]
    lengths = df.iloc[:, 1] * k   # scale values
    segment_mass_percentages = df.iloc[:, 2]
    segment_com_x = df.iloc[:, 3]
    segment_com_y = df.iloc[:, 4]
    segment_com_z = df.iloc[:, 5]

    # Calculate segment masses based on mass percentage and total user mass
    segment_masses = (segment_mass_percentages / 100) * float(mass)

    # Create dicts
    lengths_dict = dict(zip(segments, lengths))
    mass_dict = dict(zip(segments, segment_masses))
    segment_com_x_dict = dict(zip(segments, segment_com_x))
    segment_com_y_dict = dict(zip(segments, segment_com_y))
    segment_com_z_dict = dict(zip(segments, segment_com_z))

    # Local center of mass position dicts
    com_pos_x_dict = {}
    for i in lengths_dict:
        length_x = lengths_dict[i]
        fraction_x = float(segment_com_x_dict[i])
        # length percentage -> actual length -> local offset
        position_x = fraction_x * length_x
        com_pos_x_dict[i] = position_x

    com_pos_y_dict = {}
    for i in lengths_dict:
        length_y = lengths_dict[i]
        fraction_y = float(segment_com_y_dict[i])
        # length percentage -> actual length -> local offset
        position_y = fraction_y * length_y
        com_pos_y_dict[i] = position_y

    com_pos_z_dict = {}
    for i in lengths_dict:
        length_z = lengths_dict[i]
        fraction_z = float(segment_com_z_dict[i])
        # length percentage -> actual length -> local offset
        position_z = fraction_z * length_z
        com_pos_z_dict[i] = position_z


    print("lengths ", lengths_dict)
    print("masses ", mass_dict)
    print("x ", com_pos_x_dict)
    print("y ", com_pos_y_dict)
    print("z ", com_pos_z_dict)

    mujoco = ET.Element("mujoco", model=filename.replace(".xml", ""))
    worldbody = ET.SubElement(mujoco, "worldbody")
    ET.SubElement(worldbody, "geom", type="plane", size="1 1 .1", rgba=".8 .8 .8 1")
    ET.SubElement(worldbody, "light", diffuse=".8 .8 .8", pos="0 0 3", dir="0 0 -1")
    ET.SubElement(mujoco, "option", gravity="0 0 -9.81")


    # Thorax as central segment
    thorax = ET.SubElement(worldbody, "body", name="thorax", pos=f"0 0 {height*0.01-lengths_dict['Head with Neck'] + 0.2}", euler="90 0 0")
    ET.SubElement(thorax, "joint", type="free", pos="0 0 0")
    ET.SubElement(thorax, "geom", type="capsule", size=f"{0.55*lengths_dict['Thorax']/2} {height*0.07*0.01}", pos=f"0 -{0.55*lengths_dict['Thorax']/2} 0", euler="0 0 0", rgba=rgba_in)
    ET.SubElement(thorax, "geom", type="capsule", size=f"{0.45*lengths_dict['Thorax']/2} {height*0.07*0.01}", pos=f"0 -{0.55*lengths_dict['Thorax']+0.45*lengths_dict['Thorax']/2} 0", euler="0 0 0", rgba=rgba_in)

    # Head
    head = ET.SubElement(thorax, "body", name="head", pos="0 0 0")
    ET.SubElement(head, "joint", name="head_x", type="hinge", axis="1 0 0", pos="0 0 0", range="-45 45")
    ET.SubElement(head, "joint", name="head_y", type="hinge", axis="0 1 0", pos="0 0 0", range="-80 80")
    ET.SubElement(head, "joint", name="head_z", type="hinge", axis="0 0 1", pos="0 0 0", range="-60 75")
    ET.SubElement(head, "geom", type="sphere", size=f"{lengths_dict['Head with Neck']/2}", pos=f"0 {lengths_dict['Head with Neck']/2} 0", euler="0 0 0", rgba=rgba_in)

    # Abdomen
    abdomen = ET.SubElement(thorax, "body", name="abdomen", pos=f"0 {-lengths_dict['Thorax']} 0")
    ET.SubElement(abdomen, "joint", name="abdomen_x", type="hinge", axis="1 0 0", pos="0 0 0", range="-12.5 12.5")
    ET.SubElement(abdomen, "joint", name="abdomen_y", type="hinge", axis="0 1 0", pos="0 0 0", range="-15 15")
    ET.SubElement(abdomen, "joint", name="abdomen_z", type="hinge", axis="0 0 1", pos="0 0 0", range="-25 12.5")
    ET.SubElement(abdomen, "geom", type="capsule", size=f"{lengths_dict['Abdomen']/2} {height*0.01*0.067}", pos=f"0 -0.1 0", euler="0 0 0", rgba=rgba_in)

    # Pelvis
    pelvis = ET.SubElement(abdomen, "body", name="pelvis", pos=f"0 {-lengths_dict['Abdomen']} 0")
    ET.SubElement(pelvis, "joint", name="pelvis_x", type="hinge", axis="1 0 0", pos="0 0 0", range="-12.5 12.5")
    ET.SubElement(pelvis, "joint", name="pelvis_y", type="hinge", axis="0 1 0", pos="0 0 0", range="-15 15")
    ET.SubElement(pelvis, "joint", name="pelvis_z", type="hinge", axis="0 0 1", pos="0 0 0", range="-25 12.5")
    ET.SubElement(pelvis, "geom", type="capsule", size=f"{lengths_dict['Pelvis']/2} {height*0.01*0.085}", pos=f"0 -0.1 0", euler="0 0 0", rgba=rgba_in)

    # Left thigh
    left_thigh = ET.SubElement(pelvis, "body", name="left_thigh", pos=f"0 {-lengths_dict['Pelvis']} {-height*0.01*0.09 + height*0.01*0.02}")
    ET.SubElement(left_thigh, "joint", name="left_hip_x", type="hinge", axis="1 0 0", pos="0 0 0", range="-20 40")
    ET.SubElement(left_thigh, "joint", name="left_hip_y", type="hinge", axis="0 1 0", pos="0 0 0", range="-40 50")
    ET.SubElement(left_thigh, "joint", name="left_hip_z", type="hinge", axis="0 0 1", pos="0 0 0", range="-30 100")
    ET.SubElement(left_thigh, "geom", type="capsule", size=f"{height*0.01*0.04} {lengths_dict['Thigh']/2}", pos = f"0 {-lengths_dict['Thigh']/2 - height*0.01*0.02} 0", euler="-90 0 0", rgba=rgba_in)

    # Right thigh
    right_thigh = ET.SubElement(pelvis, "body", name="right_thigh", pos=f"0 {-lengths_dict['Pelvis']} {height*0.01*0.09 - height*0.01*0.02}")
    ET.SubElement(right_thigh, "joint", name="right_hip_x", type="hinge", axis="1 0 0", pos="0 0 0", range="-40 20")
    ET.SubElement(right_thigh, "joint", name="right_hip_y", type="hinge", axis="0 1 0", pos="0 0 0", range="-40 50")
    ET.SubElement(right_thigh, "joint", name="right_hip_z", type="hinge", axis="0 0 1", pos="0 0 0", range="-30 100")
    ET.SubElement(right_thigh, "geom", type="capsule", size=f"{height*0.01*0.04} {lengths_dict['Thigh']/2}", pos = f"0 {-lengths_dict['Thigh']/2 - height*0.01*0.02} 0", euler="-90 0 0", rgba=rgba_in)

    # Left shank
    left_shank = ET.SubElement(left_thigh, "body", name="left_shank", pos=f"0 {-lengths_dict['Thigh']} 0")
    ET.SubElement(left_shank, "joint", name="left_knee_z", type="hinge", axis="0 0 1", pos="0 0 0", range="-150 0")
    ET.SubElement(left_shank, "geom", type="capsule", size=f"{height*0.01*0.03} {lengths_dict['Shank']/2}", pos = f"0 {-lengths_dict['Shank']/2} 0", euler="-90 0 0", rgba=rgba_in)

    # Right shank
    right_shank = ET.SubElement(right_thigh, "body", name="right_shank", pos=f"0 {-lengths_dict['Thigh']} 0")
    ET.SubElement(right_shank, "joint", name="right_knee_z", type="hinge", axis="0 0 1", pos="0 0 0", range="-150 0")
    ET.SubElement(right_shank, "geom", type="capsule", size=f"{height*0.01*0.03} {lengths_dict['Shank']/2}", pos = f"0 {-lengths_dict['Shank']/2} 0", euler="-90 0 0", rgba=rgba_in)

    # Left foot
    left_foot = ET.SubElement(left_shank, "body", name="left_foot", pos=f"0 {-lengths_dict['Shank']} 0")
    ET.SubElement(left_foot, "joint", name="left_ankle_y", type="hinge", axis="0 1 0", pos="0 0 0", range="-30 30")
    ET.SubElement(left_foot, "joint", name="left_ankle_z", type="hinge", axis="0 0 1", pos="0 0 0", range="-20 30")
    ET.SubElement(left_foot, "geom", type="capsule", size=f"0.05 {lengths_dict['Foot']/2}", pos = f"{lengths_dict['Foot']/2} 0 0", euler="0 90 0", rgba=rgba_in)

    # Right foot
    right_foot = ET.SubElement(right_shank, "body", name="right_foot", pos=f"0 {-lengths_dict['Shank']} 0")
    ET.SubElement(right_foot, "joint", name="right_ankle_y", type="hinge", axis="0 1 0", pos="0 0 0", range="-30 30")
    ET.SubElement(right_foot, "joint", name="right_ankle_z", type="hinge", axis="0 0 1", pos="0 0 0", range="-20 30")
    ET.SubElement(right_foot, "geom", type="capsule", size=f"0.05 {lengths_dict['Foot']/2}", pos = f"{lengths_dict['Foot']/2} 0 0", euler="0 90 0", rgba=rgba_in)

    # Left upper arm
    left_upper_arm = ET.SubElement(thorax, "body", name="left_upper_arm", pos=f"0 -{0.55*lengths_dict['Thorax']/2} -{height*0.01*0.07 + height*0.01*0.0208 + 0.55*lengths_dict['Thorax']/2}")
    ET.SubElement(left_upper_arm, "joint", name="left_shoulder_x", type="hinge", axis="1 0 0", pos=f"0 {height*0.01*0.0208} 0", range="-50 180")
    ET.SubElement(left_upper_arm, "joint", name="left_shoulder_y", type="hinge", axis="0 1 0", pos=f"0 {height*0.01*0.0208} 0", range="-90 90")
    ET.SubElement(left_upper_arm, "joint", name="left_shoulder_z", type="hinge", axis="0 0 1", pos=f"0 {height*0.01*0.0208} 0", range="-50 180")
    ET.SubElement(left_upper_arm, "geom", type="capsule", size=f"{height*0.01*0.0208} {lengths_dict['Upper Arm']/2}", pos = f"0 {-lengths_dict['Upper Arm']/2 + height*0.01*0.0208} 0", euler="-90 0 0", rgba=rgba_in)

    # Right upper arm
    right_upper_arm = ET.SubElement(thorax, "body", name="right_upper_arm", pos=f"0 -{0.55*lengths_dict['Thorax']/2} {height*0.01*0.07 + height*0.01*0.0208 + 0.55*lengths_dict['Thorax']/2}")
    ET.SubElement(right_upper_arm, "joint", name="right_shoulder_x", type="hinge", axis="1 0 0", pos=f"0 {height*0.01*0.0208} 0", range="-50 180")
    ET.SubElement(right_upper_arm, "joint", name="right_shoulder_y", type="hinge", axis="0 1 0", pos=f"0 {height*0.01*0.0208} 0", range="-90 90")
    ET.SubElement(right_upper_arm, "joint", name="right_shoulder_z", type="hinge", axis="0 0 1", pos=f"0 {height*0.01*0.0208} 0", range="-50 180")
    ET.SubElement(right_upper_arm, "geom", type="capsule", size=f"{height*0.01*0.0208} {lengths_dict['Upper Arm']/2}", pos = f"0 {-lengths_dict['Upper Arm']/2 + height*0.01*0.0208} 0", euler="-90 0 0", rgba=rgba_in)

    # Left forearm
    left_forearm = ET.SubElement(left_upper_arm, "body", name="left_forearm", pos=f"0 {-lengths_dict['Upper Arm']} 0")
    ET.SubElement(left_forearm, "joint", name="left_elbow_z", type="hinge", axis="0 0 1", pos="0 0 0", range="0 150")
    ET.SubElement(left_forearm, "geom", type="capsule", size=f"0.035 {lengths_dict['Forearm']/2}", pos=f"0 {-lengths_dict['Forearm']/2} 0", euler="-90 0 0", rgba=rgba_in)

    # Right forearm
    right_forearm = ET.SubElement(right_upper_arm, "body", name="right_forearm", pos=f"0 {-lengths_dict['Upper Arm']} 0")
    ET.SubElement(right_forearm, "joint", name="right_elbow_z", type="hinge", axis="0 0 1", pos="0 0 0", range="0 150")
    ET.SubElement(right_forearm, "geom", type="capsule", size=f"0.035 {lengths_dict['Forearm']/2}", pos=f"0 {-lengths_dict['Forearm']/2} 0", euler="-90 0 0", rgba=rgba_in)

    # Left hand
    left_hand = ET.SubElement(left_forearm, "body", name="left_hand", pos=f"0 {-lengths_dict['Forearm']} 0")
    ET.SubElement(left_hand, "joint", name="left_wrist_y", type="hinge", axis="0 1 0", pos="0 0 0", range="-80 80")
    ET.SubElement(left_hand, "joint", name="left_wrist_z", type="hinge", axis="0 0 1", pos="0 0 0", range="-60 60")
    ET.SubElement(left_hand, "geom", type="capsule", size=f"0.045 {lengths_dict['Hand']/2}", pos=f"0 {-lengths_dict['Hand']/2} 0", euler="-90 0 0", rgba=rgba_in)

    # Right hand
    right_hand = ET.SubElement(right_forearm, "body", name="right_hand", pos=f"0 {-lengths_dict['Forearm']} 0")
    ET.SubElement(right_hand, "joint", name="right_wrist_y", type="hinge", axis="0 1 0", pos="0 0 0", range="-80 80")
    ET.SubElement(right_hand, "joint", name="right_wrist_z", type="hinge", axis="0 0 1", pos="0 0 0", range="-60 60")
    ET.SubElement(right_hand, "geom", type="capsule", size=f"0.045 {lengths_dict['Hand']/2}", pos=f"0 {-lengths_dict['Hand']/2} 0", euler="-90 0 0", rgba=rgba_in)


    # TODO: Limit joints
    # TODO: How to determine segment widths? Should we also scale by width?
    # TODO: How does collision work for overlapping segments?
    # TODO: Add mass etc...
    # TODO: Potential issue with thigh body position in relation to pelvis



    # Save to file
    tree = ET.ElementTree(mujoco)
    ET.indent(tree, space="  ", level=0)
    tree.write(filename, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generates a human MJCF based on sex, height, and mass, according to Dumas (2018)."
    )

    parser.add_argument(
        "-o", "--output",
        default="human.xml",
        help="Output XML filename (default: human.xml)"
    )

    parser.add_argument(
        "-m", "--mass",
        required=True,
        type=float,
        help="Mass of the human who's MJCF we want to generate in kilogram"
    )

    parser.add_argument(
        "-t", "--tall",
        required=True,
        type=float,
        help="Height of the human who's MJCF we want to generate in cm"
    )

    parser.add_argument(
        "-s", "--sex",
        required=True,
        choices=["male", "female"],
        help="Sex of the human who's MJCF we want to generate ('male' or 'female')"
    )

    args = parser.parse_args()

    generate_human_model(filename=args.output, mass=args.mass, height=args.tall, sex=args.sex)
