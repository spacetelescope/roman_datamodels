from roman_datamodels.core import DataModel  # noqa: F403, F401
from roman_datamodels.core import open  # noqa: F403, F401

# Import all the data model objects
#    In a try/except, block to catch when when the generated code is not available
#    such as when the generator is run during installation.
try:
    from ._generated import *  # noqa: F403
except ImportError:
    import warnings

    warnings.warn("Failed to import the data model objects, re-run the generator or reinstall the package.")
