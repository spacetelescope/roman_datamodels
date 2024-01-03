from pathlib import Path

from roman_datamodels.pydantic.parser import RadSchemaParser
from roman_datamodels.pydantic.parser._utils import get_rad_schema_path
from roman_datamodels.pydantic.parser._writer import write_files


def generate_files(
    write_path: Path,
    version: str | None = None,
    use_timestamp: bool = True,
):
    schema_path = get_rad_schema_path(version)
    parsed_results = RadSchemaParser(schema_path).parse()
    write_files(write_path, parsed_results, version, use_timestamp)


def setup_files():
    write_path = Path(__file__).parent / "_generated"
    write_path.mkdir(exist_ok=True)

    generate_files(write_path, use_timestamp=False)


if __name__ == "__main__":
    setup_files()
