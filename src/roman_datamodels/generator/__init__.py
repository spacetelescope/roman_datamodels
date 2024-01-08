"""
The RomanDataModel automatic code generation module.
"""
__all__ = ["setup_files"]

try:
    import datamodel_code_generator  # noqa: F401
except ImportError as err:
    raise ImportError("datamodel-code-generator is required to use the generator.") from err

from ._generator import setup_files
