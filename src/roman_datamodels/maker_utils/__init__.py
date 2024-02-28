from roman_datamodels.datamodels import MODEL_REGISTRY as _MODEL_REGISTRY  # Hide from public API

from ._basic_meta import *  # noqa: F403
from ._common_meta import *  # noqa: F403
from ._datamodels import *  # noqa: F403
from ._ground import *  # noqa: F403
from ._ref_files import *  # noqa: F403
from ._tagged_nodes import *  # noqa: F403

# These makers have special names to reflect the nature of their use in the pipeline
SPECIAL_MAKERS = {
    "WfiScienceRaw": "mk_level1_science_raw",
    "WfiImage": "mk_level2_image",
    "WfiMosaic": "mk_level3_mosaic",
}

# This is static at runtime, so we might as well compute it once
NODE_REGISTRY = {mdl: node for node, mdl in _MODEL_REGISTRY.items()}


def _camel_case_to_snake_case(value):
    """
    Courtesy of https://stackoverflow.com/a/1176023
    """
    import re

    return re.sub(r"(?<!^)(?=[A-Z])", "_", value).lower()


def _get_node_maker(node_class):
    """
    Create a dummy node of the specified class with valid values
    for attributes required by the schema.

    Parameters
    ----------
    node_class : type
        Node class (from stnode).

    Returns
    -------
    maker function for node class
    """
    if node_class.__name__ in SPECIAL_MAKERS:
        method_name = SPECIAL_MAKERS[node_class.__name__]
    else:
        method_name = f"mk_{_camel_case_to_snake_case(node_class.__name__)}"

        # Reference files are in their own module so the '_ref` monicker is left off
        if method_name.endswith("_ref"):
            method_name = method_name[:-4]

        if method_name not in globals():
            raise ValueError(f"Maker utility: {method_name} not implemented for class {node_class.__name__}")

    return globals()[method_name]


def mk_node(node_class, **kwargs):
    """
    Create a dummy node of the specified class with valid values
    for attributes required by the schema.

    Parameters
    ----------
    node_class : type
        Node class (from stnode).
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    `roman_datamodels.stnode.TaggedObjectNode`
    """

    return _get_node_maker(node_class)(**kwargs)


def mk_datamodel(model_class, **kwargs):
    """
    Create a dummy datamodel of the specified class with valid values
    for all attributes required by the schema.

    Parameters
    ----------
    model_class : type
        One of the datamodel subclasses from datamodel
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    `roman_datamodels.datamodels.Datamodel`
    """
    return model_class(mk_node(NODE_REGISTRY[model_class], **kwargs))
