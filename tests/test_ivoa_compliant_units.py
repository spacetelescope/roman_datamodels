"""
Unit tests for IVOA-compliant unit conversion and Parquet export functionality.
"""

import pathlib
import tempfile

import numpy as np
import pyarrow.parquet as pq
import pytest
from astropy import units as u
from astropy.table import Table

from roman_datamodels.datamodels._utils import (
    create_synchronized_table,
    parse_units_to_ivoa,
)


class TestParseUnitsToIVOA:
    """Test suite for parse_units_to_ivoa function."""

    def test_standard_units(self):
        """Test conversion of standard physical units."""
        input_units = ["m", "m/s", "kg", "erg/(cm2 s Angstrom)"]
        result = parse_units_to_ivoa(input_units)

        assert result[0] == "m"
        assert result[1] == "m.s**-1"
        assert result[2] == "kg"
        # Complex unit conversion - vounit format converts to IVOA standard representation
        # erg/(cm2 s Angstrom) -> 10g.nm**-1.s**-3 in IVOA vounit format
        assert result[3] == "10g.nm**-1.s**-3"

    def test_magnitude_units(self):
        """Test conversion of magnitude units (FunctionUnitBase)."""
        input_units = ["mag", "mag(AB)", "mag(ST)"]
        result = parse_units_to_ivoa(input_units)

        # All magnitude units should map to "mag"
        assert all(unit == "mag" for unit in result)

    def test_dimensionless_units(self):
        """Test handling of dimensionless/null unit representations."""
        input_units = [None, "", "unitless", "None", "UNITLESS"]
        result = parse_units_to_ivoa(input_units)

        # All should map to IVOA dimensionless "1"
        assert all(unit == "1" for unit in result)

    def test_invalid_units_fallback(self):
        """Test that invalid units fall back to '1' with warning."""
        input_units = ["invalid_unit_xyz", "not-a-unit"]

        with pytest.warns(UserWarning, match="Could not parse unit"):
            result = parse_units_to_ivoa(input_units)

        # Invalid units should fallback to "1"
        assert all(unit == "1" for unit in result)

    def test_mixed_units(self):
        """Test a realistic mix of unit types."""
        input_units = ["m/s", None, "mag", "erg/s", "", "invalid", "Jy"]

        # Suppress warning for invalid unit
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            result = parse_units_to_ivoa(input_units)

        assert result[0] == "m.s**-1"  # Standard unit
        assert result[1] == "1"  # None
        assert result[2] == "mag"  # Magnitude
        assert result[3] == "cm**2.g.s**-3"  # erg/s in IVOA vounit format
        assert result[4] == "1"  # Empty string
        assert result[5] == "1"  # Invalid (with warning)
        assert result[6] == "Jy"  # Jansky

    def test_astropy_unit_objects(self):
        """Test with Astropy Unit objects (as strings)."""
        input_units = [
            str(u.meter),
            str(u.m / u.s),
            str(u.erg / (u.cm**2 * u.s * u.Angstrom)),
        ]
        result = parse_units_to_ivoa(input_units)

        assert result[0] == "m"
        assert result[1] == "m.s**-1"
        # erg/(cm2 s Angstrom) -> 10g.nm**-1.s**-3 in IVOA vounit format
        assert result[2] == "10g.nm**-1.s**-3"

    def test_empty_list(self):
        """Test with empty input list."""
        result = parse_units_to_ivoa([])
        assert result == []


class TestCreateSynchronizedTable:
    """Test suite for create_synchronized_table function."""

    def test_basic_table_creation(self):
        """Test basic table creation without IVOA compliance."""
        import pyarrow as pa

        arrs = [np.array([1, 2, 3]), np.array([4.0, 5.0, 6.0])]
        names = ["col1", "col2"]
        units = ["m", "m/s"]
        dtypes = [pa.int64(), pa.float64()]

        table = create_synchronized_table(arrs, names, units, dtypes, global_meta=None, ivoa_compliant=False)

        assert table.num_columns == 2
        assert table.num_rows == 3
        assert table.column_names == ["col1", "col2"]

        # Check field metadata
        assert table.schema.field("col1").metadata[b"unit"] == b"m"
        assert table.schema.field("col2").metadata[b"unit"] == b"m/s"

    def test_ivoa_compliant_table(self):
        """Test table creation with IVOA compliance enabled."""
        import pyarrow as pa

        arrs = [np.array([1, 2, 3]), np.array([4.0, 5.0, 6.0])]
        names = ["col1", "col2"]
        units = ["m/s", None]  # None should convert to "1"
        dtypes = [pa.int64(), pa.float64()]

        table = create_synchronized_table(arrs, names, units, dtypes, global_meta=None, ivoa_compliant=True)

        # Check IVOA-compliant units
        assert table.schema.field("col1").metadata[b"unit"] == b"m.s**-1"
        assert table.schema.field("col2").metadata[b"unit"] == b"1"

    def test_with_descriptions(self):
        """Test table creation with column descriptions."""
        import pyarrow as pa

        arrs = [np.array([1, 2, 3])]
        names = ["col1"]
        units = ["m"]
        dtypes = [pa.int64()]
        descriptions = ["This is a test column"]

        table = create_synchronized_table(
            arrs, names, units, dtypes, global_meta=None, ivoa_compliant=False, descriptions=descriptions
        )

        # Descriptions should be in Astropy YAML metadata
        assert b"table_meta_yaml" in table.schema.metadata
        yaml_str = table.schema.metadata[b"table_meta_yaml"].decode()
        assert "This is a test column" in yaml_str

    def test_with_global_metadata(self):
        """Test preservation of global metadata."""
        import pyarrow as pa

        arrs = [np.array([1, 2, 3])]
        names = ["col1"]
        units = ["m"]
        dtypes = [pa.int64()]
        global_meta = {"instrument": "WFI", "filter": "F158"}

        table = create_synchronized_table(arrs, names, units, dtypes, global_meta=global_meta, ivoa_compliant=False)

        # Global metadata should be preserved (as bytes)
        assert b"instrument" in table.schema.metadata
        assert table.schema.metadata[b"instrument"] == b"WFI"

    def test_with_table_metadata(self):
        """Test preservation of table-level metadata."""
        import pyarrow as pa

        arrs = [np.array([1, 2, 3])]
        names = ["col1"]
        units = ["m"]
        dtypes = [pa.int64()]
        table_meta = {"aperture_radii": [1.0, 2.0, 3.0], "ee_fractions": [0.5, 0.7, 0.9]}

        table = create_synchronized_table(
            arrs, names, units, dtypes, global_meta=None, ivoa_compliant=False, table_meta=table_meta
        )

        # Table metadata should be in YAML
        yaml_str = table.schema.metadata[b"table_meta_yaml"].decode()
        assert "aperture_radii" in yaml_str
        assert "ee_fractions" in yaml_str

    def test_empty_units(self):
        """Test handling of empty unit strings."""
        import pyarrow as pa

        arrs = [np.array([1, 2, 3])]
        names = ["col1"]
        units = [""]  # Empty unit
        dtypes = [pa.int64()]

        table = create_synchronized_table(arrs, names, units, dtypes, global_meta=None, ivoa_compliant=False)

        # Empty units should not create metadata
        assert table.schema.field("col1").metadata == {}


class TestParquetRoundTrip:
    """Test round-trip preservation of data and metadata through Parquet files."""

    @pytest.fixture
    def temp_parquet_file(self):
        """Provide a temporary Parquet file path."""
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            filepath = pathlib.Path(f.name)
        yield filepath
        # Cleanup
        if filepath.exists():
            filepath.unlink()

    def test_basic_roundtrip(self, temp_parquet_file):
        """Test basic round-trip without IVOA compliance."""
        import pyarrow as pa
        import pyarrow.parquet as pq

        # Create test data
        arrs = [np.array([1, 2, 3]), np.array([4.0, 5.0, 6.0])]
        names = ["int_col", "float_col"]
        units = ["m", "m/s"]
        dtypes = [pa.int64(), pa.float64()]

        # Create and save table
        table = create_synchronized_table(
            arrs, names, units, dtypes, global_meta={"test_key": "test_value"}, ivoa_compliant=False
        )
        pq.write_table(table, temp_parquet_file)

        # Read back
        loaded_table = pq.read_table(temp_parquet_file)

        # Verify data
        assert loaded_table.num_rows == 3
        assert loaded_table.column_names == ["int_col", "float_col"]
        np.testing.assert_array_equal(loaded_table["int_col"].to_numpy(), [1, 2, 3])
        np.testing.assert_array_equal(loaded_table["float_col"].to_numpy(), [4.0, 5.0, 6.0])

        # Verify metadata
        assert loaded_table.schema.field("int_col").metadata[b"unit"] == b"m"
        assert loaded_table.schema.field("float_col").metadata[b"unit"] == b"m/s"
        assert loaded_table.schema.metadata[b"test_key"] == b"test_value"

    def test_ivoa_roundtrip(self, temp_parquet_file):
        """Test round-trip with IVOA compliance enabled."""
        import pyarrow as pa
        import pyarrow.parquet as pq

        # Create test data with mixed units
        arrs = [np.array([1, 2, 3]), np.array([4.0, 5.0, 6.0]), np.array([7.0, 8.0, 9.0])]
        names = ["velocity", "magnitude", "dimensionless"]
        units = ["m/s", "mag", None]
        dtypes = [pa.int64(), pa.float64(), pa.float64()]

        # Create and save table with IVOA compliance
        table = create_synchronized_table(arrs, names, units, dtypes, global_meta=None, ivoa_compliant=True)
        pq.write_table(table, temp_parquet_file)

        # Read back
        loaded_table = pq.read_table(temp_parquet_file)

        # Verify IVOA-compliant units
        assert loaded_table.schema.field("velocity").metadata[b"unit"] == b"m.s**-1"
        assert loaded_table.schema.field("magnitude").metadata[b"unit"] == b"mag"
        assert loaded_table.schema.field("dimensionless").metadata[b"unit"] == b"1"

    def test_astropy_table_roundtrip(self, temp_parquet_file):
        """Test round-trip through Astropy Table."""
        import pyarrow as pa

        # Create test data
        arrs = [np.array([1, 2, 3]), np.array([4.0, 5.0, 6.0])]
        names = ["col1", "col2"]
        units = ["m/s", "erg/s"]
        dtypes = [pa.int64(), pa.float64()]
        descriptions = ["Velocity column", "Energy flux column"]

        # Create table with IVOA compliance
        table = create_synchronized_table(
            arrs, names, units, dtypes, global_meta=None, ivoa_compliant=True, descriptions=descriptions
        )
        pq.write_table(table, temp_parquet_file)

        # Read back as Astropy Table
        loaded_astropy = Table.read(temp_parquet_file)

        # Verify data
        assert len(loaded_astropy) == 3
        np.testing.assert_array_equal(loaded_astropy["col1"], [1, 2, 3])
        np.testing.assert_array_equal(loaded_astropy["col2"], [4.0, 5.0, 6.0])

        # Verify units (Astropy should parse them)
        assert loaded_astropy["col1"].unit is not None
        assert loaded_astropy["col2"].unit is not None

    def test_metadata_preservation(self, temp_parquet_file):
        """Test comprehensive metadata preservation."""
        import pyarrow as pa

        # Create test data with all metadata types
        arrs = [np.array([1, 2, 3])]
        names = ["test_col"]
        units = ["m"]
        dtypes = [pa.int64()]
        global_meta = {"instrument": "WFI", "filter": "F158", "exposure_time": "100.5"}
        table_meta = {"aperture_radii": [1.0, 2.0, 3.0], "processing_level": "L2"}
        descriptions = ["Test column with metadata"]

        # Create and save
        table = create_synchronized_table(
            arrs,
            names,
            units,
            dtypes,
            global_meta=global_meta,
            ivoa_compliant=False,
            descriptions=descriptions,
            table_meta=table_meta,
        )
        pq.write_table(table, temp_parquet_file)

        # Read back
        loaded_table = pq.read_table(temp_parquet_file)

        # Verify all metadata types
        assert loaded_table.schema.metadata[b"instrument"] == b"WFI"
        assert loaded_table.schema.metadata[b"filter"] == b"F158"
        assert b"table_meta_yaml" in loaded_table.schema.metadata

        yaml_str = loaded_table.schema.metadata[b"table_meta_yaml"].decode()
        assert "aperture_radii" in yaml_str
        assert "processing_level" in yaml_str
        assert "Test column with metadata" in yaml_str


class TestBackwardCompatibility:
    """Test backward compatibility of the changes."""

    def test_default_ivoa_compliant_false(self):
        """Test that ivoa_compliant defaults to False."""
        import pyarrow as pa

        arrs = [np.array([1, 2, 3])]
        names = ["col1"]
        units = ["m/s"]  # Should NOT be converted to IVOA format
        dtypes = [pa.int64()]

        # Call without ivoa_compliant parameter (should default to False)
        table = create_synchronized_table(arrs, names, units, dtypes, global_meta=None)

        # Unit should be unchanged (not IVOA-converted)
        assert table.schema.field("col1").metadata[b"unit"] == b"m/s"

    def test_none_handling_backward_compatible(self):
        """Test that None units are handled gracefully."""
        import pyarrow as pa

        arrs = [np.array([1, 2, 3])]
        names = ["col1"]
        units = [None]
        dtypes = [pa.int64()]

        # Without IVOA compliance, None should become empty string
        table = create_synchronized_table(arrs, names, units, dtypes, global_meta=None, ivoa_compliant=False)

        # No metadata should be set for empty units
        assert table.schema.field("col1").metadata == {}


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_mismatched_array_lengths(self):
        """Test behavior with mismatched input lengths."""
        import pyarrow as pa

        arrs = [np.array([1, 2, 3]), np.array([4, 5])]  # Different lengths
        names = ["col1", "col2"]
        units = ["m", "m/s"]
        dtypes = [pa.int64(), pa.int64()]

        # PyArrow should raise an error for mismatched array lengths
        with pytest.raises((ValueError, pa.lib.ArrowInvalid)):
            create_synchronized_table(arrs, names, units, dtypes, global_meta=None)

    def test_special_characters_in_units(self):
        """Test handling of special characters in unit strings."""
        input_units = ["m^2", "kg*m/s^2", "erg/(cm^2*s*Angstrom)"]
        result = parse_units_to_ivoa(input_units)

        # Should handle special characters gracefully
        assert len(result) == 3
        assert all(isinstance(unit, str) for unit in result)

    def test_unicode_in_metadata(self):
        """Test handling of unicode characters in metadata."""
        import pyarrow as pa

        arrs = [np.array([1, 2, 3])]
        names = ["col1"]
        units = ["µm"]  # Micrometer with unicode
        dtypes = [pa.int64()]

        table = create_synchronized_table(arrs, names, units, dtypes, global_meta=None, ivoa_compliant=False)

        # Should handle unicode properly
        assert b"\xc2\xb5m" in table.schema.field("col1").metadata[b"unit"]
