from asdf.extension import ManifestExtension
from .rconverters import (
	ExposureConverter, 
	WfiScienceRawConverter,
    WfiImageConverter,
    WfiModeConverter,
    ProgramConverter,
    ObservationConverter,
    EphemerisConverter,
    VisitConverter,
    PhotometryConverter,
    CoordinatesConverter,
    ApertureConverter,
    PointingConverter,
    TargetConverter,
    VelocityAberrationConverter,
    WcsinfoConverter,
    GuidestarConverter,
    CalStepConverter,
    FlatRefConverter,
)    

DATAMODEL_CONVERTERS = [
    ExposureConverter(),
    WfiModeConverter(),
    WfiImageConverter(),
    WfiScienceRawConverter(),
    WfiImageConverter(),
    ProgramConverter(),
    ObservationConverter(),
    EphemerisConverter(),
    VisitConverter(),
    PhotometryConverter(),
    CoordinatesConverter(),
    ApertureConverter(),
    PointingConverter(),
    TargetConverter(),
    VelocityAberrationConverter(),
    WcsinfoConverter(),
    GuidestarConverter(),
    CalStepConverter(),
    FlatRefConverter(),
]

DATAMODEL_EXTENSIONS = [
    ManifestExtension.from_uri(
        "http://stsci.edu/asdf/datamodels/roman/manifests/datamodels-1.0", 
    	converters=DATAMODEL_CONVERTERS)
]