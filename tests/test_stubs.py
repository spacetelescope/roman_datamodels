import inspect

import asdf
import astropy.units as u
import pytest
from astropy.modeling.models import Shift
from astropy.time import Time
from astropy.units import Quantity, Unit
from mypy import nodes, options, parse
from numpy import ndarray, random

from roman_datamodels import random_utils, stnode

RNG = random.default_rng(472)


# mdl = stnode.Guidewindow()
# mdl.meta.


def _get_tag_for_type(type_):
    extension_manager = asdf.AsdfFile().extension_manager
    if extension_manager.handles_type(type_):
        return extension_manager.get_converter_for_type(type_).tags
    else:
        raise ValueError(f"Unhandled type {type_}")


TYPES = {
    "integer": "int",
    "number": "float",
    "string": "str",
    "boolean": "bool",
}


EXTERNAL_TAGGED_TYPES = [Quantity, Unit, Time]


def _external_tagged_types():
    return {t.__name__: _get_tag_for_type(t) for t in EXTERNAL_TAGGED_TYPES}


TAGGED_TYPES = _external_tagged_types()
TAGGED_TYPES[ndarray.__name__] = "tag:stsci.edu:asdf/core/ndarray-1.0.0"


def _parse_stubs():
    path = f"{inspect.getfile(stnode)}i"
    module = stnode.__name__
    options_ = options.Options()

    with open(path) as f:
        source = f.read()

    return parse.parse(source, path, module, None, options_)


def _class_stubs():
    stubs = _parse_stubs()
    return [c for c in stubs.defs if isinstance(c, nodes.ClassDef)]


def _get_schema(tag):
    tag_uri = tag["tag_uri"]
    schema_uri = asdf.AsdfFile().extension_manager.get_tag_definition(tag_uri).schema_uris[0]

    return asdf.schema.load_schema(schema_uri, resolve_references=True)


def _schemas():
    schemas = {}
    tagged_types = {}
    for tag in stnode._DATAMODELS_MANIFEST["tags"]:
        name = stnode._class_name_from_tag_uri(tag["tag_uri"])
        schema = _get_schema(tag)
        schemas[name] = schema
        tagged_types[name] = tag["tag_uri"]

    return schemas, tagged_types


def _stubs():
    return {c.name: c for c in _class_stubs()}


def _classes():
    return {c.__name__: c for c in stnode.NODE_CLASSES}


BASE_TYPES = [stnode.TaggedObjectNode, stnode.TaggedListNode, stnode.TaggedScalarNode, stnode.DNode, stnode.LNode]


STUBS = _stubs()
SCHEMAS, EXTEND_TAGGED_TYPES = _schemas()
INTERMEDIATE_STUBS = {k: v for k, v in STUBS.items() if k not in SCHEMAS}
CLASSES = _classes()
BASE_CLASSES = {c.__name__: c for c in BASE_TYPES}

TAGGED_TYPES.update(EXTEND_TAGGED_TYPES)


def test_check_names():
    schemas = set(SCHEMAS.keys())
    classes = set(CLASSES.keys())
    stubs = set(STUBS.keys())

    assert schemas == classes
    assert schemas.issubset(stubs), f"Missing stubs for {schemas - stubs}"


def _get_stub(name, stubs):
    stub = stubs[name]
    try:
        type_name = stub.type.name
    except AttributeError:
        # print(stub.type.items)
        return stub.type.items

    return INTERMEDIATE_STUBS.get(type_name, None) or stub


def _get_type_name(stub):
    try:
        type_name = stub.type.name
    except AttributeError:
        type_name = None
        new_stubs = _get_body(stub)
    else:
        new_stubs = {}

    return type_name, new_stubs


def _check_stub(name, schema, stubs):
    stub = _get_stub(name, stubs)
    try:
        type_name = stub.type.name
    except AttributeError:
        new_stubs = _get_body(stub)
    else:
        new_stubs = {}

    tag = schema.get("tag", None)
    if tag:
        assert tag in TAGGED_TYPES[type_name], f"Missing tag for {type_name}"

    type_ = schema.get("type", None)
    if type_:
        if type_ == "array":
            assert type_name == "stnode.LNode"
        else:
            assert type_name == TYPES[type_], f"For attribute {name} incorrect stub for {type_}, got {type_name}"

    all_of = schema.get("allOf", None)
    if all_of:
        if new_stubs:
            for subschema in all_of:
                _check_object_stub(subschema, new_stubs)
        else:
            raise ValueError(f"Missing stub for {name}")


def _check_object_stub(schema, body):
    for name, subschema in schema.items():
        _check_stub(name, subschema, body)


def _check_type_stub(name, schema, body):
    stub = _get_stub(name, body)
    type_name, _ = _get_type_name(stub)
    if schema == "array":
        assert type_name == "stnode.LNode"
    else:
        assert type_name == TYPES[schema], f"For attribute {name} incorrect stub for {schema}, got {type_name}"


def _check_full_stub(schema, body):
    properties = schema.get("properties", None)
    if properties:
        _check_object_stub(properties, body)

    type_ = schema.get("type", None)
    if type_:
        _check_type_stub()


REPLACE_NAME = {
    "pass_": "pass",
}


def _get_body(stub):
    body = {}
    try:
        stub.defs
    except AttributeError:
        for item in stub:
            name = item.name
            name = REPLACE_NAME.get(name, name)
            body[name] = item
    else:
        for b in stub.defs.body:
            name = b.lvalues[0].name
            name = REPLACE_NAME.get(name, name)
            body[name] = b

    return body


# def _handle_lvalues(stub):
# tree = {}
# for stub_ in stub.lvalues:
#     name = stub_.name
#     name = REPLACE_NAME.get(name, name)
#     print(f"    {name=},{stub_}")
#     tree[name] = _handle_stub(stub_)


def _tag_string(node, tag):
    tagged = asdf.tagged.TaggedString(node)
    tagged._tag = tag

    return tag


TAG_OBJECTS = {
    dict: (lambda x, y: asdf.tagged.TaggedDict(x, y)),
    list: (lambda x, y: asdf.tagged.TaggedList(x, y)),
    str: (lambda x, y: _tag_string(x, y)),
}


def _tag_object(base):
    ctx = asdf.AsdfFile()
    return asdf.yamlutil.custom_tree_to_tagged_tree(base, ctx)
    # ctx = asdf.AsdfFile()
    # extension_manager = ctx.extension_manager

    # if extension_manager.handles_type(type(base)):
    #     err = False
    #     if isinstance(base, ndarray):
    #         err = True
    #     converter = extension_manager.get_converter_for_type(type(base))
    #     tag = converter.select_tag(base, ctx)
    #     node = converter.to_yaml_tree(base, tag, ctx)
    #     if err:
    #         raise ValueError(f"Unhandled type {type(node['value'])}, {type(base)}")

    #     return TAG_OBJECTS[type(node)](node, tag)
    # else:
    #     return base


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


def _single_choice(choice, seed=None):
    return choice


def _Model(seed=None):
    return Shift(random_utils.generate_float(seed=seed)) & Shift(random_utils.generate_float(seed=seed))


SEG_SHAPE = (2, 8, 16, 32, 32)
DATA_SHAPE = (2, 4096, 4096)
DQ_SHAPE = (4096, 4096)
BASE_TYPE_CREATE = {
    "Time": (lambda x: random_utils.generate_astropy_time(seed=x)),
    "float": (lambda x: random_utils.generate_float(seed=x)),
    "str": (lambda x: random_utils.generate_string(seed=x)),
    "int": (lambda x: random_utils.generate_int(seed=x)),
    "bool": (lambda x: random_utils.generate_bool(seed=x)),
    "CalLogs": (lambda x: _CalLogs(seed=x)),
    "_ndarray_uint8_3D": (lambda x: random_utils.generate_array_uint8(seed=x, size=DATA_SHAPE)),
    "_ndarray_uint16_2D": (lambda x: random_utils.generate_array_uint16(seed=x, size=DQ_SHAPE)),
    "_ndarray_uint16_3D": (lambda x: random_utils.generate_array_uint16(seed=x, size=DATA_SHAPE)),
    "_ndarray_uint32_2D": (lambda x: random_utils.generate_array_uint32(seed=x, size=DQ_SHAPE)),
    "_ndarray_uint32_3D": (lambda x: random_utils.generate_array_uint32(seed=x, size=DATA_SHAPE)),
    "_ndarray_float32_2D": (lambda x: random_utils.generate_array_float32(seed=x, size=DQ_SHAPE)),
    "_ndarray_float32_3D": (lambda x: random_utils.generate_array_float32(seed=x, size=DATA_SHAPE)),
    "_Quantity_uint16_DN_3D": (lambda x: random_utils.generate_array_uint16(seed=x, size=DATA_SHAPE, units=u.DN)),
    "_Quantity_uint16_DN_5D": (lambda x: random_utils.generate_array_uint16(seed=x, size=SEG_SHAPE, units=u.DN)),
    "_Quantity_float32_electron_2D": (lambda x: random_utils.generate_array_float32(seed=x, size=DQ_SHAPE, units=u.electron)),
    "_Quantity_float32_electron_3D": (lambda x: random_utils.generate_array_float32(seed=x, size=DATA_SHAPE, units=u.electron)),
    "_Quantity_float32_electron_DN_2D": (
        lambda x: random_utils.generate_array_float32(seed=x, size=DQ_SHAPE, units=u.electron / u.DN)
    ),
    "_Quantity_float32_DN_2D": (lambda x: random_utils.generate_array_float32(seed=x, size=DQ_SHAPE, units=u.DN)),
    "_Quantity_float32_DN_3D": (lambda x: random_utils.generate_array_float32(seed=x, size=DATA_SHAPE, units=u.DN)),
    "_Quantity_float32_electron_s_2D": (
        lambda x: random_utils.generate_array_float32(seed=x, size=DQ_SHAPE, units=u.electron / u.s)
    ),
    "_Quantity_float32_electron_s_3D": (
        lambda x: random_utils.generate_array_float32(seed=x, size=DATA_SHAPE, units=u.electron / u.s)
    ),
    "_Quantity_float32_electron2_s2_2D": (
        lambda x: random_utils.generate_array_float32(seed=x, size=DQ_SHAPE, units=u.electron**2 / u.s**2)
    ),
    "_Quantity_float32_electron2_s2_3D": (
        lambda x: random_utils.generate_array_float32(seed=x, size=DATA_SHAPE, units=u.electron**2 / u.s**2)
    ),
    "_ApertureName": (lambda x: _ApertureName(seed=x)),
    "_AssociationProduct": (lambda x: _AssociationProduct(seed=x)),
    "_CalStepVal": (lambda x: _CalStepVal(seed=x)),
    "_GwMode": (lambda x: _GwMode(seed=x)),
    "_EngineeringQuality": (lambda x: _EngineeringQuality(seed=x)),
    "_EphemerisType": (lambda x: _EphemerisType(seed=x)),
    "_ExposureType": (lambda x: _ExposureType(seed=x)),
    "_ObservationSurvey": (lambda x: _ObservationSurvey(seed=x)),
    "_Pedigree": (lambda x: _Pedigree(seed=x)),
    "_PointingEngdbQuality": (lambda x: _PointingEngdbQuality(seed=x)),
    "_ResampleWeightType": (lambda x: _ResampleWeightType(seed=x)),
    "_TargetSourceType": (lambda x: _TargetSourceType(seed=x)),
    "_TargetType": (lambda x: _TargetType(seed=x)),
    "_WfiDetector": (lambda x: _WfiDetector(seed=x)),
    "_WfiOpticalElement": (lambda x: _WfiOpticalElement(seed=x)),
    "_p_exptype": (lambda x: _p_exptype(seed=x)),
    "_WfiModeName": (lambda x: _single_choice("WFI", seed=x)),
    "_ReferenceFrame": (lambda x: _single_choice("ICRS", seed=x)),
    "_Telescope": (lambda x: _single_choice("ROMAN", seed=x)),
    "_DistortionInput": (lambda x: _single_choice(u.pixel, seed=x)),
    "_DistortionOutput": (lambda x: _single_choice(u.arcsec, seed=x)),
    "_DNunit": (lambda x: _single_choice(u.DN, seed=x)),
    "_Origin": (lambda x: _Origin(seed=x)),
    "_DarkRefType": (lambda x: _single_choice("DARK", seed=x)),
    "_DistortionRefType": (lambda x: _single_choice("DISTORTION", seed=x)),
    "_FlatRefType": (lambda x: _single_choice("FLAT", seed=x)),
    "_GainRefType": (lambda x: _single_choice("GAIN", seed=x)),
    "_InverseLinearityRefType": (lambda x: _single_choice("INVERSE_LINEARITY", seed=x)),
    "_IpcRefType": (lambda x: _single_choice("IPC", seed=x)),
    "_LinearityRefType": (lambda x: _single_choice("LINEARITY", seed=x)),
    "_MaskRefType": (lambda x: _single_choice("MASK", seed=x)),
    "_PixelareaRefType": (lambda x: _single_choice("AREA", seed=x)),
    "_ReadnoiseRefType": (lambda x: _single_choice("READNOISE", seed=x)),
    "_SaturationRefType": (lambda x: _single_choice("SATURATION", seed=x)),
    "_SuperbiasRefType": (lambda x: _single_choice("BIAS", seed=x)),
    "_WfiImgPhotomRefType": (lambda x: _single_choice("PHOTOM", seed=x)),
    "Model": (lambda x: _Model(seed=x)),
}

SCALAR_NODES = {c.__name__: c for c in stnode._SCALAR_NODE_CLASSES_BY_TAG.values()}

# def _handle_lnode_args(stub):
# tree = []
# for arg in stub.args:
#     tree_ = _handle_base_type(arg)
#     if tree_ is None:
#         raise ValueError(f"Unhandled base class {arg.name}")
#     tree.append(tree_())

# return tree


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
    q = Quantity(random_utils.generate_float(seed), GET_UNIT[stub.args[0].name])
    if random_utils.generate_bool(seed):
        return q


def _handle_base_type(stub):
    print(f"{stub.name}, Call Handle base type")
    name = stub.name
    if name == "stnode.LNode":
        print(f"{stub.name}, is lnode")
        return _handle_lnode(stub)

    if name in SCALAR_NODES:
        print(f"{stub.name}, is scalar node")
        cls = SCALAR_NODES[name]
        return cls(_handle_base_class(stub))

    if name in BASE_TYPE_CREATE:
        print(f"{stub.name}, is base node")
        return BASE_TYPE_CREATE[name](42)

    if name == "_OptionalQuantity":
        return _handle_optional_quantity(stub, 42)

    print("OH NO!")

    return None


def _handle_type(stub):
    stub_ = stub.type
    if stub_.name in INTERMEDIATE_STUBS:
        if stub_.name == "_Quantity_float32_electrion_3D":
            print("HERE1")
            print(hasattr(INTERMEDIATE_STUBS[stub_.name], "name"))
        return _handle_stub(INTERMEDIATE_STUBS[stub_.name])

    if stub_.name in STUBS:
        if stub_.name == "_Quantity_float32_electrion_3D":
            print("HERE2")
        cls = CLASSES[stub_.name]
        return cls(_handle_stub(STUBS[stub_.name]))

    tree = _handle_base_type(stub_)
    if tree is None:
        print(stub)
        raise ValueError(f"Unhandled base class {stub_.name}")

    return tree


def _handle_base_class(stub):
    tree = {}
    for stub_ in stub.base_type_exprs:
        if stub_.name in BASE_CLASSES:
            continue
        if stub_.name in INTERMEDIATE_STUBS:
            if stub_.name == "Aperture":
                raise ValueError("Aperture")
            tree.update(_handle_stub(INTERMEDIATE_STUBS[stub_.name]))
        else:
            return _handle_base_type(stub_)

    return tree


def _handle_defs(stub):
    if hasattr(stub, "name"):
        print(f"{stub.name}, Call Handle defs")
    tree = _handle_base_type(stub)
    if tree is None:
        if hasattr(stub, "name"):
            print(f"{stub.name}, NO BASE TYPE")
        tree = {}
        print(stub)
        for stub_ in stub.defs.body:
            name = stub_.lvalues[0].name
            name = REPLACE_NAME.get(name, name)
            print("\n")
            print(f"    {name=}, {stub_=}")
            if name == "data":
                print(stub_)
                assert hasattr(stub_, "type")
                assert hasattr(stub_.type, "name")
            tree[name] = _handle_stub(stub_)

        if hasattr(stub, "base_type_exprs"):
            tree.update(_handle_base_class(stub))

    # if hasattr(stub, "name"):
    #     print(f"{stub.name}, NO BASE TYPE")

    if stub.name in CLASSES:
        tree = CLASSES[stub.name](tree)
    return tree


def _handle_stub(stub):
    if hasattr(stub, "defs"):
        if hasattr(stub, "name"):
            print(f"{stub.name}, Handle defs")
        return _handle_defs(stub)

    if hasattr(stub, "type"):
        if hasattr(stub.type, "name"):
            print(f"{stub.type.name}, Handle type")
        return _handle_type(stub)

    raise ValueError(f"Unhandled stub {stub}")


@pytest.mark.parametrize("name", SCHEMAS.keys())
def test_stub(name):
    stub = STUBS[name]
    schema = SCHEMAS[name]

    tree = _handle_stub(stub)
    tree = _tag_object(tree)

    asdf.schema.validate(tree, schema=schema)


# @pytest.mark.parametrize("name", SCHEMAS.keys())
# def test_class(name):
#     schema = SCHEMAS[name]
#     stub = STUBS[name]
#     class_ = CLASSES[name]

#     if issubclass(class_, stnode.TaggedObjectNode):
#         properties = schema.get("properties", {})
#         body = _get_body(stub)

#         attributes = set(properties.keys())
#         names = set(body.keys())
#         assert attributes == names

#         _check_object_stub(schema, body)
#     elif issubclass(class_, stnode.TaggedListNode):
#         pass
#     elif issubclass(class_, stnode.TaggedScalarNode):
#         pass
#     else:
#         raise ValueError(f"Unknown class {name}")
