from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias, TypeVar

from astropy.coordinates import ICRS
from astropy.modeling.models import Pix2Sky_TAN, RotateNative2Celestial, Scale, Shift  # type: ignore[attr-defined]
from astropy.units import deg, pix  # type: ignore[attr-defined]
from gwcs import WCS, coordinate_frames

if TYPE_CHECKING:
    from roman_datamodels.nodes import FpsModelType, ModelType, TvacModelType

    MdlType: TypeAlias = ModelType | FpsModelType | TvacModelType

__all__ = [
    "NOFN",
    "NOINT",
    "NONUM",
    "NOSTR",
    "Wcs",
    "default_model_type",
]

_T = TypeVar("_T")


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
    return WCS(
        [
            (detector_frame, det2sky),
            (sky_frame, None),
        ]
    )


def default_model_type(self: _T, node: type[MdlType]) -> MdlType:
    """
    Create a model_type
    """

    from roman_datamodels.stnode import RDM_NODE_REGISTRY, ImpliedNodeMixin

    if isinstance(self, ImpliedNodeMixin):
        return node(RDM_NODE_REGISTRY.node_datamodel_mapping[self.asdf_implied_by].__name__)

    return node.default()
