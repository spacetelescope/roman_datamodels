import inspect

import asdf
import astropy.units as u
import pytest
from astropy.modeling.models import Shift
from astropy.units import Quantity
from mypy import nodes, options, parse
from numpy import random

from roman_datamodels import random_utils, stnode

RNG = random.default_rng(472)


def _GwMode(seed=None):
    choice = [
        "WIM-ACQ",
        "WIM-TRACK",
        "WSM-ACQ-1",
        "WSM-ACQ-2",
        "WSM-TRACK",
        "DEFOCUSED-MODERATE",
        "DEFOCUSED-LARGE",
    ]
    return random_utils.generate_choice(choice, seed=seed)


def _WfiDetector(seed=None):
    choice = [
        "WFI01",
        "WFI02",
        "WFI03",
        "WFI04",
        "WFI05",
        "WFI06",
        "WFI07",
        "WFI08",
        "WFI09",
        "WFI10",
        "WFI11",
        "WFI12",
        "WFI13",
        "WFI14",
        "WFI15",
        "WFI16",
        "WFI17",
        "WFI18",
    ]
    return random_utils.generate_choice(choice, seed=seed)


def _WfiOpticalElement(seed=None):
    choice = [
        "F062",
        "F087",
        "F106",
        "F129",
        "F146",
        "F158",
        "F184",
        "F213",
        "GRISM",
        "PRISM",
        "DARK",
    ]
    return random_utils.generate_choice(choice, seed=seed)


def _ExposureType(seed=None):
    choice = [
        "WFI_IMAGE",
        "WFI_GRISM",
        "WFI_PRISM",
        "WFI_DARK",
        "WFI_FLAT",
        "WFI_WFSC",
    ]
    return random_utils.generate_choice(choice, seed=seed)


def _ObservationSurvey(seed=None):
    choice = ["HLS", "EMS", "SN", "N/A"]
    return random_utils.generate_choice(choice, seed=seed)


def _EphemerisType(seed=None):
    choice = ["DEFINITIVE", "PREDICTED"]
    return random_utils.generate_choice(choice, seed=seed)


def _EngineeringQuality(seed=None):
    choice = ["OK", "SUSPECT"]
    return random_utils.generate_choice(choice, seed=seed)


def _PointingEngdbQuality(seed=None):
    choice = ["CALCULATED", "PLANNED"]
    return random_utils.generate_choice(choice, seed=seed)


def _ApertureName(seed=None):
    choice = [
        "WFI_01_FULL",
        "WFI_02_FULL",
        "WFI_03_FULL",
        "WFI_04_FULL",
        "WFI_05_FULL",
        "WFI_06_FULL",
        "WFI_07_FULL",
        "WFI_08_FULL",
        "WFI_09_FULL",
        "WFI_10_FULL",
        "WFI_11_FULL",
        "WFI_12_FULL",
        "WFI_13_FULL",
        "WFI_14_FULL",
        "WFI_15_FULL",
        "WFI_16_FULL",
        "WFI_17_FULL",
        "WFI_18_FULL",
        "BORESIGHT",
        "CGI_CEN",
        "WFI_CEN",
    ]
    return random_utils.generate_choice(choice, seed=seed)


def _TargetType(seed=None):
    choice = ["FIXED", "MOVING", "GENERIC"]
    return random_utils.generate_choice(choice, seed=seed)


def _TargetSourceType(seed=None):
    choice = ["EXTENDED", "POINT", "UNKNOWN"]
    return random_utils.generate_choice(choice, seed=seed)


def _CalStepVal(seed=None):
    choice = ["N/A", "COMPLETE", "SKIPPED", "INCOMPLETE"]
    return random_utils.generate_choice(choice, seed=seed)


def _Pedigree(seed=None):
    choice = ["GROUND", "MODEL", "DUMMY", "SIMULATION"]
    return random_utils.generate_choice(choice, seed=seed)


def _Origin(seed=None):
    choice = ["STSCI", "IPAC/SSC"]
    return random_utils.generate_choice(choice, seed=seed)


def _CalLogs(seed=None):
    return [random_utils.generate_string(seed=seed) for _ in range(10)]


def _AssociationProduct(seed=None):
    return {
        "name": random_utils.generate_string(seed=seed),
        "members": [random_utils.generate_string(seed=seed) for _ in range(10)],
    }


def _p_exptype(seed=None):
    choice = [
        "WFI_IMAGE",
        "WFI_GRISM",
        "WFI_PRISM",
        "WFI_DARK",
        "WFI_FLAT",
        "WFI_WFSC",
    ]
    components = random_utils.generate_choices(choice, k=3, seed=seed)
    return f"{'|'.join(components)}|"


def _ResampleWeightType(seed=None):
    choice = ["exptime", "ivm"]
    return random_utils.generate_choice(choice, seed=seed)


def _single_choice(choice):
    return choice


def _Model(seed=None):
    return Shift(random_utils.generate_float(seed=seed)) & Shift(random_utils.generate_float(seed=seed))


SEG_SHAPE = (2, 8, 16, 32, 32)
DATA_SHAPE = (2, 4096, 4096)
DQ_SHAPE = (4096, 4096)
BASE_TYPE_CREATE = {
    "Time": (lambda: random_utils.generate_astropy_time()),
    "float": (lambda: random_utils.generate_float()),
    "str": (lambda: random_utils.generate_string()),
    "int": (lambda: random_utils.generate_int()),
    "bool": (lambda: random_utils.generate_bool()),
    "CalLogs": (lambda: _CalLogs()),
    "_ndarray_uint8_3D": (lambda: random_utils.generate_array_uint8(size=DATA_SHAPE)),
    "_ndarray_uint16_2D": (lambda: random_utils.generate_array_uint16(size=DQ_SHAPE)),
    "_ndarray_uint16_3D": (lambda: random_utils.generate_array_uint16(size=DATA_SHAPE)),
    "_ndarray_uint32_2D": (lambda: random_utils.generate_array_uint32(size=DQ_SHAPE)),
    "_ndarray_uint32_3D": (lambda: random_utils.generate_array_uint32(size=DATA_SHAPE)),
    "_ndarray_float32_2D": (lambda: random_utils.generate_array_float32(size=DQ_SHAPE)),
    "_ndarray_float32_3D": (lambda: random_utils.generate_array_float32(size=DATA_SHAPE)),
    "_Quantity_uint16_DN_3D": (lambda: random_utils.generate_array_uint16(size=DATA_SHAPE, units=u.DN)),
    "_Quantity_uint16_DN_5D": (lambda: random_utils.generate_array_uint16(size=SEG_SHAPE, units=u.DN)),
    "_Quantity_float32_electron_2D": (lambda: random_utils.generate_array_float32(size=DQ_SHAPE, units=u.electron)),
    "_Quantity_float32_electron_3D": (lambda: random_utils.generate_array_float32(size=DATA_SHAPE, units=u.electron)),
    "_Quantity_float32_electron_DN_2D": (lambda: random_utils.generate_array_float32(size=DQ_SHAPE, units=u.electron / u.DN)),
    "_Quantity_float32_DN_2D": (lambda: random_utils.generate_array_float32(size=DQ_SHAPE, units=u.DN)),
    "_Quantity_float32_DN_3D": (lambda: random_utils.generate_array_float32(size=DATA_SHAPE, units=u.DN)),
    "_Quantity_float32_electron_s_2D": (lambda: random_utils.generate_array_float32(size=DQ_SHAPE, units=u.electron / u.s)),
    "_Quantity_float32_electron_s_3D": (lambda: random_utils.generate_array_float32(size=DATA_SHAPE, units=u.electron / u.s)),
    "_Quantity_float32_electron2_s2_2D": (
        lambda: random_utils.generate_array_float32(size=DQ_SHAPE, units=u.electron**2 / u.s**2)
    ),
    "_Quantity_float32_electron2_s2_3D": (
        lambda: random_utils.generate_array_float32(size=DATA_SHAPE, units=u.electron**2 / u.s**2)
    ),
    "_ApertureName": (lambda: _ApertureName()),
    "_AssociationProduct": (lambda: _AssociationProduct()),
    "_CalStepVal": (lambda: _CalStepVal()),
    "_GwMode": (lambda: _GwMode()),
    "_EngineeringQuality": (lambda: _EngineeringQuality()),
    "_EphemerisType": (lambda: _EphemerisType()),
    "_ExposureType": (lambda: _ExposureType()),
    "_ObservationSurvey": (lambda: _ObservationSurvey()),
    "_Pedigree": (lambda: _Pedigree()),
    "_PointingEngdbQuality": (lambda: _PointingEngdbQuality()),
    "_ResampleWeightType": (lambda: _ResampleWeightType()),
    "_TargetSourceType": (lambda: _TargetSourceType()),
    "_TargetType": (lambda: _TargetType()),
    "_WfiDetector": (lambda: _WfiDetector()),
    "_WfiOpticalElement": (lambda: _WfiOpticalElement()),
    "_p_exptype": (lambda: _p_exptype()),
    "_Origin": (lambda: _Origin()),
    "_WfiModeName": (lambda: _single_choice("WFI")),
    "_ReferenceFrame": (lambda: _single_choice("ICRS")),
    "_Telescope": (lambda: _single_choice("ROMAN")),
    "_DistortionInput": (lambda: _single_choice(u.pixel)),
    "_DistortionOutput": (lambda: _single_choice(u.arcsec)),
    "_DNunit": (lambda: _single_choice(u.DN)),
    "_DarkRefType": (lambda: _single_choice("DARK")),
    "_DistortionRefType": (lambda: _single_choice("DISTORTION")),
    "_FlatRefType": (lambda: _single_choice("FLAT")),
    "_GainRefType": (lambda: _single_choice("GAIN")),
    "_InverseLinearityRefType": (lambda: _single_choice("INVERSE_LINEARITY")),
    "_IpcRefType": (lambda: _single_choice("IPC")),
    "_LinearityRefType": (lambda: _single_choice("LINEARITY")),
    "_MaskRefType": (lambda: _single_choice("MASK")),
    "_PixelareaRefType": (lambda: _single_choice("AREA")),
    "_ReadnoiseRefType": (lambda: _single_choice("READNOISE")),
    "_SaturationRefType": (lambda: _single_choice("SATURATION")),
    "_SuperbiasRefType": (lambda: _single_choice("BIAS")),
    "_WfiImgPhotomRefType": (lambda: _single_choice("PHOTOM")),
    "Model": (lambda: _Model()),
}

SCALAR_NODES = {c.__name__: c for c in stnode._SCALAR_NODE_CLASSES_BY_TAG.values()}


def _handle_lnode(stub):
    if len(stub.args) == 1:
        length = RNG.integers(low=0, high=10)
        tree = []
        for _ in range(length):
            tree_ = _handle_base_type(stub.args[0])
            if tree_ is None:
                raise ValueError(f"Unhandled base class {stub.args[0].name}")
            tree.append(tree_)
        return tree
    else:
        raise ValueError(f"Unhandled lnode {stub}")


GET_UNIT = {
    "_MJy_per_sr": u.MJy / u.sr,
    "_uJy_per_arcsec2": u.uJy / u.arcsec**2,
    "_sr": u.sr,
    "_arcsec2": u.arcsec**2,
}


def _handle_optional_quantity(stub, seed=None):
    if random_utils.generate_bool(seed):
        return Quantity(random_utils.generate_float(seed), GET_UNIT[stub.args[0].name])
    return None


def _handle_base_type(stub):
    name = stub.name
    if name == "stnode.LNode":
        return _handle_lnode(stub)

    if name in SCALAR_NODES:
        return SCALAR_NODES[name](_handle_base_class(stub))

    if name in BASE_TYPE_CREATE:
        return BASE_TYPE_CREATE[name]()

    if name == "_OptionalQuantity":
        return _handle_optional_quantity(stub)

    return None


def _get_stubs():
    path = f"{inspect.getfile(stnode)}i"

    with open(path) as f:
        source = f.read()

    return parse.parse(source, path, stnode.__name__, None, options.Options())


def _get_schema(tag):
    schema_uri = asdf.AsdfFile().extension_manager.get_tag_definition(tag["tag_uri"]).schema_uris[0]

    return asdf.schema.load_schema(schema_uri, resolve_references=True)


def _get_name(tag):
    return stnode._class_name_from_tag_uri(tag["tag_uri"])


SCHEMAS = {_get_name(tag): _get_schema(tag) for tag in stnode._DATAMODELS_MANIFEST["tags"]}
STUBS = {c.name: c for c in _get_stubs().defs if isinstance(c, nodes.ClassDef)}

INTERMEDIATE_STUBS = {k: v for k, v in STUBS.items() if k not in SCHEMAS}
CLASSES = {c.__name__: c for c in stnode.NODE_CLASSES}


def _handle_type(stub):
    stub_ = stub.type
    if stub_.name in INTERMEDIATE_STUBS:
        return _handle_stub(INTERMEDIATE_STUBS[stub_.name])

    if stub_.name in STUBS:
        return CLASSES[stub_.name](_handle_stub(STUBS[stub_.name]))

    tree = _handle_base_type(stub_)
    if tree is None:
        raise ValueError(f"Unhandled base class {stub_.name}")

    return tree


BASE_TYPES = [stnode.TaggedObjectNode, stnode.TaggedListNode, stnode.TaggedScalarNode, stnode.DNode, stnode.LNode]
BASE_CLASSES = {c.__name__: c for c in BASE_TYPES}


def _handle_base_class(stub):
    tree = {}
    for stub_ in stub.base_type_exprs:
        if stub_.name in BASE_CLASSES:
            continue
        if stub_.name in INTERMEDIATE_STUBS:
            tree.update(_handle_stub(INTERMEDIATE_STUBS[stub_.name]))
        else:
            return _handle_base_type(stub_)

    return tree


REPLACE_NAME = {
    "pass_": "pass",
}


def _handle_defs(stub):
    tree = _handle_base_type(stub)
    if tree is None:
        tree = {}
        for stub_ in stub.defs.body:
            name = stub_.lvalues[0].name
            name = REPLACE_NAME.get(name, name)
            tree[name] = _handle_stub(stub_)

        if hasattr(stub, "base_type_exprs"):
            tree.update(_handle_base_class(stub))

    if stub.name in CLASSES:
        tree = CLASSES[stub.name](tree)
    return tree


def _handle_stub(stub):
    if hasattr(stub, "defs"):
        return _handle_defs(stub)

    if hasattr(stub, "type"):
        return _handle_type(stub)

    raise ValueError(f"Unhandled stub {stub}")


def _tag_object(tree):
    ctx = asdf.AsdfFile()
    return asdf.yamlutil.custom_tree_to_tagged_tree(tree, ctx)


def test_check_names():
    schemas = set(SCHEMAS.keys())
    classes = set(CLASSES.keys())
    stubs = set(STUBS.keys())

    assert schemas == classes
    assert schemas.issubset(stubs), f"Missing stubs for {schemas - stubs}"


NUM_ITERATIONS = 1


@pytest.mark.parametrize("name", SCHEMAS.keys())
def test_stub(name):
    # Create the object from stub multiple times to make sure it works
    # this is because it is randomly generated and may follow different
    # creation paths each time
    for _ in range(NUM_ITERATIONS):
        tree = _tag_object(_handle_stub(STUBS[name]))

        asdf.schema.validate(tree, schema=SCHEMAS[name])
