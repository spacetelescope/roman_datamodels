import sys

if sys.version_info < (3, 11):
    from strenum import StrEnum
else:
    from enum import StrEnum


class asdf_tags(StrEnum):
    """ASDF tags needed to support roman datamodels."""

    ASTROPY_TIME = "tag:stsci.edu:asdf/time/time-1.1.0"

    # There are two tags for units, one for astropy (non-standard units) and one for asdf (standard units).
    ASTROPY_UNIT = "tag:astropy.org:astropy/units/unit-1.0.0"
    ASDF_UNIT = "tag:stsci.edu:asdf/unit/unit-1.0.0"

    ASTROPY_QUANTITY = "tag:stsci.edu:asdf/unit/quantity-1.1.0"

    ND_ARRAY = "tag:stsci.edu:asdf/core/ndarray-1.0.0"
