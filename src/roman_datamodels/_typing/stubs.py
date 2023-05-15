import importlib.util as util
import sys
from pathlib import Path

from roman_datamodels.stnode import registration_off

path = Path(__file__).parent / "stnode.py"
spec = util.spec_from_file_location("roman_datamodels.stnode_stubs", str(path))
stubs = util.module_from_spec(spec)
sys.modules["roman_datamodels.stnode_stubs"] = stubs

with registration_off():
    spec.loader.exec_module(stubs)
