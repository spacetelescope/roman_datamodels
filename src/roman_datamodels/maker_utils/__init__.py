from ._basic_meta import *  # noqa: F403
from ._common_meta import *  # noqa: F403
from ._datamodels import *  # noqa: F403
from ._ref_files import *  # noqa: F403

# These makers have special names to reflect the nature of their use in the pipeline
SPECIAL_MAKERS = {
    "WfiScienceRaw": "mk_level1_science_raw",
    "WfiImage": "mk_level2_image",
    "WfiMosaic": "mk_level3_mosaic",
}


def mk_node(node_class, **kwargs):
    from roman_datamodels.testing.factories import _camel_case_to_snake_case

    if node_class.__name__ in SPECIAL_MAKERS:
        method_name = SPECIAL_MAKERS[node_class.__name__]
    else:
        method_name = "mk_" + _camel_case_to_snake_case(node_class.__name__)

        # Reference files are in their own module so the '_ref` monicker is left off
        if method_name.endswith("_ref"):
            method_name = method_name[:-4]

        if method_name not in globals():
            raise ValueError(f"Maker utility: {method_name} not implemented for class {node_class.__name__}")
    return globals()[method_name](**kwargs)
