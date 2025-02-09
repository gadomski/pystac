import pytest

from pystac import Catalog, Collection, DefaultRenderer, Item, Renderer, STACObject


@pytest.fixture
def renderer() -> Renderer:
    return DefaultRenderer("/pystac")


def assert_link(stac_object: STACObject, rel: str, href: str) -> None:
    link = stac_object.get_link(rel)
    assert link
    assert link.href == href


def test_solo_item_render(renderer: Renderer) -> None:
    item = Item("an-id")
    renderer.render(item)
    assert_link(item, "self", "/pystac/an-id.json")


def test_solo_catalog_render(renderer: Renderer) -> None:
    catalog = Catalog("an-id", "a description")
    renderer.render(catalog)
    assert_link(catalog, "self", "/pystac/catalog.json")


def test_solo_collection_render(renderer: Renderer) -> None:
    collection = Collection("an-id", "a description")
    renderer.render(collection)
    assert_link(collection, "self", "/pystac/collection.json")


def test_child_catalog_render(renderer: Renderer) -> None:
    catalog = Catalog("parent", "parent catalog")
    child = Catalog("child", "child catalog")
    catalog.add_child(child)
    renderer.render(catalog)
    assert catalog.get_href() == "/pystac/catalog.json"
    assert child.get_href() == "/pystac/child/catalog.json"
