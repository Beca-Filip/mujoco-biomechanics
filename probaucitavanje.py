import pandas as pd
import xml.etree.ElementTree as ET
import argparse

def generate_human_model(filename, mass, height, sex):

    k = 1  # scaling coefficient - will be changed depending on subject height
    maleHeight=172
    femaleHeight=156
    rgba_in = "0.8 0.6 0.2 1"
    if sex == "male":
        sheet_name = 0
        k=float(k/maleHeight)
        rgba_in = "0.2 0.4 0.8 1"
    elif sex == "female":
        sheet_name = 1
        k=float(k/femaleHeight)
        rgba_in = "0.9 0.4 0.6 1"
    
    df = pd.read_excel("AnthropometricTableComplete.xlsx", sheet_name=sheet_name)
    k = k * float(height)

    # Prva kolona su imena segmenata, druga kolona su dužine
    segments = df.iloc[:, 0]
    lengths = df.iloc[:, 1] * k   # skaliranje vrednosti
    segment_mass_percentages = df.iloc[:, 2]
    segment_com_x = df.iloc[:, 3]
    segment_com_y = df.iloc[:, 4]
    segment_com_z = df.iloc[:, 5]

    # Racunje mase segmenata na osnovu procenta mase i ukupne mase korisnika
    segment_masses = (segment_mass_percentages / 100) * float(mass)

    # Napravi dict
    lengths_dict = dict(zip(segments, lengths))
    mass_dict = dict(zip(segments, segment_masses))
    segment_com_x_dict = dict(zip(segments, segment_com_x))
    segment_com_y_dict = dict(zip(segments, segment_com_y))
    segment_com_z_dict = dict(zip(segments, segment_com_z))
    
    # Novi dict: lokalna pozicija centra mase
    posMCx_dict = {}
    for i in lengths_dict:
        duzinax = lengths_dict[i]
        privremenapx = float(segment_com_x_dict[i]) /100
        # procenat dužine -> realna dužina -> lokalni pomak
        pozicijax = privremenapx * duzinax
        posMCx_dict[i] = pozicijax

    posMCy_dict = {}
    for i in lengths_dict:
        duzinay = lengths_dict[i]
        privremenapy = float(segment_com_y_dict[i]) /100
        # procenat dužine -> realna dužina -> lokalni pomak
        pozicijay = privremenapy * duzinay
        posMCy_dict[i] = pozicijay

    posMCz_dict = {}
    for i in lengths_dict:
        duzinaz = lengths_dict[i]
        privremenapz = float(segment_com_z_dict[i]) /100
        # procenat dužine -> realna dužina -> lokalni pomak
        pozicijaz = privremenapz * duzinaz
        posMCx_dict[i] = pozicijaz


    print("duzine " , lengths_dict)
    print("mase ", mass_dict)
    print("x ", posMCx_dict)
    print("y ", posMCy_dict)
    print("z ", posMCz_dict)

    mujoco = ET.Element("mujoco", model="simple_human")
    worldbody = ET.SubElement(mujoco, "worldbody")
    ET.SubElement(worldbody, "geom", type="plane", size="1 1 .1", rgba=".8 .8 .8 1")
    ET.SubElement(worldbody, "light", diffuse=".8 .8 .8", pos="0 0 3", dir="0 0 -1")
    ET.SubElement(mujoco, "option", gravity="0 0 -9.81")

    # # Add camera
    # ET.SubElement(worldbody, "camera", name="fixed_camera", pos="3 0 3", euler="0 -30 180")
    # # Add visual
    # visual = ET.SubElement(mujoco, "visual")
    # gl = ET.SubElement(visual, "global", accam="fixed_camera")

     # Thorax kao centralni segment
    thorax = ET.SubElement(worldbody, "body", name="thorax", pos="0 0 1.5", euler="90 0 0")
    ET.SubElement(thorax, "joint", type="free", pos="0 0 0")
    ET.SubElement(thorax, "geom", type="capsule", size=f"0.1 {lengths_dict['Thorax']/2}", pos=f"0 -0.1 0", euler="0 0 0", rgba=rgba_in)
    #ET.SubElement(thorax, "inertial", mass=str(mass_dict["Thorax"]), pos=f"{posMCx_dict['Thorax']} {posMCy_dict['Thorax']} {posMCz_dict['Thorax']}")

     # Head
    head = ET.SubElement(thorax, "body", name="head", pos="0 0 0")
    ET.SubElement(head, "joint", name="head_x", type="hinge", axis="1 0 0", pos=f"0 0 -{lengths_dict['Head with Neck']/2}")
    ET.SubElement(head, "joint", name="head_y", type="hinge", axis="0 1 0", pos=f"0 0 -{lengths_dict['Head with Neck']/2}")
    ET.SubElement(head, "joint", name="head_z", type="hinge", axis="0 0 1", pos=f"0 0 -{lengths_dict['Head with Neck']/2}")
    ET.SubElement(head, "geom", type="sphere", size=f"{lengths_dict['Head with Neck']/2}", pos=f"0 {lengths_dict['Head with Neck']/2} 0", euler="0 0 0", rgba=rgba_in)

     # Abdomen
    abdomen = ET.SubElement(thorax, "body", name="abdomen", pos=f"0 {-lengths_dict["Thorax"]} 0")
    ET.SubElement(abdomen, "joint", name="abdomen_x", type="hinge", axis="1 0 0", pos="0 0 0")
    ET.SubElement(abdomen, "joint", name="abdomen_y", type="hinge", axis="0 1 0", pos="0 0 0")
    ET.SubElement(abdomen, "joint", name="abdomen_z", type="hinge", axis="0 0 1", pos="0 0 0")
    ET.SubElement(abdomen, "geom", type="capsule", size=f"0.1 {lengths_dict['Abdomen']/2}", pos=f"0 -0.1 0", euler="0 0 0", rgba=rgba_in)

    #  # Pelvis
    # pelvis = ET.SubElement(abdomen, "body", name="pelvis", pos=f"0 0 {-lengths_dict['Abdomen']/2 - lengths_dict['Pelvis']/2}")
    # ET.SubElement(pelvis, "joint", name="pelvis_x", type="hinge", axis="1 0 0", pos="0 0 0")
    # ET.SubElement(pelvis, "joint", name="pelvis_y", type="hinge", axis="0 1 0", pos="0 0 0")
    # ET.SubElement(pelvis, "joint", name="pelvis_z", type="hinge", axis="0 0 1", pos="0 0 0")
    # ET.SubElement(pelvis, "geom", type="capsule", size=f"0.1 {lengths_dict['Pelvis']/2}", euler="90 0 0", rgba=rgba_in)

    #  # Left thigh
    # Left_thigh = ET.SubElement(pelvis, "body", name="left_thigh", pos=f"0 {lengths_dict['Pelvis']} {-lengths_dict['Pelvis']/2 - lengths_dict['Thigh']/2}")
    # ET.SubElement(Left_thigh, "joint", name="left_hip_x", type="hinge", axis="1 0 0", pos=f"0 0 {lengths_dict['Thigh']/2}")
    # ET.SubElement(Left_thigh, "joint", name="left_hip_y", type="hinge", axis="0 1 0", pos=f"0 0 {lengths_dict['Thigh']/2}")
    # ET.SubElement(Left_thigh, "joint", name="left_hip_z", type="hinge", axis="0 0 1", pos=f"0 0 {lengths_dict['Thigh']/2}")
    # ET.SubElement(Left_thigh, "geom", type="capsule", size=f"0.04 {lengths_dict['Thigh']/2}", euler="0 0 0", rgba=rgba_in)

    #  # Right thigh
    # Right_thigh = ET.SubElement(pelvis, "body", name="right_thigh", pos=f"0 {-lengths_dict['Pelvis']} {-lengths_dict['Pelvis']/2 - lengths_dict['Thigh']/2}")
    # ET.SubElement(Right_thigh, "joint", name="right_hip_x", type="hinge", axis="1 0 0", pos=f"0 0 {lengths_dict['Thigh']/2}")
    # ET.SubElement(Right_thigh, "joint", name="right_hip_y", type="hinge", axis="0 1 0", pos=f"0 0 {lengths_dict['Thigh']/2}")
    # ET.SubElement(Right_thigh, "joint", name="right_hip_z", type="hinge", axis="0 0 1", pos=f"0 0 {lengths_dict['Thigh']/2}")
    # ET.SubElement(Right_thigh, "geom", type="capsule", size=f"0.04 {lengths_dict['Thigh']/2}", euler="0 0 0", rgba=rgba_in)

    #  # Left shank
    # Left_shank = ET.SubElement(Left_thigh, "body", name="left_shank", pos=f"0 0 {-lengths_dict['Thigh']/2 - lengths_dict['Shank']/2}")
    # ET.SubElement(Left_shank, "joint", name="left_knee_y", type="hinge", axis="0 1 0", pos=f"0 0 {lengths_dict['Shank']/2}")
    # ET.SubElement(Left_shank, "geom", type="capsule", size=f"0.035 {lengths_dict['Shank']/2}", euler="0 0 0", rgba=rgba_in)

    #  # Right shank 
    # Right_shank = ET.SubElement(Right_thigh, "body", name="right_shank", pos=f"0 0 {-lengths_dict['Thigh']/2 - lengths_dict['Shank']/2}")
    # ET.SubElement(Right_shank, "joint", name="right_knee_y", type="hinge", axis="0 1 0", pos=f"0 0 {lengths_dict['Shank']/2}")
    # ET.SubElement(Right_shank, "geom", type="capsule", size=f"0.035 {lengths_dict['Shank']/2}", euler="0 0 0", rgba=rgba_in)

    #  # Left foot
    # Left_foot = ET.SubElement(Left_shank, "body", name="left_foot", pos=f"{lengths_dict['Foot']/2} 0 {-lengths_dict['Shank']/2 - lengths_dict['Foot']/2}")
    # ET.SubElement(Left_foot, "joint", name="left_ankle_y", type="hinge", axis="0 1 0", pos=f"0 0 {lengths_dict['Foot']/2}")
    # ET.SubElement(Left_foot, "joint", name="left_ankle_z", type="hinge", axis="0 0 1", pos=f"0 0 {lengths_dict['Foot']/2}")
    # ET.SubElement(Left_foot, "geom", type="capsule", size=f"0.05 {lengths_dict['Foot']/2}", euler="90 90 0", rgba=rgba_in)

    #  # Right foot
    # Right_foot = ET.SubElement(Right_shank, "body", name="right_foot", pos=f"{lengths_dict['Foot']/2} 0 {-lengths_dict['Shank']/2 - lengths_dict['Foot']/2}")
    # ET.SubElement(Right_foot, "joint", name="right_ankle_y", type="hinge", axis="0 1 0", pos=f"0 0 {lengths_dict['Foot']/2}")
    # ET.SubElement(Right_foot, "joint", name="right_ankle_z", type="hinge", axis="0 0 1", pos=f"0 0 {lengths_dict['Foot']/2}")
    # ET.SubElement(Right_foot, "geom", type="capsule", size=f"0.05 {lengths_dict['Foot']/2}", euler="90 90 0", rgba=rgba_in)

    # # Left upper arm
    # Left_upper_arm = ET.SubElement(thorax, "body", name="left_upper_arm", pos=f"0 {lengths_dict['Thorax']/2} -{lengths_dict['Upper Arm']/4}")
    # ET.SubElement(Left_upper_arm, "joint", name="left_shoulder_x", type="hinge", axis="1 0 0", pos=f"0 0 {lengths_dict['Upper Arm']/2}")
    # ET.SubElement(Left_upper_arm, "joint", name="left_shoulder_y", type="hinge", axis="0 1 0", pos=f"0 0 {lengths_dict['Upper Arm']/2}")
    # ET.SubElement(Left_upper_arm, "joint", name="left_shoulder_z", type="hinge", axis="0 0 1", pos=f"0 0 {lengths_dict['Upper Arm']/2}")
    # ET.SubElement(Left_upper_arm, "geom", type="capsule", size=f"0.035 {lengths_dict['Upper Arm']/2}", rgba=rgba_in)

    # # Right upper arm
    # Right_upper_arm = ET.SubElement(thorax, "body", name="right_upper_arm", pos=f"0 -{lengths_dict['Thorax']/2} -{lengths_dict['Upper Arm']/4}")
    # ET.SubElement(Right_upper_arm, "joint", name="right_shoulder_x", type="hinge", axis="1 0 0", pos=f"0 0 {lengths_dict['Upper Arm']/2}")
    # ET.SubElement(Right_upper_arm, "joint", name="right_shoulder_y", type="hinge", axis="0 1 0", pos=f"0 0 {lengths_dict['Upper Arm']/2}")
    # ET.SubElement(Right_upper_arm, "joint", name="right_shoulder_z", type="hinge", axis="0 0 1", pos=f"0 0 {lengths_dict['Upper Arm']/2}")
    # ET.SubElement(Right_upper_arm, "geom", type="capsule", size=f"0.035 {lengths_dict['Upper Arm']/2}", rgba=rgba_in)

    # # Left forearm
    # Left_forearm = ET.SubElement(Left_upper_arm, "body", name="left_forearm", pos=f"0 0 {-lengths_dict['Upper Arm']/2 - lengths_dict['Forearm']/2}")
    # ET.SubElement(Left_forearm, "joint", name="left_elbow_y", type="hinge", axis="0 1 0", pos=f"0 0 {lengths_dict['Forearm']/2}")
    # ET.SubElement(Left_forearm, "geom", type="capsule", size=f"0.03 {lengths_dict['Forearm']/2}", rgba=rgba_in)

    # # Right forearm
    # Right_forearm = ET.SubElement(Right_upper_arm, "body", name="right_forearm", pos=f"0 0 {-lengths_dict['Upper Arm']/2 - lengths_dict['Forearm']/2}")
    # ET.SubElement(Right_forearm, "joint", name="right_elbow_y", type="hinge", axis="0 1 0", pos=f"0 0 {lengths_dict['Forearm']/2}")
    # ET.SubElement(Right_forearm, "geom", type="capsule", size=f"0.03 {lengths_dict['Forearm']/2}", rgba=rgba_in)

    # # Left hand
    # Left_hand = ET.SubElement(Left_forearm, "body", name="left_hand", pos=f"0 0 {-lengths_dict['Forearm']/2 - lengths_dict['Hand']/2}")
    # ET.SubElement(Left_hand, "joint", name="left_wrist_y", type="hinge", axis="0 1 0", pos=f"0 0 {lengths_dict['Hand']/2}")
    # ET.SubElement(Left_hand, "joint", name="left_wrist_z", type="hinge", axis="0 0 1", pos=f"0 0 {lengths_dict['Hand']/2}")
    # ET.SubElement(Left_hand, "geom", type="capsule", size=f"0.025 {lengths_dict['Hand']/2}", rgba=rgba_in)

    # # Right hand
    # Right_hand = ET.SubElement(Right_forearm, "body", name="right_hand", pos=f"0 0 {-lengths_dict['Forearm']/2 - lengths_dict['Hand']/2}")
    # ET.SubElement(Right_hand, "joint", name="right_wrist_y", type="hinge", axis="0 1 0", pos=f"0 0 {lengths_dict['Hand']/2}")
    # ET.SubElement(Right_hand, "joint", name="right_wrist_z", type="hinge", axis="0 0 1", pos=f"0 0 {lengths_dict['Hand']/2}")
    # ET.SubElement(Right_hand, "geom", type="capsule", size=f"0.025 {lengths_dict['Hand']/2}", rgba=rgba_in)


    # Dodati ruke 
    # Ograniciti zglobove
    # Dodati input za pol i ucitati odgovarajuci excel sheet, promeniti boju modela u zavisnosti od pola
    # Kako odrediti sirine segmenata? Treba li skalirati i po sirini?
    # Kako funkcionise collision za preklopljene segmente?
    # Dodati masu itd...



    #Snimanje
    tree = ET.ElementTree(mujoco)
    ET.indent(tree, space="  ", level=0)
    tree.write(filename, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generates a human MJCF based on sex, height, and mass, according to Dumas (2018)."
    )
    
    parser.add_argument(
        "-o", "--output",
        default="simple_human.xml",
        help="Output XML filename (default: simple_human.xml)"
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
