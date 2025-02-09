from pystac import Item


def test_default_schema_url() -> None:
    item = Item("an-id")
    item.ext.add("proj")
    assert item.stac_extensions
    assert (
        "https://stac-extensions.github.io/projection/v2.0.0/schema.json"
        in item.stac_extensions
    )


def test_code() -> None:
    item = Item("an-id")
    item.ext.add("proj")
    item.ext.proj.code = "EPSG:4326"
    d = item.to_dict()
    assert d["properties"]["proj:code"] == "EPSG:4326"
