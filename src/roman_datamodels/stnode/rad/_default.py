from astropy.coordinates import ICRS
from astropy.modeling.models import Pix2Sky_TAN, RotateNative2Celestial, Scale, Shift  # type: ignore[attr-defined]
from astropy.units import deg, pix  # type: ignore[attr-defined]
from gwcs import WCS, coordinate_frames

__all__ = [
    "NOFN",
    "NOINT",
    "NONUM",
    "NOSTR",
    "Wcs",
]


NOFN = "none"
NOSTR = "?"
NONUM = -999999.0
NOINT = int(NONUM)


def Wcs() -> WCS:
    # Astropy has not implemented type hints for modeling so MyPy will complain about this
    # until they do.
    pixelshift = Shift(-500) & Shift(-500)  # type: ignore[no-untyped-call, operator]
    # 0.1 arcsec/pixel
    pixelscale = Scale(0.1 / 3600.0) & Scale(0.1 / 3600.0)  # type: ignore[no-untyped-call, operator]
    tangent_projection = Pix2Sky_TAN()
    celestial_rotation = RotateNative2Celestial(30.0, 45.0, 180.0)  # type: ignore[no-untyped-call]

    det2sky = pixelshift | pixelscale | tangent_projection | celestial_rotation

    # GWCS has not implemented type hints so MyPy will complain about this
    # until they do.
    detector_frame = coordinate_frames.Frame2D(name="detector", axes_names=("x", "y"), unit=(pix, pix))  # type: ignore[no-untyped-call]

    # GWCS has not implemented type hints so MyPy will complain about this
    # until they do.
    # Astropy has not implemented type hints for coordinates so MyPy will complain about this
    # until they do.
    sky_frame = coordinate_frames.CelestialFrame(reference_frame=ICRS(), name="icrs", unit=(deg, deg))  # type: ignore[no-untyped-call]

    # GWCS has not implemented type hints so MyPy will complain about this
    # until they do.
    return WCS(  # type: ignore[no-untyped-call]
        [
            (detector_frame, det2sky),
            (sky_frame, None),
        ]
    )
