import json
from pathlib import Path

import pystac
from pystac import Item


def test_init_by_id() -> None:
    _ = Item("an-id")


def test_to_dict_feature() -> None:
    d = Item("an-id").to_dict()
    assert d["type"] == "Feature"


def test_read_file(examples_path: Path) -> None:
    with open(examples_path / "simple-item.json") as f:
        d = json.load(f)
    item = pystac.read_file(examples_path / "simple-item.json")
    assert item.to_dict() == d
