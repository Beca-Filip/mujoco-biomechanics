# mujoco-biomechanics

A Python tool for generating anatomically scaled human skeletal models for the [MuJoCo](https://mujoco.org/) physics simulator.

Given a subject's **mass**, **height**, and **sex**, the generator produces a full-body MuJoCo XML model with:

- Segment geometry, mass, and centre-of-mass positions scaled from anthropometric tables (de Leva, 1996)
- Full inertia tensors (radii of gyration + products of inertia)
- Anatomical joint limits for all degrees of freedom
- Pre-configured contact exclusions and floor contact parameters

## Model topology

The generated model consists of 16 rigid bodies connected in a branching kinematic tree. The thorax is the root body and connects to the world through a free joint. All other joints are implemented using one, two, or three hinge joints.

**Table 1. Body-segment topology of the generated model.** DOF denotes degrees of freedom.

| # | Segment | Parent | Joint type | DOF |
| ---: | --- | --- | --- | ---: |
| 1 | `thorax` | `world` | Free | 6 |
| 2 | `head` | `thorax` | Hinge (3×) | 3 |
| 3 | `abdomen` | `thorax` | Hinge (3×) | 3 |
| 4 | `pelvis` | `abdomen` | Hinge (3×) | 3 |
| 5 | `left_thigh` | `pelvis` | Hinge (3×) | 3 |
| 6 | `left_shank` | `left_thigh` | Hinge (1×) | 1 |
| 7 | `left_foot` | `left_shank` | Hinge (2×) | 2 |
| 8 | `right_thigh` | `pelvis` | Hinge (3×) | 3 |
| 9 | `right_shank` | `right_thigh` | Hinge (1×) | 1 |
| 10 | `right_foot` | `right_shank` | Hinge (2×) | 2 |
| 11 | `left_upper_arm` | `thorax` | Hinge (3×) | 3 |
| 12 | `left_forearm` | `left_upper_arm` | Hinge (1×) | 1 |
| 13 | `left_hand` | `left_forearm` | Hinge (2×) | 2 |
| 14 | `right_upper_arm` | `thorax` | Hinge (3×) | 3 |
| 15 | `right_forearm` | `right_upper_arm` | Hinge (1×) | 1 |
| 16 | `right_hand` | `right_forearm` | Hinge (2×) | 2 |
| | **Total** | | | **33 + 6 = 39** |

The model has 33 internal rotational DOFs and 6 root DOFs (3 translations and 3 rotations). Each elbow and knee is a single hinge, while each shoulder uses three stacked hinges. The model is a rigid-body approximation and contains no muscles.

<!-- BEGIN GENERATED SITE TABLE -->
## Anatomical sites

The current generator defines 78 sites, including anatomical landmarks, joint centres, and centre-of-mass reference sites. Table 2 lists their exact model identifiers and parent segments. Numbers follow the row order in `src/mujoco_biomechanics/data/site_positions_male.csv`; they are documentation labels, not MuJoCo site IDs. The female CSV defines the same site names and parent segments.

**Table 2. Complete site inventory of the generated model.** Existing identifiers, including `symphision` and `olecranion`, are preserved exactly as stored in the CSV.

| # | Site name | Segment | Anatomical landmark / reference point |
| ---: | --- | --- | --- |
| 1 | `seventh_cervicale` | `thorax` | Seventh cervical vertebra (C7) |
| 2 | `suprasternale` | `thorax` | Suprasternal notch |
| 3 | `right_acromion` | `thorax` | Right acromion |
| 4 | `left_acromion` | `thorax` | Left acromion |
| 5 | `right_shoulder_joint_centre` | `thorax` | Right shoulder joint centre |
| 6 | `left_shoulder_joint_centre` | `thorax` | Left shoulder joint centre |
| 7 | `thoracic_joint_centre` | `thorax` | Thoracic joint centre |
| 8 | `centre_of_mass_thorax` | `thorax` | Thorax centre of mass (reference site) |
| 9 | `midspine_at_tenth_rib_level` | `abdomen` | Midline of the spine at the tenth-rib level |
| 10 | `right_tenth_rib` | `abdomen` | Right tenth rib |
| 11 | `left_tenth_rib` | `abdomen` | Left tenth rib |
| 12 | `right_iliocristale` | `abdomen` | Right iliac crest |
| 13 | `left_iliocristale` | `abdomen` | Left iliac crest |
| 14 | `lumbar_joint_centre` | `abdomen` | Lumbar joint centre |
| 15 | `centre_of_mass_abdomen` | `abdomen` | Abdomen centre of mass (reference site) |
| 16 | `midpoint_between_postero_superior_iliac_spines` | `pelvis` | Midpoint between the posterior superior iliac spines |
| 17 | `right_anterior_superior_iliac_spine` | `pelvis` | Right anterior superior iliac spine (ASIS) |
| 18 | `left_anterior_superior_iliac_spine` | `pelvis` | Left anterior superior iliac spine (ASIS) |
| 19 | `symphision` | `pelvis` | Pubic symphysis |
| 20 | `right_hip_joint_centre` | `pelvis` | Right hip joint centre |
| 21 | `left_hip_joint_centre` | `pelvis` | Left hip joint centre |
| 22 | `centre_of_mass_pelvis` | `pelvis` | Pelvis centre of mass (reference site) |
| 23 | `head_vertex` | `head` | Vertex of the head |
| 24 | `sellion` | `head` | Sellion (nasal-root landmark) |
| 25 | `occiput` | `head` | Occiput (back of the head) |
| 26 | `centre_of_mass_head` | `head` | Head centre of mass (reference site) |
| 27 | `right_lateral_humeral_epicondyle` | `right_upper_arm` | Right lateral humeral epicondyle |
| 28 | `left_lateral_humeral_epicondyle` | `left_upper_arm` | Left lateral humeral epicondyle |
| 29 | `right_medial_humeral_epicondyle` | `right_upper_arm` | Right medial humeral epicondyle |
| 30 | `left_medial_humeral_epicondyle` | `left_upper_arm` | Left medial humeral epicondyle |
| 31 | `right_centre_of_mass_upper_arm` | `right_upper_arm` | Right upper arm centre of mass (reference site) |
| 32 | `left_centre_of_mass_upper_arm` | `left_upper_arm` | Left upper arm centre of mass (reference site) |
| 33 | `right_olecranion` | `right_forearm` | Right olecranon |
| 34 | `left_olecranion` | `left_forearm` | Left olecranon |
| 35 | `right_ulnar_styloid` | `right_forearm` | Right ulnar styloid process |
| 36 | `left_ulnar_styloid` | `left_forearm` | Left ulnar styloid process |
| 37 | `right_radial_styloid` | `right_forearm` | Right radial styloid process |
| 38 | `left_radial_styloid` | `left_forearm` | Left radial styloid process |
| 39 | `right_centre_of_mass_forearm` | `right_forearm` | Right forearm centre of mass (reference site) |
| 40 | `left_centre_of_mass_forearm` | `left_forearm` | Left forearm centre of mass (reference site) |
| 41 | `right_second_metacarpal_head` | `right_hand` | Right head of the second metacarpal |
| 42 | `left_second_metacarpal_head` | `left_hand` | Left head of the second metacarpal |
| 43 | `right_fifth_metacarpal_head` | `right_hand` | Right head of the fifth metacarpal |
| 44 | `left_fifth_metacarpal_head` | `left_hand` | Left head of the fifth metacarpal |
| 45 | `right_third_finger_tip` | `right_hand` | Right tip of the third (middle) finger |
| 46 | `left_third_finger_tip` | `left_hand` | Left tip of the third (middle) finger |
| 47 | `right_centre_of_mass_hand` | `right_hand` | Right hand centre of mass (reference site) |
| 48 | `left_centre_of_mass_hand` | `left_hand` | Left hand centre of mass (reference site) |
| 49 | `right_greater_trochanter` | `right_thigh` | Right greater trochanter of the femur |
| 50 | `left_greater_trochanter` | `left_thigh` | Left greater trochanter of the femur |
| 51 | `right_lateral_femoral_epicondyle` | `right_thigh` | Right lateral femoral epicondyle |
| 52 | `left_lateral_femoral_epicondyle` | `left_thigh` | Left lateral femoral epicondyle |
| 53 | `right_medial_femoral_epicondyle` | `right_thigh` | Right medial femoral epicondyle |
| 54 | `left_medial_femoral_epicondyle` | `left_thigh` | Left medial femoral epicondyle |
| 55 | `right_centre_of_mass_thigh` | `right_thigh` | Right thigh centre of mass (reference site) |
| 56 | `left_centre_of_mass_thigh` | `left_thigh` | Left thigh centre of mass (reference site) |
| 57 | `right_tibiale_head` | `right_shank` | Right tibial-head landmark |
| 58 | `left_tibiale_head` | `left_shank` | Left tibial-head landmark |
| 59 | `right_fibula_head` | `right_shank` | Right head of the fibula |
| 60 | `left_fibula_head` | `left_shank` | Left head of the fibula |
| 61 | `right_sphyrion` | `right_shank` | Right sphyrion (medial malleolar landmark) |
| 62 | `left_sphyrion` | `left_shank` | Left sphyrion (medial malleolar landmark) |
| 63 | `right_lateral_malleolus` | `right_shank` | Right lateral malleolus |
| 64 | `left_lateral_malleolus` | `left_shank` | Left lateral malleolus |
| 65 | `right_centre_of_mass_shank` | `right_shank` | Right shank centre of mass (reference site) |
| 66 | `left_centre_of_mass_shank` | `left_shank` | Left shank centre of mass (reference site) |
| 67 | `right_calcaneus` | `right_foot` | Right calcaneus (heel) |
| 68 | `left_calcaneus` | `left_foot` | Left calcaneus (heel) |
| 69 | `right_first_metatarsal_head` | `right_foot` | Right head of the first metatarsal |
| 70 | `left_first_metatarsal_head` | `left_foot` | Left head of the first metatarsal |
| 71 | `right_fifth_metatarsal_head` | `right_foot` | Right head of the fifth metatarsal |
| 72 | `left_fifth_metatarsal_head` | `left_foot` | Left head of the fifth metatarsal |
| 73 | `right_second_toe_tip` | `right_foot` | Right tip of the second toe |
| 74 | `left_second_toe_tip` | `left_foot` | Left tip of the second toe |
| 75 | `right_centre_of_mass_foot` | `right_foot` | Right foot centre of mass (reference site) |
| 76 | `left_centre_of_mass_foot` | `left_foot` | Left foot centre of mass (reference site) |
| 77 | `right_metatarsal_midpoint` | `right_foot` | Right metatarsal midpoint reference site |
| 78 | `left_metatarsal_midpoint` | `left_foot` | Left metatarsal midpoint reference site |

Regenerate this section from the repository root after changing the site CSV:

```bash
python scripts/generate_readme_sites.py
```
<!-- END GENERATED SITE TABLE -->

## Requirements

- Python 3.10 or newer
- MuJoCo 3.3.4 or newer

## Installation

```bash
python -m pip install mujoco-biomechanics
```

## Generate a model

```bash
mjb-generate --mass 75 --tall 1.82 --sex male --output male.xml
```

```bash
mjb-generate --mass 60 --tall 1.68 --sex female --alpha 0.8 --output female.xml
```

## Inspect a model

```bash
mjb-inspect male.xml
```
## Build a combined scene

Save without opening the viewer:

```bash
mjb-run-scene male.xml female.xml --number-of-columns 2 --spacing 1.5 --output scene.xml --save-only
```

Save and open the viewer:

```bash
mjb-run-scene male.xml female.xml --number-of-columns 2 --spacing 1.5 --output scene.xml
```

Press Space in the viewer to pause or resume simulation.

### macOS viewer note

MuJoCo's passive viewer must be started through `mjpython` on macOS:

```bash
mjpython -m mujoco_biomechanics.run_model male.xml female.xml --output scene.xml
```

## Python API

```python
from mujoco_biomechanics.generate_human_model import generate_human_model

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
## Issues

Report problems: https://github.com/Beca-Filip/mujoco-biomechanics/issues

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
