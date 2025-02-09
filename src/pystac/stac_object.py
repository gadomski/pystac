from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterator

from typing_extensions import Self

from .constants import (
    CATALOG_TYPE,
    COLLECTION_TYPE,
    DEFAULT_STAC_VERSION,
    ITEM_TYPE,
    PARENT_REL,
    ROOT_REL,
)
from .errors import PystacError, StacError
from .link import Link

if TYPE_CHECKING:
    from .io import Reader, Writer


class STACObject(ABC):
    """The base class for all STAC values."""

    @classmethod
    @abstractmethod
    def get_type(cls: type[Self]) -> str: ...

    @classmethod
    def from_file(cls: type[Self], href: str | Path) -> Self:
        from . import io

        stac_object = io.read_file(href)
        if isinstance(stac_object, cls):
            return stac_object
        else:
            raise PystacError(f"expected {cls}, read {type(stac_object)} from {href}")

    @classmethod
    def from_dict(cls: type[STACObject], d: dict[str, Any]) -> STACObject:
        if type_value := d.get("type"):
            if type_value == CATALOG_TYPE:
                from .catalog import Catalog

                return Catalog(**d)
            elif type_value == COLLECTION_TYPE:
                from .collection import Collection

                return Collection(**d)
            elif type_value == ITEM_TYPE:
                from .item import Item

                return Item(**d)
            else:
                raise NotImplementedError
        else:
            raise StacError("missing type field on dictionary")

    def __init__(
        self,
        id: str,
        stac_version: str | None = None,
        stac_extensions: list[str] | None = None,
        links: list[Link | dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> None:
        from .io import Reader, Writer

        self.id = id
        self.stac_version = stac_version or DEFAULT_STAC_VERSION
        self.stac_extensions = stac_extensions

        self._links: list[Link] = []
        if links is not None:
            for link in links:
                if not isinstance(link, Link):
                    link = Link.from_dict(link)
                link.set_owner(self)
                self._links.append(link)

        self.extra_fields = kwargs
        self._href: str | None = None
        self._reader = Reader()
        self._writer = Writer()

    def get_href(self) -> str | None:
        return self._href

    def set_href(self, href: str, set_self_link: bool = False) -> None:
        self._href = href
        if set_self_link:
            self.set_link(Link.self(self))

    def get_reader(self) -> Reader:
        return self._reader

    def set_reader(self, reader: Reader) -> None:
        self._reader = reader

    def read_file(self, href: str) -> STACObject:
        from . import io

        href = io.make_absolute_href(href, self._href)
        return self._reader.read_file(href)

    def get_writer(self) -> Writer:
        return self._writer

    def set_writer(self, writer: Writer) -> None:
        self._writer = writer

    def write_file(self, href: str | Path) -> None:
        """Writes this STAC object to a file"""
        self._writer.write_file(self, href)

    def get_link(self, rel: str) -> Link | None:
        return next((link for link in self._links if link.rel == rel), None)

    def iter_links(self) -> Iterator[Link]:
        for link in self._links:
            yield link

    def set_link(self, link: Link) -> None:
        links = [other for other in self._links if other.rel != link.rel]
        link.set_owner(self)
        links.append(link)
        self._links = links

    def add_link(self, link: Link) -> None:
        link.set_owner(self)
        self._links.append(link)

    def get_root_link(self) -> Link | None:
        return self.get_link(ROOT_REL)

    def get_parent_link(self) -> Link | None:
        return self.get_link(PARENT_REL)

    @abstractmethod
    def to_dict(self) -> dict[str, Any]: ...

    def __repr__(self) -> str:
        return f"<pystac.{self.__class__.__name__} id={self.id}>"
