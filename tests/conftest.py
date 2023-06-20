import asdf
import pytest
import yaml

from roman_datamodels import datamodels
from roman_datamodels import maker_utils as utils

MANIFEST = yaml.safe_load(asdf.get_config().resource_manager["asdf://stsci.edu/datamodels/roman/manifests/datamodels-1.0"])


@pytest.fixture(scope="session")
def manifest():
    return MANIFEST


@pytest.fixture(name="set_up_list_of_l2_files")
def set_up_list_of_l2_files(tmp_path, request):
    # generate a list of n filepaths and files to be read later on by ModelContainer
    marker = request.node.get_closest_marker("set_up_list_of_l2_files_data")
    number_of_files_to_create = marker.args[0]
    type_of_returned_object = marker.args[1]

    result_list = []
    for i in range(number_of_files_to_create):
        filepath = tmp_path / f"test_model_container_input_as_list_of_filepaths_{i:02}.asdf"
        # create L2 file using filepath
        utils.mk_level2_image(filepath=filepath)
        if type_of_returned_object == "asdf":
            # append filepath to filepath list
            result_list.append(str(filepath))
        elif type_of_returned_object == "datamodel":
            # parse ASDF file as RDM
            datamodel = datamodels.open(str(filepath))
            # append datamodel to datamodel list
            result_list.append(datamodel)

    return result_list


def pytest_configure(config):
    config.addinivalue_line("markers", "set_up_list_of_l2_files_data(number_of_files_to_create, type_of_returned_object): ")
