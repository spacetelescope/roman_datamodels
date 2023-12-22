import sys
from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext


class PostBuildExtCommand(build_ext):
    """Post-installation for extension."""

    def run(self):
        roman_datamodels = Path(__file__).parent / "src"
        sys.path.append(str(roman_datamodels))

        from roman_datamodels.pydantic.generator import setup_files

        setup_files()


setup(
    cmdclass={
        "build_ext": PostBuildExtCommand,
    },
    ext_modules=[
        Extension(
            "roman_datamodels.pydantic._generated",
            [],
        ),
    ],
)
