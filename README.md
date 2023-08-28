[![CI](https://github.com/spacetelescope/roman_datamodels/actions/workflows/ci.yml/badge.svg)](https://github.com/spacetelescope/roman_datamodels/actions/workflows/ci.yml)
[![Weekly Cron](https://github.com/spacetelescope/roman_datamodels/actions/workflows/ci_cron.yml/badge.svg)](https://github.com/spacetelescope/roman_datamodels/actions/workflows/ci_cron.yml)
[![codecov](https://codecov.io/gh/spacetelescope/roman_datamodels/branch/main/graph/badge.svg)](https://codecov.io/gh/spacetelescope/roman_datamodels)
[![Documentation Status](https://readthedocs.org/projects/roman-datamodels/badge/?version=latest)](https://roman-datamodels.readthedocs.io/en/latest/?badge=latest)

# Roman Datamodels Support

## Installation

The easiest way to install the latest `roman-datamodels` release into a fresh virtualenv or conda environment is

    pip install roman-datamodels

### Detailed Installation

The `roman-datamodels` package can be installed into a virtualenv or conda environment via `pip`. We recommend that for each
installation you start by creating a fresh environment that only has Python installed and then install the `roman_datamodels`
package and its dependencies into that bare environment. If using conda environments, first make sure you have a recent
version of Anaconda or Miniconda installed. If desired, you can create multiple environments to allow for switching
between different versions of the `roman-datamodels` package (e.g. a released version versus the current development version).

In all cases, the installation is generally a 3-step process:

* Create a conda environment
* Activate that environment
* Install the desired version of the `roman-datamodels` package into that environment

Details are given below on how to do this for different types of installations, including tagged releases, DMS builds
used in operations, and development versions. Remember that all conda operations must be done from within a bash shell.

### Installing latest releases

You can install the latest released version via `pip`. From a bash shell:

    conda create -n <env_name> python
    conda activate <env_name>
    pip install roman-datamodels

> **Note**\
> Alternatively, you can also use `virtualenv` to create an environment;
> however, this installation method is not supported by STScI if you encounter issues.

You can also install a specific version (from `roman-datamodels 0.1.0` onward):

    conda create -n <env_name> python
    conda activate <env_name>
    pip install roman-datamodels==0.5.0

### Installing the development version from Github

You can install the latest development version (not as well tested) from the Github main branch:

    conda create -n <env_name> python
    conda activate <env_name>
    pip install git+https://github.com/spacetelescope/roman_datamodels

### Installing for Developers

If you want to be able to work on and test the source code with the `roman-datamodels` package, the high-level procedure to do
this is to first create a conda environment using the same procedures outlined above, but then install your personal
copy of the code overtop of the original code in that environment. Again, this should be done in a separate conda
environment from any existing environments that you may have already installed with released versions of the `roman-datamodels`
package.

As usual, the first two steps are to create and activate an environment:

    conda create -n <env_name> python
    conda activate <env_name>

To install your own copy of the code into that environment, you first need to fork and clone the `roman_datamodels` repo:

    cd <where you want to put the repo>
    git clone https://github.com/spacetelescope/roman_datamodels
    cd roman_datamodels

> **Note**\
> Installing via `setup.py` (`python setup.py install`, `python setup.py develop`, etc.) is deprecated and does not work.

Install from your local checked-out copy as an "editable" install:

    pip install -e .

If you want to run the unit or regression tests and/or build the docs, you can make sure those dependencies are
installed too:

    pip install -e ".[test]"
    pip install -e ".[docs]"
    pip install -e ".[test,docs]"

Need other useful packages in your development environment?

    pip install ipython pytest-xdist
