import pandas as pd
import xml.etree.ElementTree as ET

def generate_human_model(filename="simple_human.xml"):

    df = pd.read_excel("AnthropometricTableComplete.xlsx")

    k = 1  # koeficijent skaliranja - treba napraviti input za visinu ispitanika i izračunati k na osnovu toga

    # Prva kolona su imena segmenata, druga kolona su dužine
    segments = df.iloc[:, 0]
    lengths = df.iloc[:, 1] * k   # skaliranje vrednosti

    # Napravi dict
    lengths_dict = dict(zip(segments, lengths))

    print(lengths_dict)

    mujoco = ET.Element("mujoco", model="simple_human")
    worldbody = ET.SubElement(mujoco, "worldbody")
    ET.SubElement(worldbody, "geom", type="plane", size="1 1 .1", rgba=".8 .8 .8 1")
    ET.SubElement(worldbody, "light", diffuse=".8 .8 .8", pos="0 0 3", dir="0 0 -1")
    ET.SubElement(mujoco, "option", gravity="0 0 -9.81")


     # Thorax kao centralni segment
    thorax = ET.SubElement(worldbody, "body", name="thorax", pos="0 0 1.5")
    ET.SubElement(thorax, "joint", type="free", pos="0 0 0")
    ET.SubElement(thorax, "geom", type="capsule", size=f"0.1 {lengths_dict['Thorax']/2}", euler="90 0 0", rgba="0.8 0.6 0.2 1")

     # Head
    head = ET.SubElement(thorax, "body", name="head", pos=f"0 0 {lengths_dict['Thorax']/2 + lengths_dict['Head with Neck']/2}")
    ET.SubElement(head, "joint", name="head_x", type="hinge", axis="1 0 0", pos=f"0 0 -{lengths_dict['Head with Neck']/2}")
    ET.SubElement(head, "joint", name="head_y", type="hinge", axis="0 1 0", pos=f"0 0 -{lengths_dict['Head with Neck']/2}")
    ET.SubElement(head, "joint", name="head_z", type="hinge", axis="0 0 1", pos=f"0 0 -{lengths_dict['Head with Neck']/2}")
    ET.SubElement(head, "geom", type="sphere", size=f"{lengths_dict['Head with Neck']/2}", euler="90 0 0", rgba="0.8 0.6 0.2 1")

     # Abdomen
    abdomen = ET.SubElement(thorax, "body", name="abdomen", pos=f"0 0 {-lengths_dict['Thorax']/2 - lengths_dict['Abdomen']/2}")
    ET.SubElement(abdomen, "joint", name="abdomen_x", type="hinge", axis="1 0 0", pos="0 0 0")
    ET.SubElement(abdomen, "joint", name="abdomen_y", type="hinge", axis="0 1 0", pos="0 0 0")
    ET.SubElement(abdomen, "joint", name="abdomen_z", type="hinge", axis="0 0 1", pos="0 0 0")
    ET.SubElement(abdomen, "geom", type="capsule", size=f"0.1 {lengths_dict['Abdomen']/2}", euler="90 0 0", rgba="0.8 0.6 0.2 1")

     # Pelvis
    pelvis = ET.SubElement(abdomen, "body", name="pelvis", pos=f"0 0 {-lengths_dict['Abdomen']/2 - lengths_dict['Pelvis']/2}")
    ET.SubElement(pelvis, "joint", name="pelvis_x", type="hinge", axis="1 0 0", pos="0 0 0")
    ET.SubElement(pelvis, "joint", name="pelvis_y", type="hinge", axis="0 1 0", pos="0 0 0")
    ET.SubElement(pelvis, "joint", name="pelvis_z", type="hinge", axis="0 0 1", pos="0 0 0")
    ET.SubElement(pelvis, "geom", type="capsule", size=f"0.1 {lengths_dict['Pelvis']/2}", euler="90 0 0", rgba="0.8 0.6 0.2 1")

     # Left thigh
    Left_thigh = ET.SubElement(pelvis, "body", name="left_thigh", pos=f"0 {lengths_dict['Pelvis']} {-lengths_dict['Pelvis']/2 - lengths_dict['Thigh']/2}")
    ET.SubElement(Left_thigh, "joint", name="left_hip_x", type="hinge", axis="1 0 0", pos=f"0 0 {lengths_dict['Thigh']/2}")
    ET.SubElement(Left_thigh, "joint", name="left_hip_y", type="hinge", axis="0 1 0", pos=f"0 0 {lengths_dict['Thigh']/2}")
    ET.SubElement(Left_thigh, "joint", name="left_hip_z", type="hinge", axis="0 0 1", pos=f"0 0 {lengths_dict['Thigh']/2}")
    ET.SubElement(Left_thigh, "geom", type="capsule", size=f"0.04 {lengths_dict['Thigh']/2}", euler="0 0 0", rgba="0.8 0.6 0.2 1")

     # Right thigh
    Right_thigh = ET.SubElement(pelvis, "body", name="right_thigh", pos=f"0 {-lengths_dict['Pelvis']} {-lengths_dict['Pelvis']/2 - lengths_dict['Thigh']/2}")
    ET.SubElement(Right_thigh, "joint", name="right_hip_x", type="hinge", axis="1 0 0", pos=f"0 0 {lengths_dict['Thigh']/2}")
    ET.SubElement(Right_thigh, "joint", name="right_hip_y", type="hinge", axis="0 1 0", pos=f"0 0 {lengths_dict['Thigh']/2}")
    ET.SubElement(Right_thigh, "joint", name="right_hip_z", type="hinge", axis="0 0 1", pos=f"0 0 {lengths_dict['Thigh']/2}")
    ET.SubElement(Right_thigh, "geom", type="capsule", size=f"0.04 {lengths_dict['Thigh']/2}", euler="0 0 0", rgba="0.8 0.6 0.2 1")

     # Left shank
    Left_shank = ET.SubElement(Left_thigh, "body", name="left_shank", pos=f"0 0 {-lengths_dict['Thigh']/2 - lengths_dict['Shank']/2}")
    ET.SubElement(Left_shank, "joint", name="left_knee_y", type="hinge", axis="0 1 0", pos=f"0 0 {lengths_dict['Shank']/2}")
    ET.SubElement(Left_shank, "geom", type="capsule", size=f"0.035 {lengths_dict['Shank']/2}", euler="0 0 0", rgba="0.8 0.6 0.2 1")

     # Right shank 
    Right_shank = ET.SubElement(Right_thigh, "body", name="right_shank", pos=f"0 0 {-lengths_dict['Thigh']/2 - lengths_dict['Shank']/2}")
    ET.SubElement(Right_shank, "joint", name="right_knee_y", type="hinge", axis="0 1 0", pos=f"0 0 {lengths_dict['Shank']/2}")
    ET.SubElement(Right_shank, "geom", type="capsule", size=f"0.035 {lengths_dict['Shank']/2}", euler="0 0 0", rgba="0.8 0.6 0.2 1")

     # Left foot
    Left_foot = ET.SubElement(Left_shank, "body", name="left_foot", pos=f"{lengths_dict['Foot']/2} 0 {-lengths_dict['Shank']/2 - lengths_dict['Foot']/2}")
    ET.SubElement(Left_foot, "joint", name="left_ankle_y", type="hinge", axis="0 1 0", pos=f"0 0 {lengths_dict['Foot']/2}")
    ET.SubElement(Left_foot, "joint", name="left_ankle_z", type="hinge", axis="0 0 1", pos=f"0 0 {lengths_dict['Foot']/2}")
    ET.SubElement(Left_foot, "geom", type="capsule", size=f"0.05 {lengths_dict['Foot']/2}", euler="90 90 0", rgba="0.8 0.6 0.2 1")

     # Right foot
    Right_foot = ET.SubElement(Right_shank, "body", name="right_foot", pos=f"{lengths_dict['Foot']/2} 0 {-lengths_dict['Shank']/2 - lengths_dict['Foot']/2}")
    ET.SubElement(Right_foot, "joint", name="right_ankle_y", type="hinge", axis="0 1 0", pos=f"0 0 {lengths_dict['Foot']/2}")
    ET.SubElement(Right_foot, "joint", name="right_ankle_z", type="hinge", axis="0 0 1", pos=f"0 0 {lengths_dict['Foot']/2}")
    ET.SubElement(Right_foot, "geom", type="capsule", size=f"0.05 {lengths_dict['Foot']/2}", euler="90 90 0", rgba="0.8 0.6 0.2 1")



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
    generate_human_model()
    #generate_human_model("human_model.xml", lengths)?


