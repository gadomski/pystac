from __future__ import annotations

import copy
from typing import Any

from .asset import Asset
from .constants import ITEM_TYPE
from .extensions import Extension, Extensions, ProjectionExtension
from .link import Link
from .stac_object import STACObject


class Item(STACObject):
    """An Item is a GeoJSON Feature augmented with foreign members relevant to a
    STAC object.

    These include fields that identify the time range and assets of the Item.
    An Item is the core object in a STAC Catalog, containing the core metadata
    that enables any client to search or crawl online catalogs of spatial
    'assets' (e.g., satellite imagery, derived data, DEMs)."""

    @classmethod
    def get_type(cls: type[Item]) -> str:
        return ITEM_TYPE

    def __init__(
        self,
        id: str,
        geometry: dict[str, Any] | None = None,
        bbox: list[float | int] | None = None,
        properties: dict[str, Any] | None = None,
        assets: dict[str, Asset | dict[str, Any]] | None = None,
        collection: str | None = None,
        stac_version: str | None = None,
        stac_extensions: list[str] | None = None,
        links: list[Link | dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> None:
        self.geometry = geometry
        self.bbox = bbox
        self.properties = properties or dict()

        if assets is None:
            self.assets = dict()
        else:
            self.assets = dict(
                (key, asset if isinstance(asset, Asset) else Asset.from_dict(asset))
                for key, asset in assets.items()
            )

        self.collection = collection
        self.ext = ItemExtensions(self)

        super().__init__(id, stac_version, stac_extensions, links, **kwargs)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "type": self.get_type(),
            "stac_version": self.stac_version,
        }
        if self.stac_extensions is not None:
            d["stac_extensions"] = self.stac_extensions
        d["id"] = self.id
        d["geometry"] = self.geometry
        if self.bbox is not None:
            d["bbox"] = self.bbox
        d["properties"] = copy.deepcopy(self.properties)
        d["properties"].update(self.ext.to_dict())
        d["links"] = [link.to_dict() for link in self.iter_links()]
        d["assets"] = dict((key, asset.to_dict()) for key, asset in self.assets.items())
        d["collection"] = self.collection
        d.update(copy.deepcopy(self.extra_fields))
        return d


class ItemExtensions(Extensions):
    def get_supported_extensions(self) -> list[type[Extension]]:
        return [ProjectionExtension]
