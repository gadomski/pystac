import pytest
from pytest import FixtureRequest

from pystac import Item


@pytest.fixture(params=["1.0.0", "1.1.0"])
def version(request: FixtureRequest) -> str:
    return request.param


def test_validate_item(version: str) -> None:
    item = Item("an-id")
    item.stac_version = version
    item.validate()
