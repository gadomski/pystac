import copy
from typing import Any

from .asset import Asset, ItemAsset
from .constants import COLLECTION_TYPE, DEFAULT_LICENSE
from .container import Container
from .extent import Extent
from .link import Link
from .provider import Provider


class Collection(Container):
    @classmethod
    def get_type(cls) -> str:
        return COLLECTION_TYPE

    def __init__(
        self,
        id: str,
        description: str,
        title: str | None = None,
        keywords: list[str] | None = None,
        license: str = DEFAULT_LICENSE,
        providers: list[Provider | dict[str, Any]] | None = None,
        extent: Extent | dict[str, Any] | None = None,
        summaries: dict[str, Any] | None = None,
        assets: dict[str, Asset | dict[str, Any]] | None = None,
        item_assets: dict[str, ItemAsset | dict[str, Any]] | None = None,
        stac_version: str | None = None,
        stac_extensions: list[str] | None = None,
        links: list[Link | dict[str, Any]] | None = None,
        **kwargs: Any,
    ):
        self.description = description
        self.title = title
        self.keywords = keywords
        self.license = license
        self.summaries = summaries

        if providers is None:
            self.providers = None
        else:
            self.providers = [
                provider
                if isinstance(provider, Provider)
                else Provider.from_dict(provider)
                for provider in providers
            ]

        if extent is None:
            self.extent = Extent()
        elif isinstance(extent, Extent):
            self.extent = extent
        else:
            self.extent = Extent.from_dict(extent)

        if assets is None:
            self.assets = None
        else:
            self.assets = dict(
                (key, asset if isinstance(asset, Asset) else Asset.from_dict(asset))
                for key, asset in assets.items()
            )

        if item_assets is None:
            self.item_assets = None
        else:
            self.item_assets = dict(
                (
                    key,
                    item_asset
                    if isinstance(item_asset, ItemAsset)
                    else ItemAsset.from_dict(item_asset),
                )
                for key, item_asset in item_assets.items()
            )

        super().__init__(id, stac_version, stac_extensions, links, **kwargs)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "type": self.get_type(),
            "stac_version": self.stac_version,
        }
        if self.stac_extensions is not None:
            d["stac_extensions"] = self.stac_extensions
        d["id"] = self.id
        if self.title is not None:
            d["title"] = self.title
        d["description"] = self.description
        if self.keywords is not None:
            d["keywords"] = self.keywords
        d["license"] = self.license
        if self.providers is not None:
            d["providers"] = [provider.to_dict() for provider in self.providers]
        d["extent"] = self.extent.to_dict()
        if self.summaries is not None:
            d["summaries"] = self.summaries
        d["links"] = [link.to_dict() for link in self.iter_links()]
        if self.assets is not None:
            d["assets"] = dict(
                (key, asset.to_dict()) for key, asset in self.assets.items()
            )
        if self.item_assets is not None:
            d["item_assets"] = dict(
                (key, item_asset.to_dict())
                for key, item_asset in self.item_assets.items()
            )
        d.update(copy.deepcopy(self.extra_fields))
        return d
