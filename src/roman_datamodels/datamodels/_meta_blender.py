from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Any

import numpy as np
from asdf import get_config
from asdf.lazy_nodes import AsdfDictNode, AsdfListNode
from asdf.schema import load_schema
from astropy.table import Table
from astropy.time import Time
from semantic_version import Version

from roman_datamodels.stnode import DNode

if TYPE_CHECKING:
    from ._datamodels import DataModel

__all__ = ("ImageModelBlender",)


class _MissingCellType:
    """A clear signal that a cell is missing data"""

    def __str__(self):
        return "MISSING_CELL"


# Create a singleton that will be used in every missing cell
_MISSING_CELL = _MissingCellType()


def _default_factory():
    """Factory function for the SchemaTable defaults dict"""
    return _MISSING_CELL


class _SchemaTable:
    """
    Class to help turn the structure described by a RAD schema into a table that
    multiple images can have that structure from their metadata merged into.
    """

    def __init__(self, names: tuple[str, ...], defaults: dict[str, Any] | None = None):
        self._names = names

        # Make the _defaults a dict that returns MISSING_CELL for any missing key
        self._defaults: dict[str, Any] = defaultdict(_default_factory)
        # Now if we have any provided defaults, update the dict with them
        if defaults:
            self._defaults.update(defaults)

        # Set up the column storage
        self._columns: dict[str, list[Any]] = {name: [] for name in names}

    def reset(self) -> None:
        """
        Reset the table to an empty state
        """
        self._columns = {name: [] for name in self._names}

    @classmethod
    def from_rad_schema(cls, uri: str, defaults: dict[str, Any] | None = None) -> _SchemaTable:
        """Initialize a SchemaTable from a RAD schema URI

        Parameters
        ----------
        uri
            The URI of the RAD schema to load
        defaults
            A dictionary of default values to use if a value is missing from the data model node

        Returns
        -------
            A SchemeTable instance with columns based on the schema
        """
        return cls(tuple(load_schema(uri)["properties"].keys()), defaults=defaults)

    def _sanitize_value(self, value: Any) -> Any:
        if isinstance(value, list | dict | AsdfDictNode | AsdfListNode):
            return str(value)
        return value

    def add_row(self, node: DNode):
        """
        Extract a row of data from a data model node based on the columns
        defined in the schema

        Parameters
        ----------
        node
            The data model node to extract the row from

        Returns
        -------
            A tuple of values for each column in the schema
        """
        for name in self._names:
            self._columns[name].append(self._sanitize_value(node.get(name, self._defaults[name])))

    @staticmethod
    def _sanitize_column(column: list[Any]) -> list[Any]:
        """
        Sanitize the extracted column of data to ensure it can be written to an Astropy Table by ASDF
        """
        # If the column has no missing values, return it as-is
        if len(clean_column := [value for value in column if value not in (_MISSING_CELL, None)]) == len(column):
            return column

        # If the column has no valid values its size will be falsey
        #  fill it with "None"
        if not (clean_array := np.array(clean_column)).size:
            return ["None"] * len(column)

        # If the column is numeric as determined by numpy, fill missing values with NaN
        if clean_array.dtype.kind in ("f", "i"):
            return [np.nan if value in (_MISSING_CELL, None) else value for value in column]

        # If all else fails, convert everything to a string
        return [str(value) for value in column]

    def create_table(self) -> Table:
        """
        Create an Astropy Table from the collected rows
        """
        return Table({name: self._sanitize_column(column) for name, column in self._columns.items()})


class _MetaBlender:
    """
    Class to help merge the metadata from multiple images into a collection of tables
    """

    def __init__(self, schema_tables: dict[str, _SchemaTable]):
        self._schema_tables = schema_tables
        self._n_models = 0

        # Note this is just a convenience variable to help with computing the mean
        #   time across a collection of images.
        self.start_times: list[Time] = []

    def reset(self) -> None:
        """
        Reset the MetaBlender to an empty state
        """
        for table in self._schema_tables.values():
            table.reset()

        self._n_models = 0
        self.start_times = []

    @classmethod
    def from_rad_schema(cls, uri: str, defaults: dict[str, dict[str, Any] | None] | None = None) -> _MetaBlender:
        """
        Create a MetaBlender from a RAD schema that contains multiple table definitions

        Parameters
        ----------
        uri
            The URI of the RAD schema to load

        Returns
        -------
            A MetaBlender instance with tables based on the schema
        """
        defaults = defaults or {}

        tables = {}
        # Loop over the tables defined in the schema and create a schema for each table based on the
        #   individual_schema entry's referenced for that table
        for name, entry in load_schema(uri)["properties"].items():
            if "individual_schema" not in entry:
                raise ValueError(f"Schema for table {name} does not have an individual_schema")
            tables[name] = _SchemaTable.from_rad_schema(entry["individual_schema"], defaults=defaults.get(name))

        return cls(tables)

    @property
    def n_models(self) -> int:
        """
        The number of models that have been added to the MetaBlender
        """
        return self._n_models

    def add_image(self, image: DataModel) -> None:
        """
        Add the metadata from an image to the appropriate tables

        Parameters
        ----------
        image
            The ImageModel instance to extract metadata from
        """
        if not hasattr(image, "meta"):
            raise ValueError("Image does not have a meta attribute")

        for name, table in self._schema_tables.items():
            table.add_row(image.meta.get(name, image.meta))

        self._n_models += 1

    def create_tables(self) -> dict[str, Table]:
        """
        Create Astropy Tables from the collected rows for each table

        Returns
        -------
            A dictionary of Astropy Tables, keyed by table name
        """
        return {name: table.create_table() for name, table in self._schema_tables.items()}

    def mean_time(self) -> Time:
        """
        Compute the mean start time of all added images

        Returns
        -------
            The mean start time, or None if no images have been added
        """
        return Time(self.start_times).mean()


def ImageModelBlender():
    """
    Blend multiple ImageModel instances into a single representation

        This is for the `individual_image_meta` sechema

    Returns
    -------
        A _MetaBlender instance configured for blending ImageModel metadata
    """
    base_uri = "asdf://stsci.edu/datamodels/roman/schemas/meta/individual_image_meta"

    # Find the latest version of the individual_image_meta schema, this should be okay even if
    #   the newest version has new tables or will cause existing tables to have new columns as
    #   the add_row method for the tables will fill in missing columns with MISSING_CELL
    candidate_uri = None
    for schema_uri in get_config().resource_manager:
        if schema_uri.startswith(base_uri) and Version(schema_uri.rsplit("-", 1)[-1]) > Version(
            "0.0.0" if candidate_uri is None else candidate_uri.rsplit("-", 1)[-1]
        ):
            candidate_uri = schema_uri

    return _MetaBlender.from_rad_schema(candidate_uri)
