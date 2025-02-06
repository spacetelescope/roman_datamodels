import numpy as np
import numpy.typing as npt
from astropy.time import Time

from roman_datamodels.stnode import rad

from .meta import (
    Common,
    GuidewindowModes,
)

__all__ = ["Guidewindow", "Guidewindow_Meta"]


class Guidewindow_Meta(rad.ImpliedNodeMixin, Common):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return Guidewindow

    @rad.field
    def gw_start_time(self) -> Time:
        # Astropy has not implemented type hints for Time so MyPy will complain about this
        # until they do.
        return Time("2020-01-01T00:00:00.0", format="isot", scale="utc")  # type: ignore[no-untyped-call]

    @rad.field
    def gw_end_time(self) -> Time:
        # Astropy has not implemented type hints for Time so MyPy will complain about this
        # until they do.
        return Time("2020-01-01T10:00:00.0", format="isot", scale="utc")  # type: ignore[no-untyped-call]

    @rad.field
    def gw_frame_readout_time(self) -> float:
        return rad.NONUM

    @rad.field
    def gw_function_start_time(self) -> Time:
        # Astropy has not implemented type hints for Time so MyPy will complain about this
        # until they do.
        return Time("2020-01-01T00:00:00.0", format="isot", scale="utc")  # type: ignore[no-untyped-call]

    @rad.field
    def gw_function_end_time(self) -> Time:
        # Astropy has not implemented type hints for Time so MyPy will complain about this
        # until they do.
        return Time("2020-01-01T00:00:00.0", format="isot", scale="utc")  # type: ignore[no-untyped-call]

    @rad.field
    def gw_acq_exec_stat(self) -> str:
        return "StatusRMTest619"

    @rad.field
    def pedestal_resultant_exp_time(self) -> float:
        return rad.NONUM

    @rad.field
    def signal_resultant_exp_time(self) -> float:
        return rad.NONUM

    @rad.field
    def gw_acq_number(self) -> int:
        return rad.NOINT

    @rad.field
    def gw_science_file_source(self) -> str:
        return rad.NOSTR

    @rad.field
    def gw_mode(self) -> GuidewindowModes:
        return GuidewindowModes.WIM_ACQ

    @rad.field
    def gw_window_xstart(self) -> int:
        return rad.NOINT

    @rad.field
    def gw_window_ystart(self) -> int:
        return rad.NOINT

    @rad.field
    def gw_window_xstop(self) -> int:
        return self.gw_window_xstart + self.gw_window_xsize

    @rad.field
    def gw_window_ystop(self) -> int:
        return self.gw_window_xstart + self.gw_window_ysize

    @rad.field
    def gw_window_xsize(self) -> int:
        return 170

    @rad.field
    def gw_window_ysize(self) -> int:
        return 24


class Guidewindow(rad.TaggedObjectNode, rad.ArrayFieldMixin):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/guidewindow-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/guidewindow-1.0.0",
        }

    @property
    def primary_array_name(self) -> str:
        """Primary array name"""
        return "signal_frames"

    @property
    def default_array_shape(self) -> tuple[int, int, int, int, int]:
        """Default shape of the data array"""
        return (2, 8, 16, 32, 32)

    @property
    def testing_array_shape(self) -> tuple[int, int, int, int, int]:
        """Shape of the data array for testing"""
        return (2, 2, 2, 2, 2)

    @rad.field
    def meta(self) -> Guidewindow_Meta:
        return Guidewindow_Meta()

    @rad.field
    def pedestal_frames(self) -> npt.NDArray[np.uint16]:
        return np.zeros(self.array_shape, dtype=np.uint16)

    @rad.field
    def signal_frames(self) -> npt.NDArray[np.uint16]:
        return np.zeros(self.array_shape, dtype=np.uint16)

    @rad.field
    def amp33(self) -> npt.NDArray[np.uint16]:
        return np.zeros(self.array_shape, dtype=np.uint16)
