from abc import ABC, abstractmethod

from .catalog import Catalog
from .collection import Collection
from .container import Container
from .item import Item
from .link import Link
from .stac_object import STACObject


class Renderer(ABC):
    def __init__(self, root: str):
        self.root = root

    def render(self, stac_object: STACObject) -> None:
        from .catalog import Catalog
        from .collection import Collection
        from .item import Item

        if (parent_link := stac_object.get_parent_link()) and parent_link.href:
            # TODO is this true for every renderer?
            base = parent_link.href.rsplit("/", 1)[0] + "/" + stac_object.id
        else:
            base = self.root

        if isinstance(stac_object, Item):
            href = self.get_item_href(stac_object, base)
        elif isinstance(stac_object, Catalog):
            href = self.get_catalog_href(stac_object, base)
        elif isinstance(stac_object, Collection):
            href = self.get_collection_href(stac_object, base)
        else:
            raise Exception("unreachable")
        stac_object.set_href(href, set_self_link=True)

        root_link = stac_object.get_root_link()
        if isinstance(stac_object, Container):
            if root_link is None:
                root_link = Link.root(stac_object)
            for leaf in stac_object.get_children_and_items():
                leaf.set_link(root_link)
                leaf.set_link(Link.parent(stac_object))
                self.render(leaf)

    @abstractmethod
    def get_item_href(self, item: Item, base: str) -> str: ...

    @abstractmethod
    def get_collection_href(self, collection: Collection, base: str) -> str: ...

    @abstractmethod
    def get_catalog_href(self, catalog: Catalog, base: str) -> str: ...


class DefaultRenderer(Renderer):
    def get_item_href(self, item: Item, base: str) -> str:
        return base + "/" + item.id + ".json"

    def get_catalog_href(self, catalog: Catalog, base: str) -> str:
        return base + "/catalog.json"

    def get_collection_href(self, collection: Collection, base: str) -> str:
        return base + "/collection.json"
