"""
Generate an n-link chain pendulum model for MuJoCo simulation.

This script creates an XML file defining a chain of inverted pendulums,
where each pendulum segment is nested within the previous one, creating
a kinematic chain structure.
"""

import argparse
import xml.etree.ElementTree as ET


def generate_chain_pendulum(filename="pendulum_chain.xml", num_links=2):
    """
    Generate an n-link chain pendulum MuJoCo XML model.

    Args:
        filename (str): Output XML filename. Defaults to "pendulum_chain.xml".
        num_links (int): Number of pendulum links in the chain. Defaults to 2.
    """
    mujoco = ET.Element("mujoco", model="pendulum_chain")
    worldbody = ET.SubElement(mujoco, "worldbody")

    ET.SubElement(worldbody, "light", diffuse=".8 .8 .8", pos="0 0 3", dir="0 0 -1")
    ET.SubElement(worldbody, "geom", type="plane", size="1 1 .1", rgba=".8 .8 .8 1")

    parent = worldbody

    for i in range(num_links):
        # First link starts at origin, subsequent links offset by previous link length
        if i == 0:
            parent = ET.SubElement(parent, "body", pos="0 0 0")
        else:
            parent = ET.SubElement(parent, "body", pos="0 0 1")

        # Each new body becomes the parent for the next iteration,
        # creating a nested kinematic tree structure
        ET.SubElement(parent, "joint", type="hinge", axis="0 -1 0", pos="0 0 0")
        ET.SubElement(parent, "geom", type="box", pos="0 0 .5", size=".1 .1 .5", rgba=".1 .8 .1 1")

    tree = ET.ElementTree(mujoco)
    ET.indent(tree, space="  ", level=0)
    tree.write(filename, encoding="utf-8", xml_declaration=True)
    print(f"Generated {num_links}-link chain pendulum model: {filename}")


def main():
    """Parse command line arguments and generate the chain pendulum model."""
    parser = argparse.ArgumentParser(
        description="Generate an n-link chain pendulum MuJoCo XML model."
    )
    parser.add_argument(
        "positional_argument",
        type=str,
        default="default_positional_argument_value",
        help="This is a required positional argument, and goes before optional flagged arguments."
    )
    parser.add_argument(
        "-o", "--output",
        default="pendulum_chain.xml",
        help="Output XML filename (default: pendulum_chain.xml)"
    )
    parser.add_argument(
        "-n", "--num-links",
        type=int,
        default=2,
        help="Number of pendulum links in the chain (default: 2)"
    )

    args = parser.parse_args()

    if args.num_links < 1:
        parser.error("Number of links must be at least 1")
    
    print(args.positional_argument)
    generate_chain_pendulum(filename=args.output, num_links=args.num_links)


if __name__ == "__main__":
    main()


