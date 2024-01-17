import sys
from pathlib import Path

from setuptools import setup


def _run_generator():
    """Run the generator"""
    roman_datamodels = Path(__file__).parent / "src"
    sys.path.append(str(roman_datamodels))

    from roman_datamodels.generator import setup_files

    setup_files()


_run_generator()
setup()
