from roman_datamodels.stnode import FlushOptions


def mk_exposure(**kwargs):
    """
    Create a dummy Exposure instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Exposure
    """
    from roman_datamodels.nodes import Exposure

    exposure = Exposure(kwargs)
    exposure.flush(FlushOptions.EXTRA, recurse=True)
    return exposure


def mk_wfi_mode(**kwargs):
    """
    Create a dummy WFI mode instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.WfiMode
    """
    from roman_datamodels.nodes import WfiMode

    mode = WfiMode(kwargs)
    mode.flush(FlushOptions.EXTRA, recurse=True)

    return mode


def mk_program(**kwargs):
    """
    Create a dummy Program instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Program
    """
    from roman_datamodels.nodes import Program

    prog = Program(kwargs)
    prog.flush(FlushOptions.EXTRA, recurse=True)

    return prog


def mk_observation(**kwargs):
    """
    Create a dummy Observation instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Observation
    """
    from roman_datamodels.nodes import Observation

    obs = Observation(kwargs)
    obs.flush(FlushOptions.EXTRA, recurse=True)

    return obs


def mk_outlier_detection(**kwargs):
    """
    Create a dummy Outlier Detection instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.OutlierDetection
    """
    from roman_datamodels.nodes import OutlierDetection

    od = OutlierDetection(kwargs)
    od.flush(FlushOptions.EXTRA, recurse=True)

    return od


def mk_sky_background(**kwargs):
    """
    Create a dummy Sky Background instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.SkyBackground
    """
    from roman_datamodels.nodes import SkyBackground

    sb = SkyBackground(kwargs)
    sb.flush(FlushOptions.EXTRA, recurse=True)

    return sb


def mk_ephemeris(**kwargs):
    """
    Create a dummy Ephemeris instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Ephemeris
    """
    from roman_datamodels.nodes import Ephemeris

    ephem = Ephemeris(kwargs)
    ephem.flush(FlushOptions.EXTRA, recurse=True)

    return ephem


def mk_visit(**kwargs):
    """
    Create a dummy Visit instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Visit
    """
    from roman_datamodels.nodes import Visit

    visit = Visit(kwargs)
    visit.flush(FlushOptions.EXTRA, recurse=True)

    return visit


def mk_coordinates(**kwargs):
    """
    Create a dummy Coordinates instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Coordinates
    """
    from roman_datamodels.nodes import Coordinates

    coord = Coordinates(kwargs)
    coord.flush(FlushOptions.EXTRA, recurse=True)

    return coord


def mk_pointing(**kwargs):
    """
    Create a dummy Pointing instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Pointing
    """
    from roman_datamodels.nodes import Pointing

    point = Pointing(kwargs)
    point.flush(FlushOptions.EXTRA, recurse=True)

    return point


def mk_velocity_aberration(**kwargs):
    """
    Create a dummy Velocity Aberration instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.VelocityAberration
    """
    from roman_datamodels.nodes import VelocityAberration

    vab = VelocityAberration(kwargs)
    vab.flush(FlushOptions.EXTRA, recurse=True)

    return vab


def mk_wcsinfo(**kwargs):
    """
    Create a dummy WCS Info instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Wcsinfo
    """
    from roman_datamodels.nodes import Wcsinfo

    wcsi = Wcsinfo(kwargs)
    wcsi.flush(FlushOptions.EXTRA, recurse=True)

    return wcsi


def mk_l2_cal_step(**kwargs):
    """
    Create a dummy Level 2 Cal Step instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.L2CalStep
    """
    from roman_datamodels.nodes import L2CalStep

    l2calstep = L2CalStep()
    l2calstep.flush(FlushOptions.EXTRA, recurse=True)

    return l2calstep


def mk_l3_cal_step(**kwargs):
    """
    Create a dummy Level 3 Cal Step instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.L3CalStep
    """
    from roman_datamodels.nodes import L3CalStep

    l3calstep = L3CalStep()
    l3calstep.flush(FlushOptions.EXTRA, recurse=True)

    return l3calstep


def mk_guidestar(**kwargs):
    """
    Create a dummy Guidestar instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Guidestar
    """
    from roman_datamodels.nodes import Guidestar

    guide = Guidestar(kwargs)
    guide.flush(FlushOptions.EXTRA, recurse=True)

    return guide


def mk_ref_file(**kwargs):
    """
    Create a dummy RefFile instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.RefFile
    """
    from roman_datamodels.nodes import RefFile

    ref_file = RefFile(kwargs)
    ref_file.flush(FlushOptions.EXTRA, recurse=True)

    return ref_file


def mk_common_meta(**kwargs):
    """
    Create a dummy common metadata dictionary with valid values for attributes

    Returns
    -------
    dict (defined by the common-1.0.0 schema)
    """
    from roman_datamodels.nodes import Common

    meta = Common(kwargs)
    meta.flush(FlushOptions.EXTRA, recurse=True)

    return meta


def mk_l2_meta(**kwargs):
    """
    Create a dummy common metadata dictionary with valid values for attributes and add
    the additional photometry metadata

    Returns
    -------
    dict (defined by the common-1.0.0 schema with additional photometry metadata)
    """
    from roman_datamodels.nodes.datamodels.wfi_image import WfiImage_Meta

    meta = WfiImage_Meta(kwargs)
    meta.flush(FlushOptions.EXTRA, recurse=True)

    return meta


def mk_ramp_meta(**kwargs):
    """
    Create a dummy common metadata dictionary with valid values for attributes and add
    the additional photometry metadata

    Returns
    -------
    dict (defined by the common-1.0.0 schema with additional photometry metadata)
    """
    from roman_datamodels.nodes.datamodels.ramp import Ramp_Meta

    meta = Ramp_Meta(kwargs)
    meta.flush(FlushOptions.EXTRA, recurse=True)

    return meta


def mk_mosaic_meta(**kwargs):
    """
    Create a dummy metadata dictionary with valid values for mosaic attributes.

    Returns
    -------
    dict (defined by the wfi_mosaic-1.0.0 schema)
    """
    from roman_datamodels.nodes.datamodels.wfi_mosaic import WfiMosaic_Meta

    meta = WfiMosaic_Meta(kwargs)
    meta.flush(FlushOptions.EXTRA, recurse=True)

    return meta


def mk_mosaic_associations(**kwargs):
    """
    Create a dummy mosaic associations instance with valid values for
    mosaic associations attributes. Utilized by the model maker utilities.

    Returns
    -------
    roman_datamodels.stnode.MosaicAssociations
    """
    from roman_datamodels.nodes import MosaicAssociations

    mosasn = MosaicAssociations(kwargs)
    mosasn.flush(FlushOptions.EXTRA, recurse=True)

    return mosasn


def mk_guidewindow_meta(**kwargs):
    """
    Create a dummy common metadata dictionary with valid values for attributes and add
    the additional guidewindow metadata

    Returns
    -------
    dict (defined by the common-1.0.0 schema with additional guidewindow metadata)
    """

    from roman_datamodels.nodes.datamodels.guidewindow import GuideWindow_Meta

    meta = GuideWindow_Meta(kwargs)
    meta.flush(FlushOptions.EXTRA, recurse=True)

    return meta


def mk_msos_stack_meta(**kwargs):
    """
    Create a dummy common metadata dictionary with valid values for attributes and add
    the additional msos_stack metadata

    Returns
    -------
    dict (defined by the common-1.0.0 schema with additional guidewindow metadata)
    """

    from roman_datamodels.nodes.datamodels.msos_stack import MsosStack_Meta

    meta = MsosStack_Meta(kwargs)
    meta.flush(FlushOptions.EXTRA, recurse=True)

    return meta


def mk_rcs(**kwargs):
    """
    Create a dummy Relative Calibration System instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Rcs
    """
    from roman_datamodels.nodes import Rcs

    rcs = Rcs(kwargs)
    rcs.flush(FlushOptions.EXTRA, recurse=True)

    return rcs


def mk_statistics(**kwargs):
    """
    Create a dummy Statistical instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Statistics
    """

    from roman_datamodels.nodes import Statistics

    stats = Statistics(kwargs)
    stats.flush(FlushOptions.EXTRA, recurse=True)

    return stats


def mk_ref_common(reftype_, **kwargs):
    """
    Create dummy metadata for reference file instances.

    Returns
    -------
    dict (follows reference_file/ref_common-1.0.0 schema)
    """
    from roman_datamodels.nodes import RefCommonRef

    meta = RefCommonRef(kwargs)
    meta.flush(FlushOptions.EXTRA, recurse=True)

    return meta


def mk_ref_dark_meta(**kwargs):
    """
    Create dummy metadata for dark reference file instances.

    Returns
    -------
    dict (follows reference_file/ref_common-1.0.0 schema + dark reference file metadata)
    """
    from roman_datamodels.nodes.reference_files.dark import DarkRef_Meta

    meta = DarkRef_Meta(kwargs)
    meta.flush(FlushOptions.EXTRA, recurse=True)

    return meta


def mk_ref_epsf_meta(**kwargs):
    """
    Create dummy metadata for ePSF reference file instances.

    Returns
    -------
    dict (follows reference_file/ref_common-1.0.0 schema + ePSF reference file metadata)
    """
    from roman_datamodels.nodes.reference_files.epsf import EpsfRef_Meta

    meta = EpsfRef_Meta(kwargs)
    meta.flush(FlushOptions.EXTRA, recurse=True)

    return meta


def mk_ref_distoriton_meta(**kwargs):
    """
    Create dummy metadata for distortion reference file instances.

    Returns
    -------
    dict (follows reference_file/ref_common-1.0.0 schema + distortion reference file metadata)
    """
    from roman_datamodels.nodes.reference_files.distortion import DistortionRef_Meta

    meta = DistortionRef_Meta(kwargs)
    meta.flush(FlushOptions.EXTRA, recurse=True)

    return meta


def mk_ref_pixelarea_meta(**kwargs):
    """
    Create dummy metadata for pixelarea reference file instances.

    Returns
    -------
    dict (follows reference_file/ref_common-1.0.0 schema + pixelarea reference file metadata)
    """
    from roman_datamodels.nodes.reference_files.pixelarea import PixelAreaRef_Meta

    meta = PixelAreaRef_Meta(kwargs)
    meta.flush(FlushOptions.EXTRA, recurse=True)

    return meta


def mk_ref_readnoise_meta(**kwargs):
    """
    Create dummy metadata for readnoise reference file instances.

    Returns
    -------
    dict (follows reference_file/ref_common-1.0.0 schema + readnoise reference file metadata)
    """
    from roman_datamodels.nodes.reference_files.readnoise import ReadnoiseRef_Meta

    meta = ReadnoiseRef_Meta(kwargs)
    meta.flush(FlushOptions.EXTRA, recurse=True)

    return meta


def mk_mosaic_basic(**kwargs):
    """
    Create a dummy mosaic basic instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities.

    Returns
    -------
    roman_datamodels.stnode.MosaicBasic
    """
    from roman_datamodels.nodes import MosaicBasic

    mosbasic = MosaicBasic(kwargs)
    mosbasic.flush(FlushOptions.EXTRA, recurse=True)

    return mosbasic


def mk_mosaic_wcsinfo(**kwargs):
    """
    Create a dummy mosaic WCS Info instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities.

    Returns
    -------
    roman_datamodels.stnode.MosaicWcsinfo
    """
    from roman_datamodels.nodes import MosaicWcsinfo

    moswcsi = MosaicWcsinfo(kwargs)
    moswcsi.flush(FlushOptions.EXTRA, recurse=True)

    return moswcsi


def mk_individual_image_meta(**kwargs):
    """
    Create a dummy component image metadata storage instance for mosaics
    with valid values for attributes required by the schema.
    Utilized by the model maker utilities.

    Returns
    -------
    roman_datamodels.stnode.IndividualImageMeta
    """
    from roman_datamodels.nodes import IndividualImageMeta

    imm = IndividualImageMeta(kwargs)
    imm.flush(FlushOptions.EXTRA, recurse=True)

    return imm


def mk_mosaic_catalog_meta(**kwargs):
    """
    Create a dummy metadata dictionary with valid values for mosaic catalog.

    Returns
    -------
    dict (defined by the wfi_mosaic-1.0.0 schema)
    """
    from roman_datamodels.nodes.datamodels.mosaic_source_catalog import MosaicSourceCatalog_Meta

    meta = MosaicSourceCatalog_Meta(kwargs)
    meta.flush(FlushOptions.EXTRA, recurse=True)

    return meta


def mk_catalog_meta(**kwargs):
    """
    Create a dummy metadata dictionary with valid values for
    source catalog from Level 2 data.

    Returns
    -------
    dict (defined by the wfi_mosaic-1.0.0 schema)
    """
    from roman_datamodels.nodes.datamodels.image_source_catalog import ImageSourceCatalog_Meta

    meta = ImageSourceCatalog_Meta(kwargs)
    meta.flush(FlushOptions.EXTRA, recurse=True)

    return meta
