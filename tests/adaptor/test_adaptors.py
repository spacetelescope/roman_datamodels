import pytest

from roman_datamodels.core import adaptors


@pytest.mark.parametrize("adaptor", adaptors.ADAPTORS.values())
def test_adaptor_realized(adaptor):
    assert issubclass(adaptor, adaptors.Adaptor)

    # Create instance to check all abstracts has been implemented
    adaptor()
