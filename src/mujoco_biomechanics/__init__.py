from importlib.metadata import PackageNotFoundError, version
from .generate_human_model import generate_human_model
from .mjinspect import inspect_model
from .run_model import build_combined_xml

try:
    __version__ = version("mujoco-biomechanics")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "__version__",
    "generate_human_model",
    "inspect_model",
    "build_combined_xml",
]
