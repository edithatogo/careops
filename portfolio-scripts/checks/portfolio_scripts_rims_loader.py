"""Load the standalone RIMS source contract without importing a package tree."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def load_contract():
    file = Path(__file__).resolve().parents[1] / "rims_review_contract.py"
    spec = spec_from_file_location("rims_review_contract", file)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
