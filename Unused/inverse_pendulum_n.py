import sys
import string
import xml.etree.ElementTree as ET

def generate_pendulum_n(pendulum_order=1, filename='inverted_pendulum_1.xml'):
    mujoco = ET.Element("mujoco", model=filename.replace(".xml", ""))
    worldbody = ET.SubElement(mujoco, "worldbody")
    ET.SubElement(worldbody, "light", diffuse=".8 .8 .8", pos="0 0 3", dir="0 0 -1")
    ET.SubElement(worldbody, "geom", type="plane", size='1 1 .1', rgba=".8 .8 .8 1")
    #body0 = ET.SubElement(worldbody, 'body' , pos = '0 0 0')
    parent = worldbody
    #ET.SubElement(body0, 'joint', type = 'hinge', axis = '0 -1 0', pos = '0 0 0')
    #ET.SubElement(body0, 'geom', type = 'box', pos = '0 0 .5', size = '.1 .1 .5', rgba = '.1 .8 .1 1'))
    for i in range(pendulum_order):
        if i == 0:
            parent = ET.SubElement(parent, 'body', pos = '0 0 0')
        else:
            parent = ET.SubElement(parent, 'body', pos='0 0 1')
        #novi parent postaje novi body kom je parent prethodni parent,
        # malo je fucked up, nije intuitivno, stalno zaboravljam kako sam ga napravio
        ET.SubElement(parent, 'joint', type='hinge', axis='0 -1 0', pos='0 0 0')
        ET.SubElement(parent, 'geom', type='box', pos='0 0 .5', size='.1 .1 .5', rgba='.1 .8 .1 1')
    tree = ET.ElementTree(mujoco)
    ET.indent(tree, space="  ", level=0)
    tree.write(filename, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Script takes in at least 1 argument.")
        exit()

    if len(sys.argv) > 1:
        pendulum_order = int(sys.argv[1])
        if pendulum_order < 1:
            raise ValueError("pendulum_order must be >= 1.")

    if len(sys.argv) > 2:
        filename = sys.argv[2]
        if not filename.endswith(".xml"):
            filename = filename + ".xml"
    else:
        filename = f"inverted_pendulum_{pendulum_order}.xml"
        
    generate_pendulum_n(pendulum_order, filename)

    pass