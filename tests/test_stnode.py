import asdf
import yaml

from roman_datamodels import stnode


def test_generated_node_classes():
    manifest = yaml.safe_load(asdf.get_config().resource_manager["http://stsci.edu/asdf/datamodels/roman/manifests/datamodels-1.0"])

    for tag in manifest["tags"]:
        class_name = stnode._class_name_from_tag_uri(tag["tag_uri"])
        node_class = getattr(stnode, class_name)

        assert issubclass(node_class, stnode.TaggedObjectNode)
        assert node_class._tag == tag["tag_uri"]
        assert tag["description"] in node_class.__doc__
        assert tag["tag_uri"] in node_class.__doc__
        assert node_class.__module__ == stnode.__name__

