"""
These tests are to confirm that L2 files conform to expectations
of the mission operations center (MOC). Additional expectations
are covered in RAD tests (which is the preferred way to check that
files conform to expectations). Any changes that impact these
expectations must be coordinated with the MOC.
"""

import asdf
import numpy as np

from roman_datamodels.datamodels import ImageModel


def test_l2_compression(tmp_path):
    """
    Test that L2 files use lz4 compression.
    """
    fn = tmp_path / "test.asdf"
    ImageModel.create_fake_data().save(fn)

    compression_codes = set()
    with asdf.open(fn, lazy_load=False) as af:
        for node in af.search(type_=np.ndarray).nodes:
            compression_codes.add(af.get_array_compression(node))

    assert compression_codes == {"lz4"}
