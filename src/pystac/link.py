from __future__ import annotations

from typing import TYPE_CHECKING, Any

from typing_extensions import Self

from .constants import CHILD_REL, ITEM_REL, PARENT_REL, ROOT_REL, SELF_REL
from .errors import PystacError

if TYPE_CHECKING:
    from .item import Item
    from .stac_object import STACObject


class Link:
    @classmethod
    def from_dict(cls: type[Self], d: dict[str, Any]) -> Self:
        return cls(**d)

    @classmethod
    def root(cls: type[Self], root: STACObject) -> Self:
        link = cls(href=root.get_href(), rel=ROOT_REL)
        link._stac_object = root
        return link

    @classmethod
    def parent(cls: type[Self], parent: STACObject) -> Self:
        link = cls(href=parent.get_href(), rel=PARENT_REL)
        link._stac_object = parent
        return link

    @classmethod
    def child(cls: type[Self], child: STACObject) -> Self:
        link = cls(href=child.get_href(), rel=CHILD_REL)
        link._stac_object = child
        return link

    @classmethod
    def item(cls: type[Self], item: Item) -> Self:
        link = cls(href=item.get_href(), rel=ITEM_REL)
        link._stac_object = item
        return link

    @classmethod
    def self(cls: type[Self], stac_object: STACObject) -> Self:
        link = cls(href=stac_object.get_href(), rel=SELF_REL)
        link._stac_object = stac_object
        return link

    def __init__(
        self,
        href: str | None,
        rel: str,
        type: str | None = None,
        title: str | None = None,
        method: str | None = None,
        headers: dict[str, str | list[str]] | None = None,
        body: Any | None = None,
    ) -> None:
        self.href = href
        self.rel = rel
        self.type = type
        self.title = title
        self.method = method
        self.headers = headers
        self.body = body
        self._owner: STACObject | None = None
        self._stac_object: STACObject | None = None
        # TODO extra fields

    def set_owner(self, owner: STACObject) -> None:
        self._owner = owner

    def is_root(self) -> bool:
        return self.rel == ROOT_REL

    def is_parent(self) -> bool:
        return self.rel == PARENT_REL

    def is_child(self) -> bool:
        return self.rel == CHILD_REL

    def is_item(self) -> bool:
        return self.rel == ITEM_REL

    def is_self(self) -> bool:
        return self.rel == SELF_REL

    def get_stac_object(self) -> STACObject:
        if self._stac_object is None:
            if self.href is None:
                raise PystacError("cannot get a STAC object for a link with no href")
            elif self._owner:
                self._stac_object = self._owner.read_file(self.href)
            else:
                from . import io

                self._stac_object = io.read_file(self.href)
        return self._stac_object

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "href": self.href,
            "rel": self.rel,
        }
        if self.type is not None:
            d["type"] = self.type
        if self.title is not None:
            d["title"] = self.title
        if self.method is not None:
            d["method"] = self.method
        if self.headers is not None:
            d["headers"] = self.headers
        if self.body is not None:
            d["body"] = self.body
        return d

    def __repr__(self) -> str:
        return f"<pystac.Link href={self.href} rel={self.rel} to={self._stac_object}>"
