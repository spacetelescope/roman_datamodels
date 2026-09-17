"""Roman Data Quality Flags

Within science data files, the PIXELDQ flags are stored as 32-bit integers;
the GROUPDQ flags are 8-bit integers. All calibrated data from a particular
instrument and observing mode have the same set of DQ flags in the same (bit)
order. Additional details can be found in the
:external+romancal:ref:`romancal data quality flags documentation <data_quality_flags>`.

Tables detailing the specifics of the GROUPDQ and PIXELDQ flags are provided in
the documentation for `group` and `pixel` respectively.

Implementation
--------------

The flags are implemented as "bit flags": Each flag is assigned a bit position
in a byte, or multi-byte word, of memory. If that bit is set, the flag assigned
to that bit is interpreted as being set or active.

NumPy can do bitwise operations on these integer flags, provided they are of an
unsigned integer type. For our case:

* GROUPDQ (`group` enum) flags are stored as 8-bit unsigned integers (`~numpy.uint8`).
* PIXELDQ (`pixel` enum) flags are stored as 32-bit unsigned integers (`~numpy.uint32`).

The actual integer values for each flag are found using the formula
``2**bit_number`` where ``bit_number`` is the 0-index bit of interest.

The flags for both ``pixel`` and ``group`` dq flags are defined as enumerations,
so that they are both organized in a consistent manner and protected against accidental
modification. This means they can be accessed like any attribute of a Python `~enum.Enum`.
"""

from enum import Enum, unique

import numpy as np

__all__ = ["group", "pixel"]


class _DqFlagMixin:
    @property
    def bit_number(self):
        """The bit position represented by this flag, or ``None`` for ``GOOD``."""
        if self.value == 0:
            return None
        return int(self.value).bit_length() - 1


# fmt: off
@unique
class pixel(np.uint32, _DqFlagMixin, Enum):
    """Pixel-specific, PIXELDQ, data quality flags"""

    GOOD             = 0
    """No bits set, all is good"""
    DO_NOT_USE       = 2**0
    """Bad pixel. Do not use"""
    SATURATED        = 2**1
    """Pixel saturated during exposure"""
    JUMP_DET         = 2**2
    """Jump detected during exposure"""
    DROPOUT          = 2**3
    """Data lost in transmission"""
    GW_AFFECTED_DATA = 2**4
    """Data affected by the GW read window"""
    PERSISTENCE      = 2**5
    """High persistence (was RESERVED_2)"""
    AD_FLOOR         = 2**6
    """Below A/D floor (0 DN, was RESERVED_3)"""
    OUTLIER          = 2**7
    """Flagged by outlier detection (was RESERVED_4)"""
    UNRELIABLE_ERROR = 2**8
    """Uncertainty exceeds quoted error"""
    NON_SCIENCE      = 2**9
    """Pixel not on science portion of detector"""
    DEAD             = 2**10
    """Dead pixel"""
    HOT              = 2**11
    """Hot pixel"""
    WARM             = 2**12
    """Warm pixel"""
    LOW_QE           = 2**13
    """Low quantum efficiency"""
    TELEGRAPH        = 2**15
    """Telegraph pixel"""
    NONLINEAR        = 2**16
    """Pixel highly nonlinear"""
    BAD_REF_PIXEL    = 2**17
    """Reference pixel cannot be used"""
    NO_FLAT_FIELD    = 2**18
    """Flat field cannot be measured"""
    NO_GAIN_VALUE    = 2**19
    """Gain cannot be measured"""
    NO_LIN_CORR      = 2**20
    """Linearity correction not available"""
    NO_SAT_CHECK     = 2**21
    """Saturation check not available"""
    UNRELIABLE_BIAS  = 2**22
    """Bias variance large"""
    UNRELIABLE_DARK  = 2**23
    """Dark variance large"""
    UNRELIABLE_SLOPE = 2**24
    """Slope variance large (i.e., noisy pixel)"""
    UNRELIABLE_FLAT  = 2**25
    """Flat variance large"""
    RESERVED_5       = 2**26
    """Reserved"""
    RESERVED_6       = 2**27
    """Reserved"""
    UNRELIABLE_RESET = 2**28
    """Sensitive to reset anomaly"""
    RESERVED_7       = 2**29
    """Reserved"""
    OTHER_BAD_PIXEL  = 2**30
    """A catch-all flag"""
    REFERENCE_PIXEL  = 2**31
    """Pixel is a reference pixel"""


@unique
class group(np.uint8, _DqFlagMixin, Enum):
    """
    Group-specific, GROUPDQ, data quality flags

    Once groups are combined, these flags are equivalent to the pixel-specific flags.
    """

    GOOD       = pixel.GOOD
    """No bits set, all is good"""
    DO_NOT_USE = pixel.DO_NOT_USE
    """Bad pixel. Do not use"""
    SATURATED  = pixel.SATURATED
    """Pixel saturated during exposure"""
    JUMP_DET   = pixel.JUMP_DET
    """Jump detected during exposure"""
    DROPOUT    = pixel.DROPOUT
    """Data lost in transmission"""
    AD_FLOOR   = pixel.AD_FLOOR
    """Below A/D floor (0 DN, was RESERVED_3)"""
    WFI18_TRANSIENT = 2**7
    """Affected by the WFI18 transient anomaly"""

# fmt: on
