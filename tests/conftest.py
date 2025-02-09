from pathlib import Path
from typing import cast

import pytest
from pytest import FixtureRequest

from pystac import Catalog


@pytest.fixture(params=["1.0.0", "1.1.0"])
def examples_path(request: FixtureRequest) -> Path:
    return Path(__file__).parent / "examples" / ("v" + cast(str, request.param))


@pytest.fixture
def catalog(examples_path: Path) -> Catalog:
    return Catalog.from_file(examples_path / "catalog.json")
