"""
Module for all the code to activate the code generation
"""
__all__ = ["setup_files"]

from pathlib import Path

from ._parser import RadSchemaParser
from ._utils import get_rad_schema_path
from ._writer import write_files


def setup_files(write_path: Path | None = None):
    """
    Setup the pydantic models from the schemas.

    Effects
    -------
    Setup all the generated files
    """
    if write_path is None:
        write_path = Path(__file__).parent.parent / "datamodels" / "_generated"
        write_path.mkdir(exist_ok=True)

    _generate_files(write_path, use_timestamp=False)


def _generate_files(
    write_path: Path,
    version: str | None = None,
    use_timestamp: bool = True,
):
    """
    Generate the pydantic models from the schemas.

    Parameters
    ----------
    write_path: Path
        The path to write the generated files to.
    version: str, optional
        The version of the schemas being used.
    use_timestamp: bool, optional
        If we timestamp the output files.

    Effects
    -------
    Parses the schemas and writes them to files.
    """
    schema_path = get_rad_schema_path(version)
    parsed_results = RadSchemaParser(schema_path).parse()
    write_files(write_path, parsed_results, version, use_timestamp)
