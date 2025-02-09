from abc import ABC, abstractmethod
from typing import Any, Literal, cast

from ..errors import StacError
from ..stac_object import STACObject
from .extension import Extension
from .projection import ProjectionExtension

Name = Literal["proj"]


class UnsupportedExtension(StacError):
    pass


class Extensions(ABC):
    def __init__(self, stac_object: STACObject) -> None:
        self._stac_object = stac_object
        self._extensions: dict[Name, Extension] = dict()

    def add(self, name: Name) -> None:
        match name:
            case "proj":
                self._add(ProjectionExtension)

    @abstractmethod
    def get_supported_extensions(self) -> list[type[Extension]]: ...

    @property
    def proj(self) -> ProjectionExtension:
        if "proj" not in self._extensions:
            self._extensions["proj"] = ProjectionExtension()
        return cast(ProjectionExtension, self._extensions["proj"])

    def to_dict(self) -> dict[str, Any]:
        # TODO should we implicitly update the extension urls?
        d = {}
        for extension in self._extensions.values():
            d.update(extension.to_dict())
        return d

    def _add(self, extension: type[Extension]) -> None:
        if extension in self.get_supported_extensions():
            self._set_extension_url(extension)
        else:
            raise UnsupportedExtension(
                f"{self._stac_object} does not support {extension}"
            )

    def _set_extension_url(self, extension: type[Extension]) -> None:
        if self._stac_object.stac_extensions:
            stac_extensions = [
                s
                for s in self._stac_object.stac_extensions
                if not extension.is_extension_url(s)
            ]
        else:
            stac_extensions = []
        stac_extensions.append(extension.get_extension_url())
        self._stac_object.stac_extensions = stac_extensions


__all__ = ["Extension", "ProjectionExtension", "Extensions"]
