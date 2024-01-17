import sys
from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext
from setuptools.command.sdist import sdist


def _run_generator():
    """Run the generator"""
    roman_datamodels = Path(__file__).parent / "src"
    sys.path.append(str(roman_datamodels))

    from roman_datamodels.generator import setup_files

    setup_files()


class PostBuildExtCommand(build_ext):
    """Post-installation for extension."""

    def run(self):
        _run_generator()
        super().run()


class PostSDistCommand(sdist):
    """Post-installation for source distribution."""

    def run(self):
        super().run()
        _run_generator()


setup(
    cmdclass={
        "build_ext": PostBuildExtCommand,
        "sdist": PostSDistCommand,
    },
    ext_modules=[
        Extension(
            "roman_datamodels.datamodels._generated",
            [],
        ),
    ],
)
