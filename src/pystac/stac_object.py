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
    SELF_REL,
)
from .errors import StacError
from .link import Link

if TYPE_CHECKING:
    from .io import Reader, Writer


class STACObject(ABC):
    """The base class for all STAC objects."""

    @classmethod
    @abstractmethod
    def get_type(cls: type[Self]) -> str:
        """Returns the `type` field for this STAC object.

        Examples:
            >>> print(Item.get_type())
            "Feature"
        """

    @classmethod
    def from_file(cls: type[Self], href: str | Path) -> Self:
        """Reads a STAC object from a JSON file.

        Use this class method to "downcast" a STAC object to a given type.

        Raises:
            StacError: Raised if the object's type does not match the calling class.

        Examples:
            >>> catalog = Catalog.from_file("catalog.json")
            >>> Item.from_file("catalog.json") # Will raise a `StacError`
        """
        from . import io

        stac_object = io.read_file(href)
        if isinstance(stac_object, cls):
            return stac_object
        else:
            raise StacError(f"expected {cls}, read {type(stac_object)} from {href}")

    @classmethod
    def from_dict(cls: type[STACObject], d: dict[str, Any]) -> STACObject:
        """Creates a STAC object from a dictionary.

        If you already know what type of STAC object your dictionary represents,
        use the initializer directly, e.g. `Catalog(**d)`.

        Args:
            d: A JSON dictionary

        Returns:
            A STAC object

        Raises:
            StacError: If the type field is not present or not a value we recognize.

        Examples:
            >>> # Use this when you don't know what type of object it is
            >>> stac_object = STACObject.from_dict(d)
            >>> # Use this when you know you have a catalog
            >>> catalog = Catalog(**d)
        """
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
                raise StacError(f"unknown type field: {type_value}")
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
        """Creates a new STAC object.

        Args:
            id: The STAC object's id
            stac_version: If not provided or `None`, will default to
                [DEFAULT_STAC_VERSION][pystac.DEFAULT_STAC_VERSION]
            stac_extensions: A list of extension schema urls
            links: A list of links
            **kwargs: Any extra fields on the object
        """
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
        """Returns this STAC object's href.

        This is assigned when an object is read from a file. Objects created
        directly do not have an href.
        """
        if self._href:
            return self._href
        elif link := self.get_link(SELF_REL):
            return link.href
        else:
            return None

    def set_href(self, href: str | None, set_self_link: bool = False) -> None:
        """Sets this STAC object's href.

        Args:
            href: The href
            set_self_link: If true, the `self` link will be set to this href.
                It's more common to set `self` links via
                [Container.render][pystac.Container.render].
        """
        self._href = href
        if set_self_link:
            if href:
                self.set_link(Link.self(self))
            else:
                self.remove_links(SELF_REL)

    def get_reader(self) -> Reader:
        """Returns this STAC object's reader."""
        return self._reader

    def set_reader(self, reader: Reader) -> None:
        """Sets this STAC object's reader.

        This reader will be shared with any objects that are read "from" this
        object, e.g. via resolving links.
        """
        self._reader = reader

    def read_file(self, href: str) -> STACObject:
        """Reads a new STAC object from a file.

        This method will resolve relative hrefs by using this STAC object's href
        or, if not set, its `self` link.
        """
        from . import io

        href = io.make_absolute_href(href, self.get_href())
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
        self.remove_links(link.rel)
        link.set_owner(self)
        self._links.append(link)

    def remove_links(self, rel: str) -> None:
        self._links = [link for link in self._links if link.rel != rel]

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
