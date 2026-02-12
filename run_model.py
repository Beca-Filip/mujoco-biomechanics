#pokretanje MuJoCo viewer-a za testiranje XML modela

import mujoco
import mujoco.viewer

model = mujoco.MjModel.from_xml_path("simple_human.xml") # zamenite ime fajla s nazivom vašeg XML modela
data = mujoco.MjData(model)

# Pokretanje interaktivnog viewer-a
mujoco.viewer.launch(model, data)