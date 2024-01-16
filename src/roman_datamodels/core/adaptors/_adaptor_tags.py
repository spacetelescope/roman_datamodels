"""
This module contains the tags needed for third party ASDF related types to be supported
by Pydantic.
"""
__all__ = ["asdf_tags"]

import sys

if sys.version_info < (3, 11):
    from strenum import StrEnum
else:
    from enum import StrEnum


class asdf_tags(StrEnum):
    """ASDF tags needed to support roman datamodels."""

    ASTROPY_TIME = "tag:stsci.edu:asdf/time/time-*"

    # There are two tags for units, one for astropy (non-standard units) and one for asdf (standard units).
    ASTROPY_UNIT = "tag:astropy.org:astropy/units/unit-*"
    ASDF_UNIT = "tag:stsci.edu:asdf/unit/unit-*"

    ASTROPY_QUANTITY = "tag:stsci.edu:asdf/unit/quantity-*"

    ND_ARRAY = "tag:stsci.edu:asdf/core/ndarray-*"

    @staticmethod
    def get_tag_key(value: str) -> str:
        """
        Courtesy of https://stackoverflow.com/a/1176023

        Parameters
        ----------
        value : str
            The value to convert to a tag key (this may not be in the enum)
        """
        import re

        return re.sub(r"(?<!^)(?=[A-Z])", "_", value).upper()
