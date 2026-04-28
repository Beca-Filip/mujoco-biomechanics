# mujoco-biomechanics

A Python tool for generating anatomically scaled human musculoskeletal models for the [MuJoCo](https://mujoco.org/) physics simulator.

Given a subject's **mass**, **height**, and **sex**, the generator produces a full-body MuJoCo XML model with:

- Segment geometry, mass, and centre-of-mass positions scaled from anthropometric tables (de Leva, 1996)
- Full inertia tensors (radii of gyration + products of inertia)
- Anatomical joint limits for all degrees of freedom
- Pre-configured contact exclusions and floor contact parameters

## Quick start

```bash
pip install -r requirements.txt

# Generate a model
python generate_human_model.py --mass 75 --height 1.80 --sex male --output subject.xml

# Visualise
python run_model.py subject.xml
```

## Citation

If you use this work in your research, please cite:

```bibtex
@software{beca2026mujoco,
  author  = {Be{\v{c}}anovi{\'c}, Filip and Mi{\v{s}}kovi{\'c}, Du{\v{s}}an and Nedeljkovi{\'c}, Kosta and Tepav{\v{c}}evi{\'c}, Marko},
  title   = {{mujoco-biomechanics}: Anthropometrically Scaled Human Models for {MuJoCo}},
  year    = {2026},
  url     = {https://github.com/becaphilippe/mujoco-biomechanics}
}
```

## Reference

de Leva, P. (1996). Adjustments to Zatsiorsky-Seluyanov's segment inertia parameters.
*Journal of Biomechanics*, 29(9), 1223–1230.
