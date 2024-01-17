__all__ = [
    "__version__",
    "DataModel",
    "open",
]

# When run from setup.py, we need to import the generator to run it
#   This means importing roman_datamodels.generator will import this __init__.py
#   _version.py is generated near the end of the setup.py process so it will not
#   exist at the time the generator is run. This try/except block allows the
#   generator to import during the setup.py process without the _version.py file
try:
    from ._version import version as __version__
except ImportError:
    import warnings

    warnings.warn(
        "Setup.py is running the generator, _version.py is not available.\n"
        "If this is not the case, reinstall roman_datamodels",
        ImportWarning,
    )

    __version__ = "unknown"

from .datamodels import DataModel, open
