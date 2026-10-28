# mujoco-biomechanics

A Python tool for generating anatomically scaled human musculoskeletal models for the [MuJoCo](https://mujoco.org/) physics simulator.

Given a subject's **mass**, **height**, and **sex**, the generator produces a full-body MuJoCo XML model with:

- Segment geometry, mass, and centre-of-mass positions scaled from anthropometric tables (de Leva, 1996)
- Full inertia tensors (radii of gyration + products of inertia)
- Anatomical joint limits for all degrees of freedom
- Pre-configured contact exclusions and floor contact parameters

## Requirements

- Python 3.10 or newer
- MuJoCo 3.3.4 or newer

## Installation

```bash
python -m pip install mujoco-biomechanics
```

## Generate a model

```bash
mujoco-biomechanics-generate --mass 75 --height 1.82 --sex male --output male.xml
```

```bash
mujoco-biomechanics-generate --mass 60 --height 1.68 --sex female --alpha 0.8 --output female.xml
```

## Inspect a model

```bash
mujoco-biomechanics-inspect male.xml
```
## Build a combined scene

Save without opening the viewer:

```bash
mujoco-biomechanics-run-scene male.xml female.xml --number-of-columns 2 --spacing 1.5 --output scene.xml --save-only
```

Save and open the viewer:

```bash
mujoco-biomechanics-run-scene male.xml female.xml --number-of-columns 2 --spacing 1.5 --output scene.xml
```

Press Space in the viewer to pause or resume simulation.

### macOS viewer note

MuJoCo's passive viewer must be started through `mjpython` on macOS:

```bash
mjpython -m mujoco_biomechanics_code.run_model male.xml female.xml --output scene.xml
```

## Python API

```python
from mujoco_biomechanics_code.generate_human_model import generate_human_model

output = generate_human_model(
    filename="human.xml",
    mass=75.0,
    height=1.82,
    sex="male",
    alpha=1.0,
)
print(output)
```

## Development installation

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install the package and development tools:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run tests:

```bash
python -m pytest
```

## Build

Remove previous build artefacts first, then run:

```bash
python -m build
python -m twine check dist/*
python scripts/verify_distribution.py dist
```


## License

MIT.

## Citation

If you use this work in your research, please cite:

```bibtex
@software{becanovic2026mujoco,
  author  = {Be{\v{c}}anovi{\'c}, Filip and Mi{\v{s}}kovi{\'c}, Du{\v{s}}an and Nedeljkovi{\'c}, Kosta and Tepav{\v{c}}evi{\'c}, Marko},
  title   = {{mujoco-biomechanics}: Anthropometrically Scaled Human Models for {MuJoCo}},
  year    = {2026},
  url     = {https://github.com/Beca-Filip/mujoco-biomechanics}
}
```
