import pandas as pd
import xml.etree.ElementTree as ET
import argparse

def generate_human_model(filename : str, mass : float, height : float, sex : str):

    k = 1  # scaling coefficient - will be changed depending on subject height
    male_height = 1.77
    female_height = 1.61
    if sex == "male":
        file_name = "anthropometric_table_male.csv"
        k = float(k / male_height)
        rgba_in = "0.2 0.4 0.8 1"
    elif sex == "female":
        file_name = "anthropometric_table_female.csv"
        k = float(k / female_height)
        rgba_in = "0.9 0.4 0.6 1"

    df = pd.read_csv(file_name)
    k = k * float(height)

    # First column is segment names, second column is lengths
    segments = df.iloc[:, 0]
    lengths = df.iloc[:, 1] * k   # scale values
    widths = df.iloc[:, 12] * k   # scale values
    segment_mass_percentages = df.iloc[:, 2]
    segment_com_x = df.iloc[:, 3]
    segment_com_y = df.iloc[:, 4]
    segment_com_z = df.iloc[:, 5]
    joint_limit_negative_x = df.iloc[:, 13]
    joint_limit_positive_x = df.iloc[:, 14]
    joint_limit_negative_y = df.iloc[:, 15]
    joint_limit_positive_y = df.iloc[:, 16]
    joint_limit_negative_z = df.iloc[:, 17]
    joint_limit_positive_z = df.iloc[:, 18]

    # Calculate segment masses based on mass percentage and total user mass
    segment_masses = (segment_mass_percentages / 100) * float(mass)

    # Create dicts
    lengths_dict = dict(zip(segments, lengths))
    widths_dict = dict(zip(segments, widths))
    mass_dict = dict(zip(segments, segment_masses))
    segment_com_x_dict = dict(zip(segments, segment_com_x))
    segment_com_y_dict = dict(zip(segments, segment_com_y))
    segment_com_z_dict = dict(zip(segments, segment_com_z))
    joint_limit_negative_x_dict = dict(zip(segments, joint_limit_negative_x))
    joint_limit_positive_x_dict = dict(zip(segments, joint_limit_positive_x))
    joint_limit_negative_y_dict = dict(zip(segments, joint_limit_negative_y))
    joint_limit_positive_y_dict = dict(zip(segments, joint_limit_positive_y))
    joint_limit_negative_z_dict = dict(zip(segments, joint_limit_negative_z))
    joint_limit_positive_z_dict = dict(zip(segments, joint_limit_positive_z))

    # Local center of mass position dicts
    com_pos_x_dict = {}
    for i in lengths_dict:
        length_x = lengths_dict[i]
        fraction_x = float(segment_com_x_dict[i]) / 100
        # length percentage -> actual length -> local offset
        position_x = fraction_x * length_x
        com_pos_x_dict[i] = position_x

    com_pos_y_dict = {}
    for i in lengths_dict:
        length_y = lengths_dict[i]
        fraction_y = float(segment_com_y_dict[i]) / 100
        # length percentage -> actual length -> local offset
        position_y = fraction_y * length_y
        com_pos_y_dict[i] = position_y

    com_pos_z_dict = {}
    for i in lengths_dict:
        length_z = lengths_dict[i]
        fraction_z = float(segment_com_z_dict[i]) / 100
        # length percentage -> actual length -> local offset
        position_z = fraction_z * length_z
        com_pos_z_dict[i] = position_z

    df_sites = pd.read_csv("site_positions.csv")

    site_names = df_sites.iloc[:, 0]
    site_segments = df_sites.iloc[:, 1]

    site_x = df_sites.iloc[:, 2]
    site_y = df_sites.iloc[:, 3]
    site_z = df_sites.iloc[:, 4]
    
    # Site segments dict
    site_body_dict = dict(zip(site_names, site_segments))

    # Site coordinates dicts
    site_x_dict = dict(zip(site_names, site_x))
    site_y_dict = dict(zip(site_names, site_y))
    site_z_dict = dict(zip(site_names, site_z))

    for site in site_names:
        segment_name = site_body_dict[site]
        segment_length = lengths_dict[segment_name]
        segment_width = widths_dict[segment_name]

        fraction_x = float(site_x_dict[site]) / 100
        fraction_y = float(site_y_dict[site]) / 100
        fraction_z = float(site_z_dict[site]) / 100

        site_x_dict[site] = fraction_x * segment_length
        site_y_dict[site] = fraction_y * segment_length
        site_z_dict[site] = fraction_z * segment_width

    #print("lengths ", lengths_dict)
    #print("masses ", mass_dict)
    print("x ", site_x_dict)
    print("y ", site_y_dict)
    print("z ", site_z_dict)

    mujoco = ET.Element("mujoco", model=filename.replace(".xml", ""))
    worldbody = ET.SubElement(mujoco, "worldbody")
    ET.SubElement(worldbody, "geom", type="plane", size="1 1 .1", rgba=".8 .8 .8 1")
    ET.SubElement(worldbody, "light", diffuse=".8 .8 .8", pos="0 0 3", dir="0 0 -1")
    ET.SubElement(mujoco, "option", gravity="0 0 -9.81")


    # Thorax as central segment
    thorax = ET.SubElement(worldbody, "body", name="thorax", pos=f"0 0 {height-lengths_dict['Head with Neck']}", euler="90 0 0")
    ET.SubElement(thorax, "joint", type="free", pos="0 0 0")
    ET.SubElement(thorax, "geom", type="capsule", size=f"{lengths_dict['Thorax']/3} {widths_dict['Thorax']/2-lengths_dict['Thorax']/6}", pos=f"0 -{lengths_dict['Thorax']/3} 0", euler="0 0 0", rgba=rgba_in)
    ET.SubElement(thorax, "geom", type="capsule", size=f"{lengths_dict['Thorax']/3} {widths_dict['Thorax']/2-lengths_dict['Thorax']/6}", pos=f"0 -{lengths_dict['Thorax']} 0", euler="0 0 0", rgba=rgba_in)
    ET.SubElement(thorax, "inertial", mass=f"{mass_dict['Thorax']}", pos=f"{com_pos_x_dict['Thorax']} {com_pos_y_dict['Thorax']} {com_pos_z_dict['Thorax']}", fullinertia="0.02 0.03 0.04 0.001 0.002 0.003")

    # Head
    head = ET.SubElement(thorax, "body", name="head", pos="0 0 0")
    ET.SubElement(head, "joint", name="head_x", type="hinge", axis="1 0 0", pos="0 0 0", range=f"{-joint_limit_negative_x_dict['Head with Neck']} {joint_limit_positive_x_dict['Head with Neck']}")
    ET.SubElement(head, "joint", name="head_y", type="hinge", axis="0 1 0", pos="0 0 0", range=f"{-joint_limit_negative_y_dict['Head with Neck']} {joint_limit_positive_y_dict['Head with Neck']}")
    ET.SubElement(head, "joint", name="head_z", type="hinge", axis="0 0 1", pos="0 0 0", range=f"{-joint_limit_negative_z_dict['Head with Neck']} {joint_limit_positive_z_dict['Head with Neck']}")
    ET.SubElement(head, "geom", type="sphere", size=f"{lengths_dict['Head with Neck']/2}", pos=f"0 {lengths_dict['Head with Neck']/2} 0", euler="0 0 0", rgba=rgba_in)
    ET.SubElement(head, "inertial", mass=f"{mass_dict['Head with Neck']}", pos=f"{com_pos_x_dict['Head with Neck']} {com_pos_y_dict['Head with Neck']} {com_pos_z_dict['Head with Neck']}", fullinertia="0.02 0.03 0.04 0.001 0.002 0.003")

    # Abdomen
    abdomen = ET.SubElement(thorax, "body", name="abdomen", pos=f"0 {-lengths_dict['Thorax']} 0")
    ET.SubElement(abdomen, "joint", name="abdomen_x", type="hinge", axis="1 0 0", pos="0 0 0", range=f"{-joint_limit_negative_x_dict['Abdomen']} {joint_limit_positive_x_dict['Abdomen']}")
    ET.SubElement(abdomen, "joint", name="abdomen_y", type="hinge", axis="0 1 0", pos="0 0 0", range=f"{-joint_limit_negative_y_dict['Abdomen']} {joint_limit_positive_y_dict['Abdomen']}")
    ET.SubElement(abdomen, "joint", name="abdomen_z", type="hinge", axis="0 0 1", pos="0 0 0", range=f"{-joint_limit_negative_z_dict['Abdomen']} {joint_limit_positive_z_dict['Abdomen']}")
    ET.SubElement(abdomen, "geom", type="capsule", size=f"{lengths_dict['Abdomen']/2} {widths_dict['Abdomen']/2-lengths_dict['Abdomen']/4}", pos=f"0 -{lengths_dict['Abdomen']} 0", euler="0 0 0", rgba=rgba_in)
    ET.SubElement(abdomen, "inertial", mass=f"{mass_dict['Abdomen']}", pos=f"{com_pos_x_dict['Abdomen']} {com_pos_y_dict['Abdomen']} {com_pos_z_dict['Abdomen']}", fullinertia="0.02 0.03 0.04 0.001 0.002 0.003")
    
    # Pelvis
    pelvis = ET.SubElement(abdomen, "body", name="pelvis", pos=f"0 {-lengths_dict['Abdomen']} 0")
    ET.SubElement(pelvis, "joint", name="pelvis_x", type="hinge", axis="1 0 0", pos="0 0 0", range=f"{-joint_limit_negative_x_dict['Pelvis']} {joint_limit_positive_x_dict['Pelvis']}")
    ET.SubElement(pelvis, "joint", name="pelvis_y", type="hinge", axis="0 1 0", pos="0 0 0", range=f"{-joint_limit_negative_y_dict['Pelvis']} {joint_limit_positive_y_dict['Pelvis']}")
    ET.SubElement(pelvis, "joint", name="pelvis_z", type="hinge", axis="0 0 1", pos="0 0 0", range=f"{-joint_limit_negative_z_dict['Pelvis']} {joint_limit_positive_z_dict['Pelvis']}")
    ET.SubElement(pelvis, "geom", type="capsule", size=f"{lengths_dict['Pelvis']/2} {widths_dict['Pelvis']/2-lengths_dict['Pelvis']/4}", pos=f"0 -{lengths_dict['Pelvis']} 0", euler="0 0 0", rgba=rgba_in)
    ET.SubElement(pelvis, "inertial", mass=f"{mass_dict['Pelvis']}", pos=f"{com_pos_x_dict['Pelvis']} {com_pos_y_dict['Pelvis']} {com_pos_z_dict['Pelvis']}", fullinertia="0.02 0.03 0.04 0.001 0.002 0.003")

    # Left thigh
    left_thigh = ET.SubElement(pelvis, "body", name="left_thigh", pos=f"0 {-lengths_dict['Pelvis']} {-widths_dict['Pelvis']/2}")
    ET.SubElement(left_thigh, "joint", name="left_hip_x", type="hinge", axis="1 0 0", pos="0 0 0", range=f"{-joint_limit_negative_x_dict['Thigh']} {joint_limit_positive_x_dict['Thigh']}")
    ET.SubElement(left_thigh, "joint", name="left_hip_y", type="hinge", axis="0 1 0", pos="0 0 0", range=f"{-joint_limit_negative_y_dict['Thigh']} {joint_limit_positive_y_dict['Thigh']}")
    ET.SubElement(left_thigh, "joint", name="left_hip_z", type="hinge", axis="0 0 1", pos="0 0 0", range=f"{-joint_limit_negative_z_dict['Thigh']} {joint_limit_positive_z_dict['Thigh']}")
    ET.SubElement(left_thigh, "geom", type="capsule", size=f"{widths_dict['Thigh']/2} {lengths_dict['Thigh']/2-widths_dict['Thigh']/4}", pos = f"0 {-lengths_dict['Thigh']/2} 0", euler="-90 0 0", rgba=rgba_in)
    ET.SubElement(left_thigh, "inertial", mass=f"{mass_dict['Thigh']}", pos=f"{com_pos_x_dict['Thigh']} {com_pos_y_dict['Thigh']} {com_pos_z_dict['Thigh']}", fullinertia="0.02 0.03 0.04 0.001 0.002 0.003")
    ET.SubElement(left_thigh, "site", name="greater_trochanter_left", pos=f"{site_x_dict['greater_trochanter_left']} {site_y_dict['greater_trochanter_left']} {site_z_dict['greater_trochanter_left']}", size="0.02", rgba="1 0 0 1")
    ET.SubElement(left_thigh, "site", name="lateral_femoral_epicondyle_left", pos=f"{site_x_dict['lateral_femoral_epicondyle_left']} {site_y_dict['lateral_femoral_epicondyle_left']} {site_z_dict['lateral_femoral_epicondyle_left']}", size="0.02", rgba="1 0 0 1")

    # Right thigh
    right_thigh = ET.SubElement(pelvis, "body", name="right_thigh", pos=f"0 {-lengths_dict['Pelvis']} {widths_dict['Pelvis']/2}")
    ET.SubElement(right_thigh, "joint", name="right_hip_x", type="hinge", axis="1 0 0", pos="0 0 0", range=f"{-joint_limit_positive_x_dict['Thigh']} {joint_limit_negative_x_dict['Thigh']}")
    ET.SubElement(right_thigh, "joint", name="right_hip_y", type="hinge", axis="0 1 0", pos="0 0 0", range=f"{-joint_limit_negative_y_dict['Thigh']} {joint_limit_positive_y_dict['Thigh']}")
    ET.SubElement(right_thigh, "joint", name="right_hip_z", type="hinge", axis="0 0 1", pos="0 0 0", range=f"{-joint_limit_negative_z_dict['Thigh']} {joint_limit_positive_z_dict['Thigh']}")
    ET.SubElement(right_thigh, "geom", type="capsule", size=f"{widths_dict['Thigh']/2} {lengths_dict['Thigh']/2-widths_dict['Thigh']/4}", pos = f"0 {-lengths_dict['Thigh']/2} 0", euler="-90 0 0", rgba=rgba_in)
    ET.SubElement(right_thigh, "inertial", mass=f"{mass_dict['Thigh']}", pos=f"{com_pos_x_dict['Thigh']} {com_pos_y_dict['Thigh']} {com_pos_z_dict['Thigh']}", fullinertia="0.02 0.03 0.04 0.001 0.002 0.003")
    ET.SubElement(right_thigh, "site", name="greater_trochanter_right", pos=f"{site_x_dict['greater_trochanter_right']} {site_y_dict['greater_trochanter_right']} {site_z_dict['greater_trochanter_right']}", size="0.02", rgba="1 0 0 1")
    ET.SubElement(right_thigh, "site", name="lateral_femoral_epicondyle_right", pos=f"{site_x_dict['lateral_femoral_epicondyle_right']} {site_y_dict['lateral_femoral_epicondyle_right']} {site_z_dict['lateral_femoral_epicondyle_right']}", size="0.02", rgba="1 0 0 1")

    # Left shank
    left_shank = ET.SubElement(left_thigh, "body", name="left_shank", pos=f"0 {-lengths_dict['Thigh']} 0")
    ET.SubElement(left_shank, "joint", name="left_knee_z", type="hinge", axis="0 0 1", pos="0 0 0", range=f"{-joint_limit_negative_z_dict['Shank']} {joint_limit_positive_z_dict['Shank']}")
    ET.SubElement(left_shank, "geom", type="capsule", size=f"{widths_dict['Shank']/2} {lengths_dict['Shank']/2-widths_dict['Shank']/4}", pos = f"0 {-lengths_dict['Shank']/2} 0", euler="-90 0 0", rgba=rgba_in)
    ET.SubElement(left_shank, "inertial", mass=f"{mass_dict['Shank']}", pos=f"{com_pos_x_dict['Shank']} {com_pos_y_dict['Shank']} {com_pos_z_dict['Shank']}", fullinertia="0.02 0.03 0.04 0.001 0.002 0.003")
    ET.SubElement(left_shank, "site", name="lateral_maleollus_left", pos=f"{site_x_dict['lateral_maleollus_left']} {site_y_dict['lateral_maleollus_left']} {site_z_dict['lateral_maleollus_left']}", size="0.02", rgba="1 0 0 1")

    # Right shank
    right_shank = ET.SubElement(right_thigh, "body", name="right_shank", pos=f"0 {-lengths_dict['Thigh']} 0")
    ET.SubElement(right_shank, "joint", name="right_knee_z", type="hinge", axis="0 0 1", pos="0 0 0", range=f"{-joint_limit_negative_z_dict['Shank']} {joint_limit_positive_z_dict['Shank']}")
    ET.SubElement(right_shank, "geom", type="capsule", size=f"{widths_dict['Shank']/2} {lengths_dict['Shank']/2-widths_dict['Shank']/4}", pos = f"0 {-lengths_dict['Shank']/2} 0", euler="-90 0 0", rgba=rgba_in)
    ET.SubElement(right_shank, "inertial", mass=f"{mass_dict['Shank']}", pos=f"{com_pos_x_dict['Shank']} {com_pos_y_dict['Shank']} {com_pos_z_dict['Shank']}", fullinertia="0.02 0.03 0.04 0.001 0.002 0.003")
    ET.SubElement(right_shank, "site", name="lateral_maleollus_right", pos=f"{site_x_dict['lateral_maleollus_right']} {site_y_dict['lateral_maleollus_right']} {site_z_dict['lateral_maleollus_right']}", size="0.02", rgba="1 0 0 1")

    # Left foot
    left_foot = ET.SubElement(left_shank, "body", name="left_foot", pos=f"0 {-lengths_dict['Shank']} 0")
    ET.SubElement(left_foot, "joint", name="left_ankle_y", type="hinge", axis="0 1 0", pos="0 0 0", range=f"{-joint_limit_negative_y_dict['Foot']} {joint_limit_positive_y_dict['Foot']}")
    ET.SubElement(left_foot, "joint", name="left_ankle_z", type="hinge", axis="0 0 1", pos="0 0 0", range=f"{-joint_limit_negative_z_dict['Foot']} {joint_limit_positive_z_dict['Foot']}")
    ET.SubElement(left_foot, "geom", type="capsule", size=f"{widths_dict['Foot']/2} {lengths_dict['Foot']/2-widths_dict['Foot']/4}", pos = f"{lengths_dict['Foot']/2} 0 0", euler="0 90 0", rgba=rgba_in)
    ET.SubElement(left_foot, "inertial", mass=f"{mass_dict['Foot']}", pos=f"{com_pos_x_dict['Foot']} {com_pos_y_dict['Foot']} {com_pos_z_dict['Foot']}", fullinertia="0.02 0.03 0.04 0.001 0.002 0.003")
    ET.SubElement(left_foot, "site", name="metatarsal_fifth_left", pos=f"{site_x_dict['metatarsal_fifth_left']} {site_y_dict['metatarsal_fifth_left']} {site_z_dict['metatarsal_fifth_left']}", size="0.02", rgba="1 0 0 1")

    # Right foot
    right_foot = ET.SubElement(right_shank, "body", name="right_foot", pos=f"0 {-lengths_dict['Shank']} 0")
    ET.SubElement(right_foot, "joint", name="right_ankle_y", type="hinge", axis="0 1 0", pos="0 0 0", range=f"{-joint_limit_negative_y_dict['Foot']} {joint_limit_positive_y_dict['Foot']}")
    ET.SubElement(right_foot, "joint", name="right_ankle_z", type="hinge", axis="0 0 1", pos="0 0 0", range=f"{-joint_limit_negative_z_dict['Foot']} {joint_limit_positive_z_dict['Foot']}")
    ET.SubElement(right_foot, "geom", type="capsule", size=f"{widths_dict['Foot']/2} {lengths_dict['Foot']/2-widths_dict['Foot']/4}", pos = f"{lengths_dict['Foot']/2} 0 0", euler="0 90 0", rgba=rgba_in)
    ET.SubElement(right_foot, "inertial", mass=f"{mass_dict['Foot']}", pos=f"{com_pos_x_dict['Foot']} {com_pos_y_dict['Foot']} {com_pos_z_dict['Foot']}", fullinertia="0.02 0.03 0.04 0.001 0.002 0.003")
    ET.SubElement(right_foot, "site", name="metatarsal_fifth_right", pos=f"{site_x_dict['metatarsal_fifth_right']} {site_y_dict['metatarsal_fifth_right']} {site_z_dict['metatarsal_fifth_right']}", size="0.02", rgba="1 0 0 1")

    # Left upper arm
    left_upper_arm = ET.SubElement(thorax, "body", name="left_upper_arm", pos=f"0 -{0.55*lengths_dict['Thorax']/2} -{height*0.07 + height*0.0208 + 0.55*lengths_dict['Thorax']/2}")
    ET.SubElement(left_upper_arm, "joint", name="left_shoulder_x", type="hinge", axis="1 0 0", pos=f"0 {height*0.0208} 0", range=f"{-joint_limit_negative_x_dict['Upper Arm']} {joint_limit_positive_x_dict['Upper Arm']}")
    ET.SubElement(left_upper_arm, "joint", name="left_shoulder_y", type="hinge", axis="0 1 0", pos=f"0 {height*0.0208} 0", range=f"{-joint_limit_negative_y_dict['Upper Arm']} {joint_limit_positive_y_dict['Upper Arm']}")
    ET.SubElement(left_upper_arm, "joint", name="left_shoulder_z", type="hinge", axis="0 0 1", pos=f"0 {height*0.0208} 0", range=f"{-joint_limit_negative_z_dict['Upper Arm']} {joint_limit_positive_z_dict['Upper Arm']}")
    ET.SubElement(left_upper_arm, "geom", type="capsule", size=f"{widths_dict['Upper Arm']/2} {lengths_dict['Upper Arm']/2-widths_dict['Upper Arm']/4}", pos = f"0 {-lengths_dict['Upper Arm']/2 + height*0.0208} 0", euler="-90 0 0", rgba=rgba_in)
    ET.SubElement(left_upper_arm, "inertial", mass=f"{mass_dict['Upper Arm']}", pos=f"{com_pos_x_dict['Upper Arm']} {com_pos_y_dict['Upper Arm']} {com_pos_z_dict['Upper Arm']}", fullinertia="0.02 0.03 0.04 0.001 0.002 0.003")
    ET.SubElement(left_upper_arm, "site", name="acromion_left", pos=f"{site_x_dict['acromion_left']} {site_y_dict['acromion_left']} {site_z_dict['acromion_left']}", size="0.02", rgba="1 0 0 1")
    ET.SubElement(left_upper_arm, "site", name="lateral_humeral_epicondyle_left", pos=f"{site_x_dict['lateral_humeral_epicondyle_left']} {site_y_dict['lateral_humeral_epicondyle_left']} {site_z_dict['lateral_humeral_epicondyle_left']}", size="0.02", rgba="1 0 0 1")

    # Right upper arm
    right_upper_arm = ET.SubElement(thorax, "body", name="right_upper_arm", pos=f"0 -{0.55*lengths_dict['Thorax']/2} {height*0.07 + height*0.0208 + 0.55*lengths_dict['Thorax']/2}")
    ET.SubElement(right_upper_arm, "joint", name="right_shoulder_x", type="hinge", axis="1 0 0", pos=f"0 {height*0.0208} 0", range=f"{-joint_limit_positive_x_dict['Upper Arm']} {joint_limit_negative_x_dict['Upper Arm']}")
    ET.SubElement(right_upper_arm, "joint", name="right_shoulder_y", type="hinge", axis="0 1 0", pos=f"0 {height*0.0208} 0", range=f"{-joint_limit_negative_y_dict['Upper Arm']} {joint_limit_positive_y_dict['Upper Arm']}")
    ET.SubElement(right_upper_arm, "joint", name="right_shoulder_z", type="hinge", axis="0 0 1", pos=f"0 {height*0.0208} 0", range=f"{-joint_limit_negative_z_dict['Upper Arm']} {joint_limit_positive_z_dict['Upper Arm']}")
    ET.SubElement(right_upper_arm, "geom", type="capsule", size=f"{widths_dict['Upper Arm']/2} {lengths_dict['Upper Arm']/2-widths_dict['Upper Arm']/4}", pos = f"0 {-lengths_dict['Upper Arm']/2 + height*0.0208} 0", euler="-90 0 0", rgba=rgba_in)
    ET.SubElement(right_upper_arm, "inertial", mass=f"{mass_dict['Upper Arm']}", pos=f"{com_pos_x_dict['Upper Arm']} {com_pos_y_dict['Upper Arm']} {com_pos_z_dict['Upper Arm']}", fullinertia="0.02 0.03 0.04 0.001 0.002 0.003")
    ET.SubElement(right_upper_arm, "site", name="acromion_right", pos=f"{site_x_dict['acromion_right']} {site_y_dict['acromion_right']} {site_z_dict['acromion_right']}", size="0.02", rgba="1 0 0 1")
    ET.SubElement(right_upper_arm, "site", name="lateral_humeral_epicondyle_right", pos=f"{site_x_dict['lateral_humeral_epicondyle_right']} {site_y_dict['lateral_humeral_epicondyle_right']} {site_z_dict['lateral_humeral_epicondyle_right']}", size="0.02", rgba="1 0 0 1")

    # Left forearm
    left_forearm = ET.SubElement(left_upper_arm, "body", name="left_forearm", pos=f"0 {-lengths_dict['Upper Arm']} 0")
    ET.SubElement(left_forearm, "joint", name="left_elbow_z", type="hinge", axis="0 0 1", pos="0 0 0", range=f"{-joint_limit_negative_z_dict['Forearm']} {joint_limit_positive_z_dict['Forearm']}")
    ET.SubElement(left_forearm, "geom", type="capsule", size=f"{widths_dict['Forearm']/2} {lengths_dict['Forearm']/2-widths_dict['Forearm']/4}", pos=f"0 {-lengths_dict['Forearm']/2} 0", euler="-90 0 0", rgba=rgba_in)
    ET.SubElement(left_forearm, "inertial", mass=f"{mass_dict['Forearm']}", pos=f"{com_pos_x_dict['Forearm']} {com_pos_y_dict['Forearm']} {com_pos_z_dict['Forearm']}", fullinertia="0.02 0.03 0.04 0.001 0.002 0.003")

    # Right forearm
    right_forearm = ET.SubElement(right_upper_arm, "body", name="right_forearm", pos=f"0 {-lengths_dict['Upper Arm']} 0")
    ET.SubElement(right_forearm, "joint", name="right_elbow_z", type="hinge", axis="0 0 1", pos="0 0 0", range=f"{-joint_limit_negative_z_dict['Forearm']} {joint_limit_positive_z_dict['Forearm']}")
    ET.SubElement(right_forearm, "geom", type="capsule", size=f"{widths_dict['Forearm']/2} {lengths_dict['Forearm']/2-widths_dict['Forearm']/4}", pos=f"0 {-lengths_dict['Forearm']/2} 0", euler="-90 0 0", rgba=rgba_in)
    ET.SubElement(right_forearm, "inertial", mass=f"{mass_dict['Forearm']}", pos=f"{com_pos_x_dict['Forearm']} {com_pos_y_dict['Forearm']} {com_pos_z_dict['Forearm']}", fullinertia="0.02 0.03 0.04 0.001 0.002 0.003")

    # Left hand
    left_hand = ET.SubElement(left_forearm, "body", name="left_hand", pos=f"0 {-lengths_dict['Forearm']} 0")
    ET.SubElement(left_hand, "joint", name="left_wrist_y", type="hinge", axis="0 1 0", pos="0 0 0", range=f"{-joint_limit_negative_y_dict['Hand']} {joint_limit_positive_y_dict['Hand']}")
    ET.SubElement(left_hand, "joint", name="left_wrist_z", type="hinge", axis="0 0 1", pos="0 0 0", range=f"{-joint_limit_negative_z_dict['Hand']} {joint_limit_positive_z_dict['Hand']}")
    ET.SubElement(left_hand, "geom", type="capsule", size=f"{widths_dict['Hand']/2} {lengths_dict['Hand']/2-widths_dict['Hand']/4}", pos=f"0 {-lengths_dict['Hand']/2} 0", euler="-90 0 0", rgba=rgba_in)
    ET.SubElement(left_hand, "inertial", mass=f"{mass_dict['Hand']}", pos=f"{com_pos_x_dict['Hand']} {com_pos_y_dict['Hand']} {com_pos_z_dict['Hand']}", fullinertia="0.02 0.03 0.04 0.001 0.002 0.003")
    ET.SubElement(left_hand, "site", name="ulnar_styloid_left", pos=f"{site_x_dict['ulnar_styloid_left']} {site_y_dict['ulnar_styloid_left']} {site_z_dict['ulnar_styloid_left']}", size="0.02", rgba="1 0 0 1")

    # Right hand
    right_hand = ET.SubElement(right_forearm, "body", name="right_hand", pos=f"0 {-lengths_dict['Forearm']} 0")
    ET.SubElement(right_hand, "joint", name="right_wrist_y", type="hinge", axis="0 1 0", pos="0 0 0", range=f"{-joint_limit_negative_y_dict['Hand']} {joint_limit_positive_y_dict['Hand']}")
    ET.SubElement(right_hand, "joint", name="right_wrist_z", type="hinge", axis="0 0 1", pos="0 0 0", range=f"{-joint_limit_negative_z_dict['Hand']} {joint_limit_positive_z_dict['Hand']}")
    ET.SubElement(right_hand, "geom", type="capsule", size=f"{widths_dict['Hand']/2} {lengths_dict['Hand']/2-widths_dict['Hand']/4}", pos=f"0 {-lengths_dict['Hand']/2} 0", euler="-90 0 0", rgba=rgba_in)
    ET.SubElement(right_hand, "inertial", mass=f"{mass_dict['Hand']}", pos=f"{com_pos_x_dict['Hand']} {com_pos_y_dict['Hand']} {com_pos_z_dict['Hand']}", fullinertia="0.02 0.03 0.04 0.001 0.002 0.003")
    ET.SubElement(right_hand, "site", name="ulnar_styloid_right", pos=f"{site_x_dict['ulnar_styloid_right']} {site_y_dict['ulnar_styloid_right']} {site_z_dict['ulnar_styloid_right']}", size="0.02", rgba="1 0 0 1")

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
        help="Height of the human who's MJCF we want to generate in m"
    )

    parser.add_argument(
        "-s", "--sex",
        required=True,
        choices=["male", "female"],
        help="Sex of the human who's MJCF we want to generate ('male' or 'female')"
    )

    args = parser.parse_args()

    generate_human_model(filename=args.output, mass=args.mass, height=args.tall, sex=args.sex)
