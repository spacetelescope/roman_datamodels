from astropy.time import Time

from roman_datamodels.stnode import rad

from ..scalars import GuidewindowModes

__all__ = ["Guidestar"]


class Guidestar(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/guidestar-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/guidestar-1.0.0"
        }

    @rad.field
    def guide_window_id(self) -> str:
        return rad.NOSTR

    @rad.field
    def guide_mode(self) -> GuidewindowModes:
        return GuidewindowModes.WSM_ACQ_2

    @rad.field
    def data_start(self) -> Time:
        # Astropy has not implemented type hints for Time so MyPy will complain about this
        # until they do.
        return Time("2020-01-01T00:00:00.0", format="isot", scale="utc")  # type: ignore[no-untyped-call]

    @rad.field
    def data_end(self) -> Time:
        # Astropy has not implemented type hints for Time so MyPy will complain about this
        # until they do.
        return Time("2020-01-01T01:00:00.0", format="isot", scale="utc")  # type: ignore[no-untyped-call]

    @rad.field
    def window_xstart(self) -> int:
        return rad.NOINT

    @rad.field
    def window_ystart(self) -> int:
        return rad.NOINT

    @rad.field
    def window_xstop(self) -> int:
        return self.window_xstart + self.window_xsize

    @rad.field
    def window_ystop(self) -> int:
        return self.window_ystart + self.window_ysize

    @rad.field
    def window_xsize(self) -> int:
        return 170

    @rad.field
    def window_ysize(self) -> int:
        return 24

    @rad.field
    def guide_star_id(self) -> str:
        return rad.NOSTR

    @rad.field
    def gsc_version(self) -> str:
        return rad.NOSTR

    @rad.field
    def ra(self) -> float:
        return rad.NONUM

    @rad.field
    def dec(self) -> float:
        return rad.NONUM

    @rad.field
    def ra_uncertainty(self) -> float:
        return rad.NONUM

    @rad.field
    def dec_uncertainty(self) -> float:
        return rad.NONUM

    @rad.field
    def fgs_magnitude(self) -> float:
        return rad.NONUM

    @rad.field
    def fgs_magnitude_uncertainty(self) -> float:
        return rad.NONUM

    @rad.field
    def centroid_x(self) -> float:
        return rad.NONUM

    @rad.field
    def centroid_y(self) -> float:
        return rad.NONUM

    @rad.field
    def centroid_x_uncertainty(self) -> float:
        return rad.NONUM

    @rad.field
    def centroid_y_uncertainty(self) -> float:
        return rad.NONUM

    @rad.field
    def epoch(self) -> str:
        return rad.NOSTR

    @rad.field
    def proper_motion_ra(self) -> float:
        return rad.NONUM

    @rad.field
    def proper_motion_dec(self) -> float:
        return rad.NONUM

    @rad.field
    def parallax(self) -> float:
        return rad.NONUM

    @rad.field
    def centroid_rms(self) -> float:
        return rad.NONUM
